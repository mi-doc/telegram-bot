from django.db import models
from tempfile import TemporaryFile


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
    media_group_id = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = ImageManager()

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def assign_to_subject_and_media_group(self, subject_name=None, subject_instance=None, media_group_id=None):
        subj = subject_instance or Subject.objects.get_or_create(user_id=self.user_id, name=subject_name)[0]
        self.subject = subj
        self.save()

    @classmethod
    def get_last_image_sent_by_user(cls, user_id):
        return cls.objects.filter(user_id=user_id).order_by('created').last()

    @classmethod
    def create_from_telegram_data(cls, *, image_name, downloaded_file, user_id, media_group_id):
        img_temp = TemporaryFile()
        img_temp.write(downloaded_file)
        img_temp.flush()
        new_img = Image.objects.create(user_id=user_id, media_group_id=media_group_id)
        new_img.image.save(image_name, img_temp)
        new_img.save()
        return new_img

    @classmethod
    def get_all_subject_images(cls, *, subject_name=None, subject_id=None):
        keyword = {'subject__id': subject_id} if subject_id else {'subject__name': subject_name}
        filter_by_sbj = cls.objects.filter(**keyword)

        values = filter_by_sbj.filter(media_group_id__isnull=False).values_list('media_group_id', flat=True).distinct()
        filter_by_media_group = cls.objects.filter(media_group_id__in=list(values))
        return filter_by_sbj.union(filter_by_media_group).order_by('created')


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
