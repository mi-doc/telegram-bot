from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=64, verbose_name="Name")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


def upload_directory_path(instance, filename):
    if not instance.subject:
        return filename
    return '{0}/{1}'.format(instance.subject.name, filename)


class Image(models.Model):
    subject = models.ForeignKey(Subject, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_directory_path)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
