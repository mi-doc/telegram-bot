from django.db import models
from tempfile import TemporaryFile


class Album(models.Model):
    name = models.CharField(max_length=64, verbose_name="Name")
    user_id = models.CharField(max_length=64, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        verbose_name = "Album"
        verbose_name_plural = "Albums"


class ImageManager(models.Manager):

    def get_images_with_files_uploaded(self):
        """
        Returns a queryset of all image instances that have image file accessible
        :return: Image queryset
        """
        return self.exclude(image__in=['', None])

    def get_last_image_sent_by_user(self, user_id):
        """
        Returns the last image user uploaded to the album bot
        :param user_id: telegram user id
        :return: Image instance
        """
        return self.filter(user_id=user_id).order_by('created').last()

    def create_from_telegram_data(self, *, image_name, downloaded_file, user_id, media_group_id):
        """
        Creates Image instance from uploaded telegram image
        :param image_name: name of the new image
        :param downloaded_file: image binary data
        :param user_id: telegram user id
        :param media_group_id: telegram media group id of image is part of a set of images
        :return: Image instance
        """
        img_temp = TemporaryFile()
        img_temp.write(downloaded_file)
        img_temp.flush()
        new_img = self.create(user_id=user_id, media_group_id=media_group_id)
        new_img.image.save(image_name, img_temp)
        new_img.save()
        return new_img

    def get_all_album_images(self, *, album_name=None, album_id=None):
        """
        Returns all images of the requested album. Accepts either album name or id
        :param album_name: name of the album
        :param album_id: id of the album
        :return: queryset of all album images
        """
        keyword = {'album__id': album_id} if album_id else {'album__name': album_name}
        filter_by_album = self.filter(**keyword)
        vals = filter_by_album.filter(media_group_id__isnull=False).values_list('media_group_id', flat=True).distinct()
        filter_by_media_group = self.filter(media_group_id__in=list(vals))
        return filter_by_album.union(filter_by_media_group).order_by('created')


def upload_directory_path(image, filename):
    """
    Path to save uploaded images
    :param image: Image instance
    :param filename: name of the image
    :return: absolute path in the static root
    """
    return f"{image.user_id}/{filename}"


class Image(models.Model):
    user_id = models.CharField(max_length=64, blank=True, null=True)
    album = models.ForeignKey(Album, blank=True, null=True, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_directory_path)
    media_group_id = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = ImageManager()

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def add_to_album(self, album_name=None, album_instance=None):
        """
        Adds image to a specified album. Accepts either album name or instance
        :param album_name: name of the album to add image to
        :param album_instance: instance of the album to add image to
        :return: Image instance
        """
        subj = album_instance or Album.objects.get_or_create(user_id=self.user_id, name=album_name)[0]
        self.album = subj
        self.save()
        return self

    def get_image_album(self):
        """
        Returns album containing the image, if present
        :return: Album instance or None
        """
        if self.album:
            return self.album
        if not self.media_group_id:
            return None
        return Image.objects.filter(media_group_id=self.media_group_id, album__isnull=False).first().album


class UserStateManager(models.Manager):

    def get_for_user_id(self, user_id):
        """
        Returns state of the user.
        :param user_id: telegram user_id
        :return: UserState instance
        """
        return self.get_or_create(user_id=user_id)[0]

    def update_user_state(self, user_id, new_state=None):
        """
        Updates user state to specified state
        :param user_id: telegram user_id
        :param new_state: the state user will get
        :return: UserState instance
        """
        state = self.get_or_create(user_id=user_id)[0]
        state.state = new_state or UserState.State.INIT
        state.save()
        return self


class UserState(models.Model):
    class State(models.TextChoices):
        INIT = '1', 'Initial'
        SENT_PHOTO = '2', 'Photo has been uploaded'
        CREATE_NEW_ALBUM = '3', 'Creating new album'

    user_id = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.INIT)

    objects = UserStateManager()
