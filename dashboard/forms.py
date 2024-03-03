from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from jalali_date.fields import JalaliDateTimeField
from jalali_date.widgets import AdminJalaliDateWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from blog import models as blog_models
from shop import models as shop_models

class TitleOfModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title

#  Sign in forms ...
class ProfileForm(forms.Form):
    fullname = forms.CharField(required=False)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False)
    city = forms.CharField(required=False)
    zipcode = forms.CharField(required=False)
    phone2 = forms.CharField(required=False)
    pass1 = forms.CharField(required=False, widget=forms.PasswordInput())
    pass2 = forms.CharField(required=False, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("pass1")
        pass2 = cleaned_data.get("pass2")

        if pass1 != pass2:
            raise ValidationError("pass1 and pass2 must be the same!")


class ProfilePicForm(forms.Form):
    avatar = forms.FileField(required=False)


class UserAddForm(forms.Form):
    USER_LEVEL = [
        ("user", "کاربر"),
        ("admin", "مدیر"),
    ]
    fullname = forms.CharField(required=False)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput())
    is_active = forms.BooleanField(required=False)
    is_superuser = forms.ChoiceField(required=False, choices=USER_LEVEL)

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if data and len(data) < 5:
            raise ValidationError("password must be at least 5 characters.")
        return data.strip()


class SMSForm(forms.Form):
    numbers = forms.CharField(required=True, max_length=1024)
    another_time = forms.BooleanField(required=False, initial=False)
    date = JalaliDateTimeField(
        required=False, widget=AdminJalaliDateWidget(format="%d-%m-%Y %H:%M")
    )
    time = forms.TimeField(required=False, widget=forms.TimeInput(format="%H:%M"))
    text = forms.CharField(
        required=True, max_length=512, widget=forms.Textarea(attrs={"rows": 4})
    )

class AddBlogCatForm(forms.Form):
    title = forms.CharField(required=True, max_length=128) 
    description = forms.CharField(required=True, max_length=256) 
    parent = TitleOfModelChoiceField(queryset=blog_models.Category.objects.all().order_by('date_created'), empty_label="لطفا یک مورد را انتخاب نمایید...", required=False) 

class AddShopCatForm(forms.Form):
    title = forms.CharField(required=True, max_length=128) 
    description = forms.CharField(required=True, max_length=256) 
    parent = TitleOfModelChoiceField(queryset=shop_models.Category.objects.all().order_by('date_created'), empty_label="لطفا یک مورد را انتخاب نمایید...", required=False)

class AddProdShopCatForm(forms.Form):
    title = forms.CharField(required=True, max_length=128) 
    description = forms.CharField(required=True, max_length=256) 


class AddEditBlogForm(forms.Form):
    title = forms.CharField(max_length=128)
    description = forms.CharField(max_length=256)
    tags = forms.CharField(max_length=512, required=True)
    content = forms.CharField(widget=CKEditorUploadingWidget(attrs={'rows': 10}))
    image_wide= forms.FileField(required=False)
    image_cover=forms.FileField(required=False)
    image_icon=forms.FileField(required=False)
    category = TitleOfModelChoiceField(queryset=blog_models.Category.objects.all().order_by('date_created'), empty_label="لطفا یک مورد را انتخاب نمایید...")

