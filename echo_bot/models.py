from django.db import models


class Subject(models.Model):
    code_name = models.CharField(max_length=64, verbose_name="Name")
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


def user_directory_path(instance, filename):
    print(filename)
    if not instance.subject:
        return filename
    return '{0}/{1}'.format(instance.subject.code_name, filename)


class Image(models.Model):
    subject = models.ForeignKey(Subject, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
