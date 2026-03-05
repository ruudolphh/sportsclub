# Dependency Management with pip-tools

## 1. Analysis of Original requirements.txt

### Security Issues Identified

**1.1 Missing Version Pinning**
```
# BEFORE (Unsafe)
django-cors-headers
django-environ
django-ninja
```

**Problem**: No version constraints allow any version to be installed, including:
- Future major versions with breaking changes
- Versions with unpatched vulnerabilities
- Completely incompatible releases

**Risk**: In production, a dependency update could silently introduce breaking changes, causing runtime failures or security vulnerabilities.

**1.2 Missing Hash Verification**
```
# NO hash validation in original file
```

**Problem**: `pip` can install packages from untrusted sources without cryptographic verification.

**Risk**: 
- Supply chain attacks (compromised packages)
- Man-in-the-middle attacks
- Installation of malicious or tampered packages

**1.3 Non-Reproducible Builds**
```
# Original: Different installs produce different results
pip install -r requirements.txt  # Install A: Gets Django 5.0.1, Psycopg 3.2.0
pip install -r requirements.txt  # Install B: Gets Django 5.1.0, Psycopg 3.3.1
# Both valid, but builds are NOT identical
```

**Problem**: Without pinned versions, the same `requirements.txt` produces different environments:
- Makes debugging harder
- Breaks deterministic deployments
- Violates CI/CD reproducibility requirements

**1.4 Transitive Dependency Uncertainty**
```
# Original: No visibility into sub-dependencies
django-ninja                     # What version?
                                # What does it require?
                                # No explicit record
```

**Problem**: Transitive dependencies (dependencies of your dependencies) are not explicitly listed or versioned.

**Risk**: 
- Hidden breaking changes
- Outdated sub-dependencies
- Difficult to audit security issues

---

## 2. pip-tools Solution

### 2.1 Architecture

**Two-File System**:
```
requirements.in      ← INPUT: Direct dependencies (human-maintained)
requirements.txt     ← LOCK: All dependencies with hashes (auto-generated)
```

### 2.2 Workflow

#### Step 1: Define Direct Dependencies (requirements.in)
```ini
# requirements.in - ONLY direct, project dependencies
django>=5.0
django-cors-headers>=4.0
django-ninja>=1.0
psycopg[binary,pool]>=3.0
```

**Principles**:
- List ONLY packages your code imports
- Use version ranges (>=x.y, >=x.y,<z.0)
- Keep it human-readable
- Version in Git repository

#### Step 2: Compile to Lock File
```bash
# Generate requirements.txt with all transitive dependencies + hashes
pip-compile requirements.in --generate-hashes --resolver=backtracking

# Output: requirements.txt with 349+ lines of pinned versions and hashes
```

#### Step 3: Install from Lock File
```bash
# Deterministic, reproducible, verified installation
pip install -r requirements.txt

# Every install is identical (same versions, same hashes)
# All packages cryptographically verified
```

### 2.3 Input vs Lock Files

| Aspect | requirements.in | requirements.txt |
|--------|-----------------|------------------|
| **Type** | Input file | Lock file |
| **Who edits** | Developers (manually) | pip-compile (auto) |
| **Content** | Direct dependencies | All dependencies (direct + transitive) |
| **Versions** | Flexible ranges (>=5.0) | Fixed versions (==6.0.2) |
| **Hashes** | None | SHA256 hashes for each version |
| **Readability** | High (20-30 lines) | Low (300+ lines, auto-generated) |
| **Git tracking** | YES ✓ | YES ✓ |
| **Purpose** | Specify requirements | Ensure reproducibility |

**Example**: django-ninja (from requirements.in)
```
# In requirements.in: ONE line
django-ninja>=1.0

# In requirements.txt: EXPANDED to all dependencies
django-ninja==1.5.3 \
    --hash=sha256:0a6ead5b4e57ec1050b584eb6f36f105f256b8f4ac70d12e774d8b6dd91e2198 \
    --hash=sha256:974803944965ad0566071633ffd4999a956f2ad1ecbed815c0de37c1c969592b
    # via -r requirements.in

asgiref==3.11.1 \
    --hash=...
    # via
    #   django
    #   django-ninja      ← Installed because django-ninja needs it
```

---

## 3. Why This Matters in CI/CD and Production

