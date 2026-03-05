# people/models/person.py
from core.models import Auditory
from django.db import models
from nanoid_field import NanoidField


class Person(Auditory):
    """Base class for people."""

    id = models.BigAutoField(primary_key=True)
    public_id = NanoidField(unique=True, editable=False, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    address = models.ForeignKey(
        "core.Address", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
