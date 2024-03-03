from email.policy import default
from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField 
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

import os, uuid, time


User = get_user_model()


def _set_uploaded_filename(instance, filename):
    base_path = timezone.now().strftime('blogs/%Y/%m/%d')
    filename, ext = os.path.splitext(os.path.basename(filename))
    new_filename = uuid.uuid5(uuid.NAMESPACE_URL, f'{filename}-{time.time()}')
    output_filename = os.path.join(base_path, f'{new_filename}{ext}')
    return output_filename


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title', unique=True, null=False, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank = 
    True, null=True)
    user = models.ForeignKey(User, related_name='blog_cats' ,on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title or ""
    class Meta:
        unique_together = ('slug', 'parent',)    
        verbose_name_plural = "categories"     

    def __str__(self):                           
        full_path = [self.title]                  
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])  
    
class Post(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='title', unique=True, null=False, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    content = RichTextUploadingField(null=True, blank=True)
    image_wide  = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    image_cover  = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    image_icon  = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.PROTECT, blank = 
    True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()

    def __str__(self) -> str:
        return self.title or ""

class Comment(models.Model):
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, blank = 
    True, null=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.comment[0:10] or ""

class PostImages(models.Model):
    image  = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey(Post, related_name='images' ,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.post.title or ""