class AddEditShopForm(forms.Form):
    title = forms.CharField(max_length=128)
    description=forms.CharField(max_length=256)
    tags = forms.CharField(max_length=512, required=True)
    content=forms.CharField(widget=CKEditorUploadingWidget(attrs={'rows': 10}))
    # features=forms.CharField(widget=CKEditorUploadingWidget(attrs={'rows': 10}))
    price=forms.IntegerField()
    discount=forms.IntegerField()
    disabled=forms.BooleanField(required=False)
    amount=forms.IntegerField()
    video = forms.CharField(max_length=5000, required=False)
    image_cover=forms.FileField(required=False)
    catalog1=forms.FileField(required=False)
    catalog2=forms.FileField(required=False)
    catalog3=forms.FileField(required=False)
    category=TitleOfModelChoiceField(queryset=shop_models.Category.objects.all().order_by('date_created'), empty_label="لطفا یک مورد را انتخاب نمایید...")

    wing_dimensions = forms.CharField(max_length=700, required=False)
    maximum_thickness = forms.CharField(max_length=700, required=False)
    longitudinal_movement = forms.CharField(max_length=700, required=False)
    pusher_engines = forms.CharField(max_length=700, required=False)
    pusher_gearboxes = forms.CharField(max_length=700, required=False)
    power_transmission = forms.CharField(max_length=700, required=False)
    high_pressure_gearbox = forms.CharField(max_length=700, required=False)
    high_pressure_engine = forms.CharField(max_length=700, required=False)
    drive_motor = forms.CharField(max_length=700, required=False)

    mechanism_type = forms.CharField(max_length=700, required=False)
    cutting_milling_head_count = forms.CharField(max_length=700, required=False)
    worktable_dimensions = forms.CharField(max_length=700, required=False)
    total_weight = forms.CharField(max_length=700, required=False)
    operating_voltage = forms.CharField(max_length=700, required=False)
    axis_x_y_movement_system = forms.CharField(max_length=700, required=False)
    axis_a_b_movement_system = forms.CharField(max_length=700, required=False)
    axis_z_movement_system = forms.CharField(max_length=700, required=False)
    rotary_axis_c = forms.CharField(max_length=700, required=False)
    z_axis_working_range = forms.CharField(max_length=700, required=False)
    x_y_axis_speed = forms.CharField(max_length=700, required=False)
    z_axis_speed = forms.CharField(max_length=700, required=False)
    spindle_type = forms.CharField(max_length=700, required=False)
    power_transmission_system = forms.CharField(max_length=700, required=False)
    drive_motor_type = forms.CharField(max_length=700, required=False)
    jack_type = forms.CharField(max_length=700, required=False)
    gearbox_type = forms.CharField(max_length=700, required=False)
    rotary_gearboxes = forms.CharField(max_length=700, required=False)
    height_control_system = forms.CharField(max_length=700, required=False)
    machine_maximum_error = forms.CharField(max_length=700, required=False)
    controller_maximum_error = forms.CharField(max_length=700, required=False)
    cutting_milling_thickness_range = forms.CharField(max_length=700, required=False)
    spindle_distance_between_axes = forms.CharField(max_length=700, required=False)
    maximum_rotary_part_opening_length = forms.CharField(max_length=700, required=False)
    maximum_disk_diameter = forms.CharField(max_length=700, required=False)
    plasma_installation_prerequisites = forms.CharField(max_length=700, required=False)
    maximum_laser_power = forms.CharField(max_length=700, required=False)
    laser_technology_type = forms.CharField(max_length=700, required=False)
    machine_movement_accuracy = forms.CharField(max_length=700, required=False)
    drilling_accuracy = forms.CharField(max_length=700, required=False)
    cable_thickness_cable_length = forms.CharField(max_length=700, required=False)
    water_pump_capacity = forms.CharField(max_length=700, required=False)
    water_collection_tank = forms.CharField(max_length=700, required=False)
    glass_separation_system_after_cutting = forms.CharField(max_length=700, required=False)
    glass_easy_movement_system = forms.CharField(max_length=700, required=False)
    pipe_boring_dimensions = forms.CharField(max_length=700, required=False)
    controller_type = forms.CharField(max_length=700, required=False)
    g_code_reading_capability = forms.CharField(max_length=700, required=False)
    electrical_panel = forms.CharField(max_length=700, required=False)
    computer_system = forms.CharField(max_length=700, required=False)
    uniform_spraying_material_reservoir = forms.CharField(max_length=700, required=False)
    abrasive_tank = forms.CharField(max_length=700, required=False)
    abrasive_hopper = forms.CharField(max_length=700, required=False)
    waterjet_pump_power = forms.CharField(max_length=700, required=False)
    

