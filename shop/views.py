import http
from operator import add
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.db.models import F, ExpressionWrapper, IntegerField
from django.http import Http404
from django.db.models.expressions import RawSQL
from django.core.paginator import Paginator
from . import models, forms
from taggit import models as tag_model
from home import forms as home_forms
from zeep import Client
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import CategoryProd

class ShopListCatView(View):
    def get(self, requset, cat_id):
        products = (
            models.Product.objects.filter(category__pk=cat_id)
            .order_by("-date_created")
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )
        paginator = Paginator(products, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )

        products_fav = (
            models.Product.objects.all()
            .order_by("-date_created")[:3]
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )

        context = {
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(requset, "shop/shop_list.html", context)


class ShopListTagView(View):
    def get(self, requset, tag_slug=None):
        tags = None
        products = []
        if tag_slug:
            tags = tag_model.Tag.objects.filter(slug=tag_slug)
            products = (
                models.Product.objects.filter(tags__in=tags)
                .order_by("-date_created")
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
            )
        paginator = Paginator(products, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )

        products_fav = (
            models.Product.objects.all()
            .order_by("-date_created")[:3]
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )

        context = {
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(requset, "shop/shop_list.html", context)
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from django.http import HttpResponse
from . import models

class ProdShopListCatView(View):
    def get(self, request, cat_id):
        
        category = models.CategoryProd.objects.get(pk=cat_id)
        catname=category.title
        
        related_products = models.ProductProd.objects.filter(category=category).order_by("-date_created")

        # تقسیم صفحه بندی
        paginator = Paginator(related_products, 9)
        page_number = request.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number, on_each_side=2, on_ends=1)
        procat = models.ProductProd.objects.filter(category_id=cat_id)
        # گرفتن محصولات محبوب
        products_fav = models.ProductProd.objects.all().order_by("-date_created")[:3]
        print(procat)
        context = {
            "catname":catname,
            "procat":procat,
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }

        # رندر کردن تمپلیت‌ها
        shop_list_html = render(request, "shop/shop_list_prod.html", context)
        home_index_html = render(request, "home/index.html", context)

        # ترکیب کردن محتوای HTML
        combined_html = shop_list_html.content + home_index_html.content

        return HttpResponse(combined_html)



class ProdShopListTagView(View):
    def get(self, requset, tag_slug=None):
        tags = None
        products = []
        if tag_slug:
            tags = tag_model.Tag.objects.filter(slug=tag_slug)
            products = models.ProductProd.objects.filter(tags__in=tags).order_by(
                "-date_created"
            )
        paginator = Paginator(products, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )

        products_fav = models.ProductProd.objects.all().order_by("-date_created")[:3]

        context = {
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(requset, "shop/shop_list_prod.html", context)


class ShopListView(View):
    def get(self, requset):
        products = (
            models.Product.objects.all()
            .order_by("-date_created")
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )
        paginator = Paginator(products, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )

        products_fav = (
            models.Product.objects.all()
            .order_by("-date_created")[:3]
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )

        context = {
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(requset, "shop/shop_list.html", context)


class ProdShopListView(View):
    def get(self, requset):
        products = (
            models.ProductProd.objects.all()
            .order_by("-date_created")
        )
        paginator = Paginator(products, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        product_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )

        products_fav = models.Product.objects.all().order_by("-date_created")[:3]
        category=CategoryProd.objects.all()
        print(
            

        )
        context = {
            "category":category,
            "products": product_obj,
            "products_fav": products_fav,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(requset, "shop/shop_list_prod.html", context)


class ShopDetailView(View):
    def get(self, requset, product_id):
        form = forms.ReviewForm()
        try:
            products_fav = (
                models.Product.objects.all()
                .order_by("-date_created")[:3]
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
            )
            products_sim = (
                models.Product.objects.all()
                .order_by("-date_created")[:15]
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
            )
            product = (
                models.Product.objects.filter(pk=product_id)
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
                .first()
            )
            all_cats = models.Category.objects.filter(parent__exact=None).order_by(
                "date_created"
            )[:6]
            reviews = models.Review.objects.filter(
                product__pk__exact=product_id
            ).order_by("-date_created")
            all_reviews = models.Review.objects.filter(
                product__pk__exact=product_id, is_approved=True
            ).order_by("-date_created")

            images = models.ProductImages.objects.filter(product__pk__exact=product_id)

            context = {
                "product": product,
                "products_sim": products_sim,
                "products_fav": products_fav,
                "reviews": reviews,
                "all_reviews": all_reviews,
                "images": images,
                "form": form,
                "all_cats": all_cats,
            }
            return render(requset, "shop/shop_detail.html", context)
        except Exception as e:
            print(e)
            raise Http404("Page not Found!")

    def post(self, request, product_id):
        form = forms.ReviewForm(request.POST)
        try:
            products_fav = (
                models.Product.objects.all()
                .order_by("-date_created")[:3]
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
            )
            products_sim = (
                models.Product.objects.all()
                .order_by("-date_created")[:15]
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
            )
            product = (
                models.Product.objects.filter(pk=product_id)
                .annotate(
                    final_price=ExpressionWrapper(
                        F("price") * (1 - F("discount") / 100.0),
                        output_field=IntegerField(),
                    )
                )
                .first()
            )
            all_cats = models.Category.objects.filter(parent__exact=None).order_by(
                "date_created"
            )[:6]
            reviews = models.Review.objects.filter(
                product__pk__exact=product_id
            ).order_by("-date_created")
            all_reviews = models.Review.objects.filter(
                product__pk__exact=product_id, is_approved=True
            ).order_by("-date_created")
            images = models.ProductImages.objects.filter(product__pk__exact=product_id)

            context = {
                "product": product,
                "products_sim": products_sim,
                "products_fav": products_fav,
                "reviews": reviews,
                "all_reviews": all_reviews,
                "images": images,
                "form": form,
                "all_cats": all_cats,
            }
            if form.is_valid():
                name = form.cleaned_data["name"]
                email = form.cleaned_data["email"]
                review = form.cleaned_data["review"]
                rate = form.cleaned_data["rate"]
                if request.user.is_authenticated:
                    user = request.user
                    models.Review.objects.create(
                        name=user.fullname,
                        email=user.email,
                        user=user,
                        product=product,
                        review=review,
                        rate=rate,
                        is_approved=True if user.is_superuser else False,
                    )
                else:
                    models.Review.objects.create(
                        name=name,
                        email=email,
                        user=None,
                        product=product,
                        review=review,
                        rate=rate,
                    )

                return redirect(
                    reverse("shop:shop-detail", kwargs={"product_id": product_id})
                )
            else:
                return render(request, "shop/shop_detail.html", context)
        except Exception as e:
            print(e)
            raise Http404("Page not found!")


class ProdShopDetailView(View):
    def get(self, requset, product_id):
        form = forms.ReviewForm()
        try:
            products_fav = models.ProductProd.objects.all().order_by("-date_created")[
                :3
            ]
            products_sim = models.ProductProd.objects.all().order_by("-date_created")[
                :15
            ]
            product = models.ProductProd.objects.filter(pk=product_id).first()

            reviews = models.ReviewProd.objects.filter(
                product__pk__exact=product_id
            ).order_by("-date_created")
            all_reviews = models.ReviewProd.objects.filter(
                product__pk__exact=product_id, is_approved=True
            ).order_by("-date_created")

            images = models.ProductImagesProd.objects.filter(
                product__pk__exact=product_id
            )
            all_cats = models.CategoryProd.objects.all().order_by("date_created")[:6]
            context = {
                "product": product,
                "products_sim": products_sim,
                "products_fav": products_fav,
                "reviews": reviews,
                "all_reviews": all_reviews,
                "images": images,
                "form": form,
                "all_cats": all_cats,
            }
            return render(requset, "shop/shop_detail_prod.html", context)
        except Exception as e:
            print("prod shop detail: ", e)
            raise Http404("Page not Found!")

    def post(self, request, product_id):
        form = forms.ReviewForm(request.POST)
        try:
            products_fav = models.ProductProd.objects.all().order_by("-date_created")[
                :3
            ]
            products_sim = models.ProductProd.objects.all().order_by("-date_created")[
                :15
            ]
            product = models.ProductProd.objects.filter(pk=product_id).first()

            reviews = models.ReviewProd.objects.filter(
                product__pk__exact=product_id
            ).order_by("-date_created")
            all_reviews = models.ReviewProd.objects.filter(
                product__pk__exact=product_id, is_approved=True
            ).order_by("-date_created")
            images = models.ProductImagesProd.objects.filter(
                product__pk__exact=product_id
            )
            all_cats = models.CategoryProd.objects.all().order_by("date_created")[:6]
            context = {
                "product": product,
                "products_sim": products_sim,
                "products_fav": products_fav,
                "reviews": reviews,
                "all_reviews": all_reviews,
                "images": images,
                "form": form,
                "all_cats": all_cats,
            }
            if form.is_valid():
                name = form.cleaned_data["name"]
                email = form.cleaned_data["email"]
                review = form.cleaned_data["review"]
                rate = form.cleaned_data["rate"]
                if request.user.is_authenticated:
                    user = request.user
                    models.ReviewProd.objects.create(
                        name=user.fullname,
                        email=user.email,
                        user=user,
                        product=product,
                        review=review,
                        rate=rate,
                        is_approved=True if user.is_superuser else False,
                    )
                else:
                    models.ReviewProd.objects.create(
                        name=name,
                        email=email,
                        user=None,
                        product=product,
                        review=review,
                        rate=rate,
                    )

                return redirect(
                    reverse("shop:prod-shop-detail", kwargs={"product_id": product_id})
                )
            else:
                return render(request, "shop/shop_detail_prod.html", context)
        except Exception as e:
            print(e)
            raise Http404("Page not found!")


class ShopCartView(View):
    def get(self, requset):
        products_sim = (
            models.Product.objects.all()
            .order_by("-date_created")[:15]
            .annotate(
                final_price=ExpressionWrapper(
                    F("price") * (1 - F("discount") / 100.0),
                    output_field=IntegerField(),
                )
            )
        )
        cart = requset.session.get("cart", {})
        shipping = 25000
        total_invoice = shipping + cart["total"] if "total" in cart else 0
        context = {
            "cart": cart,
            "shipping": shipping,
            "total_invoice": total_invoice,
            "products_sim": products_sim,
        }
        return render(requset, "shop/shop_cart.html", context)


class ShopCheckoutView(View):
    def get(self, requset):
        # login form
        form_login = home_forms.SigninForm()

        # discount form
        form_discount = forms.DiscountForm()

        # customer info form
        if requset.user.is_authenticated:
            form_customer = forms.CustomerForm(
                initial={
                    "name": requset.user.fullname or "",
                    "company": "",
                    "address": requset.user.profile.address or "",
                    "zipcode": requset.user.profile.zipcode or "",
                    "phone": requset.user.phone or "",
                    "email": requset.user.email or "",
                    "description": "",
                }
            )
        else:
            form_customer = forms.CustomerForm()

        cart = requset.session.get("cart", {})
        shipping = 25000
        total_invoice = shipping + cart["total"] if "total" in cart else 0

        context = {
            "form_login": form_login,
            "form_discount": form_discount,
            "form_customer": form_customer,
            "cart": cart,
            "shipping": shipping,
            "total_invoice": total_invoice,
        }
        return render(requset, "shop/shop_checkout.html", context)

    def post(self, request):
        form = forms.CustomerForm(request.POST)
        form_login = home_forms.SigninForm(request.POST)
        if request.POST.get("username"):
            if form_login.is_valid():
                username = request.POST.get("username")
                password = request.POST.get("password")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                return redirect(reverse("shop:checkout"))
            else:
                print("login form errors: ", form_login.errors)
        if form.is_valid():
            name = form.cleaned_data["name"]
            company = form.cleaned_data["company"]
            address = form.cleaned_data["address"]
            zipcode = form.cleaned_data["zipcode"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data["email"]
            description = form.cleaned_data["description"]

            cart = request.session.get("cart", {})
            shipping = 25000

            invoice_obj = models.Invoice(
                name=name,
                company=company,
                address=address,
                zipcode=zipcode,
                phone=phone,
                email=email,
                description=description,
            )
            invoice_obj.user = request.user if request.user.is_authenticated else None
            invoice_obj.count = len(cart["items"]) if "items" in cart else 0
            invoice_obj.sub_total = cart["total"] if "total" in cart else 0
            invoice_obj.shipping = shipping
            invoice_obj.save()
            invoice_obj.invoice_number = invoice_obj.pk + 1000
            invoice_obj.save()

            if "items" in cart:
                for item in cart["items"]:
                    product = models.Product.objects.get(pk=item["id"])
                    models.CartItem.objects.create(
                        title=item["title"],
                        count=item["count"],
                        price=item["price"],
                        total=item["total"],
                        product=product,
                        invoice=invoice_obj,
                    )

            payment_amount = invoice_obj.total
            payment_user = request.user if request.user.is_authenticated else None
            payment_obj = models.Payment(
                amount=payment_amount,
                status=models.Payment.STATUS_PENDING,
                user=payment_user,
                invoice=invoice_obj,
            )
            payment_obj.save()

            try:
                psp = Client("https://sandbox.zarinpal.com/pg/services/WebGate/wsdl")
                url = (
                    f"http://{str(get_current_site(request))}{reverse('shop:complete')}"
                )
                psp_result = psp.service.PaymentRequest(
                    MerchantID=settings.ZARINPAL_MID,
                    Amount=payment_amount,
                    Description=f"پرداخت فاکتور با شماره {invoice_obj.invoice_number}",
                    Email=email,
                    Mobile=phone,
                    CallbackURL=url,
                )
                if psp_result.Status == 100:
                    payment_obj.authority = psp_result.Authority
                    payment_obj.save()
                    return redirect(
                        f"https://sandbox.zarinpal.com/pg/StartPay/{psp_result.Authority}"
                    )
                else:
                    payment_obj.status = models.Payment.STATUS_FAILED
                    payment_obj.save()
                    return render(request, "error_500.html")
            except Exception as e:
                print("PSP exception: ", e)
                return render(request, "error_500.html")
        else:
            print("Checkout Errors: ", form.errors)
            if request.user.is_authenticated:
                form_customer = forms.CustomerForm(
                    initial={
                        "name": request.user.fullname or "",
                        "company": "",
                        "address": request.user.profile.address or "",
                        "zipcode": request.user.profile.zipcode or "",
                        "phone": request.user.phone or "",
                        "email": request.user.email or "",
                        "description": "",
                    }
                )
            else:
                form_customer = forms.CustomerForm()

            cart = request.session.get("cart", {})
            shipping = 25000
            total_invoice = shipping + cart["total"] if "total" in cart else 0

            # login form
            form_login = home_forms.SigninForm()

            # discount form
            form_discount = forms.DiscountForm()
            context = {
                "form_login": form_login,
                "form_discount": form_discount,
                "form_customer": form_customer,
                "cart": cart,
                "shipping": shipping,
                "total_invoice": total_invoice,
            }
            return render(request, "shop/shop_checkout.html", context)


class ShopCompleteView(View):
    def get(self, request):
        if request.GET.get("Status") == "OK":

            try:
                authority = request.GET.get("Authority")
                payment = models.Payment.objects.get(authority=authority)
                if payment.status == models.Payment.STATUS_SUCCESS:
                    return render(request, "shop/shop_alreadypaid.html")
                psp = Client("https://sandbox.zarinpal.com/pg/services/WebGate/wsdl")
                psp_result = psp.service.PaymentVerification(
                    MerchantID=settings.ZARINPAL_MID,
                    Authority=authority,
                    Amount=payment.amount,
                )

                if psp_result.Status == 100:
                    invoice = models.Invoice.objects.filter(
                        payment__authority=authority
                    ).first()
                    payment.status = models.Payment.STATUS_SUCCESS
                    payment.refid = psp_result.RefID
                    payment.save()
                    context = {"invoice": invoice, "refid": psp_result.RefID}
                    request.session["cart"] = {}
                    return render(request, "shop/shop_complete.html", context)
                elif psp_result.Status == 101:
                    return render(request, "shop/shop_alreadypaid.html")
                else:
                    payment.status = models.Payment.STATUS_FAILED
                    payment.save()
                    return render(request, "shop/shop_notpaid.html")
            except Exception as e:
                print("Error: ", e)
                raise Http404("Order with entered ref_id not found!")
        else:
            return render(request, "shop/shop_notpaid.html")
