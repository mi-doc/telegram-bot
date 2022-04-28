from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=64, verbose_name="Name")
    user_id = models.CharField(max_length=64, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


# def upload_directory_path(instance, filename):
#     if not instance.subject:
#         return f"other/{filename}"
#     return f"{instance.subject.name}/{filename}"


class ImageManager(models.Manager):

    def get_images_with_files_uploaded(self):
        return self.exclude(image__in=['', None])


class Image(models.Model):
    user_id = models.CharField(max_length=64, blank=True, null=True)
    subject = models.ForeignKey(Subject, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = ImageManager()

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def assign_to_subject(self, subject_name=None, subject_instance=None):
        subj = subject_instance or Subject.objects.get_or_create(user_id=self.user_id, name=subject_name)[0]
        self.subject = subj
        self.save()

    @classmethod
    def get_last_image_sent_by_user(cls, user_id):
        return cls.objects.filter(user_id=user_id).order_by('created').last()


class UserState(models.Model):
    class State(models.TextChoices):
        INIT = '1', 'Initial'
        SENT_PHOTO = '2', 'Photo is sent'
        CREATE_NEW_SUBJECT = '3', 'Creating new subject'

    user_id = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.INIT)

    @classmethod
    def check_if_user_has_sent_photo(cls, user_id):
        state_qs = cls.objects.filter(user_id=user_id)
        if state_qs and state_qs.first().state == cls.State.SENT_PHOTO:
            return True
        return False

    @classmethod
    def get_for_user_id(cls, user_id):
        return UserState.objects.get_or_create(user_id=user_id)[0]

    @classmethod
    def update_user_state(cls, user_id, new_state=State.INIT):
        state = cls.objects.get_or_create(user_id=user_id)[0]
        state.state = new_state
        state.save()

    @classmethod
    def update_user_state_to_init(cls, user_id):
        state = cls.objects.get_or_create(user_id=user_id)[0]
        state.state = cls.State.INIT
        state.save()

    @classmethod
    def update_user_state_to_sent_photo(cls, user_id):
        state = cls.objects.get_or_create(user_id=user_id)[0]
        state.state = cls.State.SENT_PHOTO
        state.save()
