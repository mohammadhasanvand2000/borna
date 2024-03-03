from django.db import models
from django.utils import timezone
import os, uuid, time
from django.contrib.auth import get_user_model

User = get_user_model()

def _set_uploaded_filename(instance, filename):
    base_path = timezone.now().strftime('profiles/%Y/%m/%d')
    filename, ext = os.path.splitext(os.path.basename(filename))
    new_filename = uuid.uuid5(uuid.NAMESPACE_URL, f'{filename}-{time.time()}')
    output_filename = os.path.join(base_path, f'{new_filename}{ext}')
    return output_filename

class Profile(models.Model):
    address = models.CharField(max_length=1024, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    phone = models.CharField(max_length=32, null=True, blank=True)
    zipcode = models.CharField(max_length=32, null=True, blank=True)
    avatar = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.user.fullname) or ""