class AddEditProdShopForm(forms.Form):
    title = forms.CharField(max_length=128)
    description=forms.CharField(max_length=256)
    tags = forms.CharField(max_length=512, required=True)
    content=forms.CharField(widget=CKEditorUploadingWidget(attrs={'rows': 10}))
    # features=forms.CharField(widget=CKEditorUploadingWidget(attrs={'rows': 10}))
    disabled=forms.BooleanField(required=False)
    image_cover=forms.FileField(required=False)
    video = forms.CharField(max_length=5000, required=False)
    catalog1=forms.FileField(required=False)
    catalog2=forms.FileField(required=False)
    catalog3=forms.FileField(required=False)
    category=TitleOfModelChoiceField(queryset=shop_models.CategoryProd.objects.all().order_by('date_created'), empty_label="لطفا یک مورد را انتخاب نمایید...")
    wing_dimensions = forms.CharField(max_length=700, required=False)
    maximum_thickness = forms.CharField(max_length=700, required=False)
    longitudinal_movement = forms.CharField(max_length=700, required=False)
    pusher_engines = forms.CharField(max_length=700, required=False)
    pusher_gearboxes = forms.CharField(max_length=700, required=False)
    power_transmission = forms.CharField(max_length=700, required=False)
    high_pressure_gearbox = forms.CharField(max_length=700, required=False)
    high_pressure_engine = forms.CharField(max_length=700, required=False)
    drive_motor = forms.CharField(max_length=700, required=False)

    mechanism_type = forms.CharField(max_length=700, required=False)
    cutting_milling_head_count = forms.CharField(max_length=700, required=False)
    worktable_dimensions = forms.CharField(max_length=700, required=False)
    total_weight = forms.CharField(max_length=700, required=False)
    operating_voltage = forms.CharField(max_length=700, required=False)
    axis_x_y_movement_system = forms.CharField(max_length=700, required=False)
    axis_a_b_movement_system = forms.CharField(max_length=700, required=False)
    axis_z_movement_system = forms.CharField(max_length=700, required=False)
    rotary_axis_c = forms.CharField(max_length=700, required=False)
    z_axis_working_range = forms.CharField(max_length=700, required=False)
    x_y_axis_speed = forms.CharField(max_length=700, required=False)
    z_axis_speed = forms.CharField(max_length=700, required=False)
    spindle_type = forms.CharField(max_length=700, required=False)
    power_transmission_system = forms.CharField(max_length=700, required=False)
    drive_motor_type = forms.CharField(max_length=700, required=False)
    jack_type = forms.CharField(max_length=700, required=False)
    gearbox_type = forms.CharField(max_length=700, required=False)
    rotary_gearboxes = forms.CharField(max_length=700, required=False)
    height_control_system = forms.CharField(max_length=700, required=False)
    machine_maximum_error = forms.CharField(max_length=700, required=False)
    controller_maximum_error = forms.CharField(max_length=700, required=False)
    cutting_milling_thickness_range = forms.CharField(max_length=700, required=False)
    spindle_distance_between_axes = forms.CharField(max_length=700, required=False)
    maximum_rotary_part_opening_length = forms.CharField(max_length=700, required=False)
    maximum_disk_diameter = forms.CharField(max_length=700, required=False)
    plasma_installation_prerequisites = forms.CharField(max_length=700, required=False)
    maximum_laser_power = forms.CharField(max_length=700, required=False)
    laser_technology_type = forms.CharField(max_length=700, required=False)
    machine_movement_accuracy = forms.CharField(max_length=700, required=False)
    drilling_accuracy = forms.CharField(max_length=700, required=False)
    cable_thickness_cable_length = forms.CharField(max_length=700, required=False)
    water_pump_capacity = forms.CharField(max_length=700, required=False)
    water_collection_tank = forms.CharField(max_length=700, required=False)
    glass_separation_system_after_cutting = forms.CharField(max_length=700, required=False)
    glass_easy_movement_system = forms.CharField(max_length=700, required=False)
    pipe_boring_dimensions = forms.CharField(max_length=700, required=False)
    controller_type = forms.CharField(max_length=700, required=False)
    g_code_reading_capability = forms.CharField(max_length=700, required=False)
    electrical_panel = forms.CharField(max_length=700, required=False)
    computer_system = forms.CharField(max_length=700, required=False)
    uniform_spraying_material_reservoir = forms.CharField(max_length=700, required=False)
    abrasive_tank = forms.CharField(max_length=700, required=False)
    abrasive_hopper = forms.CharField(max_length=700, required=False)
    waterjet_pump_power = forms.CharField(max_length=700, required=False)
    
class CommentEditForm(forms.Form):
    name = forms.CharField(max_length=128)
    email=forms.EmailField(required=False ,max_length=256)
    comment=forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

class ReviewEditForm(forms.Form):
    name = forms.CharField(max_length=128)
    email=forms.EmailField(required=False ,max_length=256)
    rate=forms.FloatField(required=True)
    review=forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))

class ProductImagesForm(forms.Form):
    pic1 = forms.FileField(required=False)
    pic2 = forms.FileField(required=False)
    pic3 = forms.FileField(required=False)
    pic4 = forms.FileField(required=False)
    pic5 = forms.FileField(required=False)

class SliderContentForm(forms.Form):
    small_title = forms.CharField(max_length=128, required=True)
    big_title = forms.CharField(max_length=128, required=True)
    description = forms.CharField(max_length=256, required=True)
    cta_title = forms.CharField(max_length=128, required=True)
    cta_link = forms.CharField(max_length=256, required=True)
    image = forms.FileField(required=False)