### 3.1 Deterministic Builds
```bash
# Developer's machine
pip install -r requirements.txt  →  Environment A (Django 6.0.2, Psycopg 3.3.2)

# CI pipeline
pip install -r requirements.txt  →  Environment B (Django 6.0.2, Psycopg 3.3.2) ✓ IDENTICAL

# Production server
pip install -r requirements.txt  →  Environment C (Django 6.0.2, Psycopg 3.3.2) ✓ IDENTICAL

# All environments are byte-identical
```

### 3.2 Security Verification
```bash
# Without hashes (UNSAFE)
pip install -r requirements.txt
# No verification - package could be compromised

# With hashes (SECURE)
pip install -r requirements.txt
# Each package checked against cryptographic hash
# If hash doesn't match: INSTALL FAILS
# Detects:
#   - Compromised packages
#   - Man-in-the-middle attacks
#   - Tampered downloads
```

### 3.3 Reproducible Deployments
```
Monday:   Deploy v1.0  → Environment = Django 6.0.2
Wednesday: Deploy v1.0 → Environment = Django 6.0.2 (NOT 6.0.3 or 6.1.0)
Saturday: Deploy v1.0 → Environment = Django 6.0.2 (Even if newer versions exist)
```

---

## 4. Production Maintenance Procedure

### 4.1 Adding New Dependencies

```bash
# 1. Add to requirements.in
echo "celery>=5.0" >> requirements.in

# 2. Regenerate lock file
pip-compile requirements.in --generate-hashes

# 3. Review changes
git diff requirements.txt

# 4. Test in CI
git commit -am "Add celery dependency"
# ... CI tests run ...

# 5. Deploy to staging
# ... manual testing ...

# 6. Deploy to production
# pip install -r requirements.txt (deterministic, verified)
```

### 4.2 Updating Existing Dependencies

#### Minor/Patch Updates (Safe)
```bash
# Update in requirements.in - patch/minor versions only
# Before: django>=5.0,<6.0
# After:  django>=5.1,<6.0    ← Still prevents major version jumps

pip-compile requirements.in --generate-hashes
git diff requirements.txt    # Review what changed
pytest                        # Run full test suite
git commit -am "Update Django to 5.x patch"
```

#### Major Updates (Careful)
```bash
# Update one package at a time
pip-compile requirements.in --generate-hashes

# Run ALL tests
pytest -v

# Test in staging environment
# Verify no breaking changes
# Manual testing in CI environment

# Only after passing all tests:
git commit -am "Update Django to 6.0"
```

### 4.3 Using pip-compile --upgrade

```bash
# See what versions are available without changing anything
pip-compile requirements.in --dry-run --upgrade

# Upgrade to latest compatible versions (within constraints)
pip-compile requirements.in --generate-hashes --upgrade

# Upgrade specific package only
pip-compile requirements.in --generate-hashes --upgrade-package celery
```

### 4.4 Handling Vulnerable Packages

**Scenario**: CVE published for psycopg 3.2.0

```bash
# 1. Identify vulnerability
# Affected: psycopg==3.2.0
# Fixed in: psycopg>=3.2.1

# 2. Update constraint in requirements.in
# Before: psycopg[binary,pool]>=3.0
# After:  psycopg[binary,pool]>=3.2.1    ← Enforce minimum version

# 3. Regenerate and test
pip-compile requirements.in --generate-hashes
pytest                       # Verify compatibility
docker-compose up            # Test in containers

# 4. Deploy immediately (security hotfix)
git commit -am "Security: Update psycopg to fix CVE-2024-XXXXX"
```

### 4.5 Dependency Review Process

**Before merging to main**:

```
1. Automated checks (GitHub Actions)
   ✓ pip-compile --dry-run succeeds
   ✓ All tests pass
   ✓ Security scan passes
   ✓ No new vulnerabilities detected

2. Manual code review
   ✓ requirements.in changes are justified
   ✓ Version constraints are reasonable
   ✓ No unnecessary dependency additions

3. Staging testing (if major version bump)
   ✓ Test in container
   ✓ Test database migrations
   ✓ Test API endpoints
   ✓ Manual smoke tests

4. Merge and deploy to production
```

### 4.6 Regular Dependency Audits

