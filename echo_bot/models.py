from django.db import models


class Person(models.Model):
    code_name = models.CharField(max_length=64, verbose_name="Name")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"


class Photo(models.Model):
    person = models.ForeignKey(Person, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='person_images/')
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Protos"
