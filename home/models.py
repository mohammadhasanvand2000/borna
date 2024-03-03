from django.db import models
from django.utils import timezone

import time, os, uuid


def _set_uploaded_filename(instance, filename):
    base_path = timezone.now().strftime("products/%Y/%m/%d")
    filename, ext = os.path.splitext(os.path.basename(filename))
    new_filename = uuid.uuid5(uuid.NAMESPACE_URL, f"{filename}-{time.time()}")
    output_filename = os.path.join(base_path, f"{new_filename}{ext}")
    return output_filename

class ContatcUs(models.Model):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=128)
    message = models.CharField(max_length=2048)
    is_seen = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name+ "-"+ self.subject

class SliderContent(models.Model):
    small_title = models.CharField(max_length=128)
    big_title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    image = models.FileField(upload_to=_set_uploaded_filename)
    cta_title =models.CharField(max_length=128)
    cta_link =models.CharField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.small_title