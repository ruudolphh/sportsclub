# Quick Reference: Secure Dependency Management

## 🔥 Common Commands

### Installation
```bash
# Secure installation (production)
pip install -r requirements.txt --require-hashes --allow-unsafe

# Development installation
pip install -r requirements.txt

# Sync environment to exact lock file
pip-sync requirements.txt
```

### Dependency Management
```bash
# Add new package
echo "celery>=5.0" >> requirements.in
pip-compile requirements.in --generate-hashes
pip install -r requirements.txt --require-hashes --allow-unsafe
pytest                          # Test

# Update single package
pip-compile --upgrade-package django --generate-hashes

# Update all packages (use cautiously)
pip-compile --upgrade --generate-hashes

# Check what would change
pip-compile --dry-run --upgrade
```

### Security
```bash
# Verify hashes
pip install -r requirements.txt --require-hashes --allow-unsafe

# Scan for CVEs
pip install pip-audit
pip-audit -r requirements.txt --desc

# Check for conflicts
pip-check
```

---

## 📁 File Reference

| File | Purpose | Edit? |
|------|---------|-------|
| requirements.in | Direct dependencies | ✅ YES |
| requirements.txt | Lock file with hashes | ❌ NO (auto-generated) |
| .github/dependabot.yml | Dependency bot config | ✅ YES (if needed) |
| .github/workflows/ci.yml | CI tests | ✅ YES (normal) |

---

## 🔐 Security Checklist

Before merging dependency changes:

```
□ Edited requirements.in (NOT requirements.txt)
□ Ran: pip-compile requirements.in --generate-hashes
□ Tested locally: pip install -r requirements.txt --require-hashes --allow-unsafe
□ Ran all tests: pytest -v
□ No vulnerabilities: pip-audit -r requirements.txt
□ Hash verification works
□ CI pipeline passes
□ No new CVEs introduced
□ Version constraints are reasonable
```

---

## 🚨 Emergency Procedures

### Critical Vulnerability in Dependency

```bash
# STEP 1: Identify affected package
# Example: psycopg has CVE

# STEP 2: Update requirements.in with fixed version
# Change: psycopg[binary,pool]>=3.0
# To:     psycopg[binary,pool]>=3.2.1  (patch version)

# STEP 3: Generate new lock
pip-compile requirements.in --generate-hashes

# STEP 4: Test immediately
pip install -r requirements.txt --require-hashes --allow-unsafe
pytest -v
docker-compose up  # test containers

# STEP 5: Deploy immediately
git commit -am "security: Fix CVE in psycopg"
git push
# CI runs, deploys to production
```

### Rollback (if necessary)
```bash
# Find last known good commit
git log --oneline requirements.txt | head -5

# Revert to previous version
git revert <commit-hash>

# Redeploy
git push
```

---

## 📊 Dependency Statistics

```
Total packages:      28
Direct dependencies: 13
Transitive deps:     15
Hash entries:        56
Python version:      3.13
File size:           ~15 KB
Last compiled:       2026-02-06
Vulnerabilities:     0 ⭐
```

---

## 🔄 Weekly Maintenance

```bash
# EVERY MONDAY:

# 1. Check for Dependabot alerts
#    Go to: GitHub → Security → Dependabot alerts

# 2. Merge security update PRs if any
#    (Dependabot creates them automatically)

# 3. Monitor for new vulnerabilities
#    pip-audit -r requirements.txt

# 4. Keep documentation updated
#    Review requirements.md, dependencies.md

# Takes: ~15 minutes
```

---

## 🎓 Learning Path

**New to pip-tools?**

1. Read: [requirements.md](requirements.md) (sections 1-3)
2. Try: `pip-compile --help`
3. Practice: Add a test dependency, compile, test
4. Understand: How transitive deps work

**Need GitHub setup?**

1. Read: [dependencies.md](dependencies.md) (sections 1-3)
2. Check: GitHub Security tab in your repo
3. Monitor: Dependabot alerts weekly

**Production deployment?**

1. Use: `pip install -r requirements.txt --require-hashes --allow-unsafe`
2. Verify: Hash matching before install
3. Monitor: GitHub Dependabot alerts continuously

---

## ❓ FAQ

**Q: Can I edit requirements.txt directly?**  
A: ❌ NO. Always edit requirements.in, then run pip-compile.

**Q: What if pip-compile fails?**  
A: Check for version conflicts. Try updating one package at a time.

**Q: How often should we update dependencies?**  
A: Security updates immediately. Patch updates monthly. Major updates quarterly.

**Q: What's the --require-hashes flag?**  
A: It tells pip to verify each package's hash. Installation fails if hash doesn't match.

**Q: Do we need pip-tools installed in production?**  
A: No. Only in development for compilation. Production only needs pip.

**Q: How do we handle breaking changes?**  
A: Test in staging. Update in requirements.in. Merge to main when tests pass.

---

## 🔗 Related Files

- [requirements.md](requirements.md) - Full pip-tools guide
- [dependencies.md](dependencies.md) - GitHub security guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Complete overview

---

## ✅ You're Good If

```
✅ pip install -r requirements.txt --require-hashes --allow-unsafe works
✅ All 28 packages install successfully
✅ pip-audit shows 0 vulnerabilities
✅ You understand requirements.in vs requirements.txt
✅ You can add a new dependency and compile it
✅ You can merge a Dependabot security update
```

---

**Last Updated**: 2026-02-06  
**Status**: Production-ready  
**Questions**: See requirements.md or dependencies.md
