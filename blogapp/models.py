from django.db import models
from django.utils import timezone
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

from PIL import Image
from io import BytesIO
import os.path



class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    image_full = models.ImageField(
        upload_to='pic_folder/', default='pic_folder/if_value_poster_2.png')
    image_display=models.ImageField(upload_to='pic_folder/display/', 
                                    default='pic_folder/display/muybridge_horse_small.jpg' )

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def _resize(self):
        scale = 200
        im = Image.open(self.image_full)
        width, height = im.size
        im = im.resize((int(width/height*scale), scale), Image.ANTIALIAS)

        output = StringIO()
        file_path = os.path.join(settings.MEDIA_ROOT, 'display/', os.path.basename(self.image_full.name)) 
        im.save(output, format='JPEG', quality=100)
        #output.seek(0)
        self.image_display.save(file_path, output.getvalue())

    def resize(self):
        #self.image_display = InMemoryUploadedFile(
        #   output,'ImageField', "%s.jpg" %self.image_full.name.split('.')[0],
        #    'image/jpeg', sys.getsizeof(output), None)
        #self.save()

            # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        if not self.image_full:
            return

        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Set our max thumbnail size in a tuple (max width, max height)
        THUMBNAIL_SIZE = (99, 66)

        if self.image_full.name.endswith(".jpg"):
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
            DJANGO_TYPE = 'image/jpeg'

        elif self.image_full.name.endswith(".png"):
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'
            DJANGO_TYPE = 'image/png'

        # Open original photo which we want to thumbnail using PIL's Image
        image = Image.open(BytesIO(self.image_full.read()))
        scale = 300
        width, height = image.size
        image = image.resize((int(width/height*scale), scale), Image.ANTIALIAS)

        # We use our PIL Image object to create the thumbnail, which already
        # has a thumbnail() convenience method that contrains proportions.
        # Additionally, we use Image.ANTIALIAS to make the image look better.
        # Without antialiasing the image pattern artifacts may result.
        #image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = BytesIO()
        image.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.image_full.name)[-1],
                temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.image_display.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )

        force_update = False
        if self.id:
            force_update = True
        super(Post, self).save(force_update=force_update)

    def __str__(self):
        return self.title

