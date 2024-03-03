from email.policy import default
from random import choices
from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from django.utils import timezone
from taggit.managers import TaggableManager

import os, uuid, time


User = get_user_model()


def _set_uploaded_filename(instance, filename):
    base_path = timezone.now().strftime("products/%Y/%m/%d")
    filename, ext = os.path.splitext(os.path.basename(filename))
    new_filename = uuid.uuid5(uuid.NAMESPACE_URL, f"{filename}-{time.time()}")
    output_filename = os.path.join(base_path, f"{new_filename}{ext}")
    return output_filename


class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from="title", unique=True, null=False, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    parent = models.ForeignKey(
        "self", related_name="children", on_delete=models.CASCADE, blank=True, null=True
    )
    user = models.ForeignKey(User, related_name="shop_cats", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = (
            "slug",
            "parent",
        )
        verbose_name_plural = "categories"

    def __str__(self):
        full_path = [self.title]
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return " -> ".join(full_path[::-1])


class Product(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from="title", unique=True, null=False, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    content = models.TextField()
    features = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    price = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    disabled = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    video = models.CharField(max_length=5000, null=True, blank=True)
    image_cover = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog1 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog2 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog3 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.PROTECT
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()
    

    def __str__(self) -> str:
        return self.title


class Review(models.Model):
    review = models.TextField()
    rate = models.FloatField(default=3)
    name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.review[0:10]


class ProductImages(models.Model):
    image = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.product.title


#  new models for no sale products
class CategoryProd(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from="title", unique=True, null=False, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="shop_prod_cats", on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.title
    class Meta:
        unique_together = (
            "slug",
        )
        verbose_name_plural = "prod_categories"



class ProductProd(models.Model):
    title = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from="title", unique=True, null=False, editable=False)
    description = models.CharField(max_length=1024, null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    content = models.TextField()
    features = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    disabled = models.BooleanField(default=False)
    video = models.CharField(max_length=5000, null=True, blank=True)
   
    image_cover = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog1 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog2 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )
    catalog3 = models.FileField(
        upload_to=_set_uploaded_filename, null=True, blank=True
    )

    category = models.ForeignKey(
        CategoryProd, related_name="prod_products", on_delete=models.PROTECT
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()

    wing_dimensions                       = models.CharField(max_length=700, null=True, blank=True, verbose_name="ابعاد بال گیر")
    maximum_thickness                     = models.CharField(max_length=700, null=True, blank=True, verbose_name="حد اکثر ضخامت بال قابل نورد")
    longitudinal_movement                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="موتور اصلی حرکت طولی")
    pusher_engines                        = models.CharField(max_length=700, null=True, blank=True, verbose_name="موتور های فشار دهنده")
    pusher_gearboxes                      = models.CharField(max_length=700, null=True, blank=True, verbose_name="گیربکس های فشار دهنده")
    power_transmission                    = models.CharField(max_length=700, null=True, blank=True, verbose_name="انتقال نیرو در فشاردهنده ها")
    high_pressure_gearbox                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع گیربکس فشاردهنده بالا")
    high_pressure_engine                  = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع موتور فشاردهنده بالا")
    drive_motor                           = models.CharField(max_length=700, null=True, blank=True, verbose_name="موتور محرک دستگاه")

    mechanism_type                        = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع مکانیزم")
    cutting_milling_head_count            = models.CharField(max_length=700, null=True, blank=True, verbose_name="تعداد هد برشکاری/فرزکاری")#
    worktable_dimensions                  = models.CharField(max_length=700, null=True, blank=True, verbose_name="ابعاد مفید میزکار")#
    total_weight                          = models.CharField(max_length=700, null=True, blank=True, verbose_name="وزن کلی دستگاه")#
    operating_voltage                     = models.CharField(max_length=700, null=True, blank=True, verbose_name="ولتاژ کاری")#
    axis_x_y_movement_system              = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم حرکتی محور X & Y")
    axis_a_b_movement_system              = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم حرکتی محور A & B")
    axis_z_movement_system                = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم حرکتی محور Z")
    rotary_axis_c                         = models.CharField(max_length=700, null=True, blank=True, verbose_name="محور C روتاری")
    z_axis_working_range                  = models.CharField(max_length=700, null=True, blank=True, verbose_name="محدوده کاری محور Z")
    x_y_axis_speed                        = models.CharField(max_length=700, null=True, blank=True, verbose_name="سرعت حرکتی محور X & Y")
    z_axis_speed                          = models.CharField(max_length=700, null=True, blank=True, verbose_name="سرعت حرکتی محور Z")
    spindle_type                          = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع اسپیندل")
    power_transmission_system             = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم انتقال نیرو")
    drive_motor_type                      = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع موتورهای حرکتی")
    jack_type                             = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع جک ها")
    gearbox_type                          = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع سیستم گیربکس")
    rotary_gearboxes                      = models.CharField(max_length=700, null=True, blank=True, verbose_name="گیربکس های روتاری")
    height_control_system                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم کنترل ارتفاع")
    machine_maximum_error                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="حداکثر خطای ماشین")
    controller_maximum_error              = models.CharField(max_length=700, null=True, blank=True, verbose_name="حداکثر خطای سیستم کنترلر")
    cutting_milling_thickness_range       = models.CharField(max_length=700, null=True, blank=True, verbose_name="محدوده ضخامت برشکاری / فرزکاری")
    spindle_distance_between_axes         = models.CharField(max_length=700, null=True, blank=True, verbose_name="آکس بین اسپیندل ها")
    maximum_rotary_part_opening_length    = models.CharField(max_length=700, null=True, blank=True, verbose_name="حداکثر طول باز شدن قسمت روتاری")
    maximum_disk_diameter                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="حداکثر قطر دیسک")
    plasma_installation_prerequisites     = models.CharField(max_length=700, null=True, blank=True, verbose_name="پیش نیاز نصب پلاسما")
    maximum_laser_power                   = models.CharField(max_length=700, null=True, blank=True, verbose_name="حداکثر توان لیزر")
    laser_technology_type                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع تکنولوژی لیزر")
    machine_movement_accuracy             = models.CharField(max_length=700, null=True, blank=True, verbose_name="دقت حرکتی دستگاه")
    drilling_accuracy                     = models.CharField(max_length=700, null=True, blank=True, verbose_name="دقت سوراخکاری دستگاه")
    cable_thickness_cable_length          = models.CharField(max_length=700, null=True, blank=True, verbose_name="ضخامت کابل / طول کابل")
    water_pump_capacity                   = models.CharField(max_length=700, null=True, blank=True, verbose_name="ظرفیت پمپ آب")
    water_collection_tank                 = models.CharField(max_length=700, null=True, blank=True, verbose_name="حوضچه جمع آوری آب")
    glass_separation_system_after_cutting = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم جداسازی شیشه پس از برش")
    glass_easy_movement_system            = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم حرکت آسان شیشه")
    pipe_boring_dimensions                = models.CharField(max_length=700, null=True, blank=True, verbose_name="ابعاد مفید لوله بر")
    controller_type                       = models.CharField(max_length=700, null=True, blank=True, verbose_name="نوع کنترلر")
    g_code_reading_capability             = models.CharField(max_length=700, null=True, blank=True, verbose_name="قابلیت خواندن G-code")
    electrical_panel                      = models.CharField(max_length=700, null=True, blank=True, verbose_name="تابلو برق")
    computer_system                       = models.CharField(max_length=700, null=True, blank=True, verbose_name="سیستم کامپیوتری")
    uniform_spraying_material_reservoir   = models.CharField(max_length=700, null=True, blank=True, verbose_name="مخزن پاشش یکنواخت ماده ساینده")
    abrasive_tank                         = models.CharField(max_length=700, null=True, blank=True, verbose_name="مخزن ماده ساینده")
    abrasive_hopper                       = models.CharField(max_length=700, null=True, blank=True, verbose_name="Abrasive hopper")
    waterjet_pump_power                   = models.CharField(max_length=700, null=True, blank=True, verbose_name="توان پمپ واترجت")

    

    
    def __str__(self) -> str:
        return self.title 



class ReviewProd(models.Model):
    review = models.TextField()
    rate = models.FloatField(default=3)
    name = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(
        ProductProd, related_name="prod_reviews", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.review[0:10]


class ProductImagesProd(models.Model):
    image = models.FileField(upload_to=_set_uploaded_filename, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        ProductProd, related_name="prod_images", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.product.title



class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    invoice_number = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=128)
    company = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=512)
    zipcode = models.IntegerField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invoices", blank=True)
    count = models.PositiveIntegerField(default=0)
    sub_total = models.PositiveIntegerField(default=0)
    shipping = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
      self.total = int(self.sub_total) + int(self.shipping)
      super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.phone}-{self.total}"
    
class CartItem(models.Model):
    title = models.CharField(max_length=128)
    count = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='items')

    def __str__(self) -> str:
        return f"{self.title}-total: {self.total}"

class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CANCEL = 'cancel'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCEL, 'Canceled'),
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    refid = models.CharField(max_length=100, null=True, blank=True)
    authority = models.CharField(max_length=100, null=True, blank=True)
    amount=models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="payments", blank=True)
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name="payment", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.phone if self.user else 'A user'} - {self.status}"