```bash
# Weekly: Check for vulnerability updates
pip-compile requirements.in --upgrade --dry-run
# Review what would be updated

# Monthly: Update all dependencies conservatively
pip-compile requirements.in --upgrade --generate-hashes
# Test thoroughly
# Deploy if tests pass

# Quarterly: Major version review
# Evaluate updating to new major versions
# Plan migration path
```

---

## 5. Prevented Risk Scenarios

### 5.1 Supply Chain Attacks
```
WITHOUT hashes:
  Attacker compromises PyPI mirror
  → Injects malicious psycopg 3.3.2
  → Your CI silently installs compromised version
  → Database credentials leaked
  → UNDETECTED ❌

WITH hashes:
  Attacker compromises PyPI mirror
  → Injects malicious psycopg 3.3.2 (different file)
  → Hash doesn't match requirements.txt
  → Installation FAILS
  → DETECTED ✓ and blocked
```

### 5.2 Non-Reproducible Builds
```
WITHOUT pinning:
  Monday CI build:    Django 5.0.0 (latest yesterday)
  Friday CI build:    Django 5.1.0 (released Wednesday)
  Same code, different Django version
  → Different behavior, different bugs, non-reproducible
  
WITH pinning:
  Monday CI build:    Django 5.0.0
  Friday CI build:    Django 5.0.0 (exact version)
  Always identical
```

### 5.3 Unexpected Breaking Changes
```
WITHOUT pinning:
  requires: django-cors-headers
  Install A: Installs django-cors-headers 4.0.0
  Install B: Installs django-cors-headers 5.0.0 (BREAKING API CHANGES)
  Same requirements.txt, different behavior ❌

WITH pinning:
  requires: django-cors-headers==4.9.0
  Install A: Installs django-cors-headers 4.9.0
  Install B: Installs django-cors-headers 4.9.0 (ALWAYS SAME)
  Predictable, tested behavior ✓
```

### 5.4 Transitive Dependency Chaos
```
WITHOUT tracking transitive deps:
  Your requirements.in: django-ninja>=1.0
  
  When installed, django-ninja needs asgiref
  But requirements.txt doesn't explicitly list asgiref!
  
  Six months later:
  - asgiref 3.0 released with breaking changes
  - pip-compile picks it up automatically
  - Your app breaks
  - No record of the change
  - Difficult to debug

WITH pip-tools lock file:
  requirements.txt lists ALL dependencies:
  - django-ninja==1.5.3
  - asgiref==3.11.1 (via django-ninja)
  
  All versions documented
  All upgrades explicit and reviewed
  Full change history in Git
```

### 5.5 Installation of Malicious Packages
```
WITHOUT verification:
  Attacker registers fake package: "djngo-ninja"  ← typo
  OR compromises package metadata
  pip install -r requirements.txt
  
  No hash validation:
  → Might install wrong/malicious package
  → No cryptographic proof of integrity
  
WITH hashes:
  Package hash doesn't match
  → Installation FAILS
  → Error message: "hash mismatch"
  → Administrator investigates
  → Threat neutralized
```

---

## 6. Commands Reference

```bash
# Create lock file from input file
pip-compile requirements.in --generate-hashes

# Install from lock file (recommended for production)
pip install -r requirements.txt

# Check what would change without applying
pip-compile requirements.in --dry-run --upgrade

# Upgrade specific package
pip-compile requirements.in --upgrade-package django --generate-hashes

# Sync environment to exactly match lock file
pip-sync requirements.txt

# Update a single dependency in place
pip-compile requirements.in --upgrade-package celery --generate-hashes
```

---

## 7. Summary

| Feature | Benefit | Implementation |
|---------|---------|-----------------|
| **Version Pinning** | Reproducible builds | `django==6.0.2` in requirements.txt |
| **Hash Verification** | Supply chain security | `--hash=sha256:...` for each package |
| **Two-File System** | Clear separation | requirements.in (input) + requirements.txt (lock) |
| **Transitive Tracking** | Full visibility | All dependencies listed in lock file |
| **Determinism** | CI/CD reliability | Identical installs across environments |
| **Auditability** | Security compliance | Full dependency history in Git |

This setup ensures that every dependency is:
- ✓ Explicitly versioned
- ✓ Cryptographically verified
- ✓ Reproducible across environments
- ✓ Auditable in source control
- ✓ Updated intentionally and tested before deployment
