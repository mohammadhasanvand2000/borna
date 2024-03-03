from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models.expressions import RawSQL
from django.conf import settings
import ghasedakpack, pyotp, jalali_date, jdatetime, time
from django.db.models import Sum, Count, Avg
from django.db.models.functions import (
    ExtractWeekDay,
    ExtractDay,
)
from datetime import datetime
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from zeep import Client
from . import forms
from . import models
from blog import models as blog_models
from shop import models as shop_models
from home import models as home_models

User = get_user_model()
sms = ghasedakpack.Ghasedak(settings.SECRET_SMS)
totp = pyotp.TOTP(pyotp.random_base32())


# mixins.py
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class DashboardUserProfileView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        profile = models.Profile.objects.get(user__exact=request.user)
        data = {
            "fullname": profile.user.fullname or "",
            "phone": profile.user.phone or "",
            "email": profile.user.email or "",
            "address": profile.address or "",
            "city": profile.city or "",
            "zipcode": profile.zipcode or "",
            "phone2": profile.phone or "",
            "pass1": "",
            "pass2": "",
        }
        form1 = forms.ProfileForm(initial=data)
        form2 = forms.ProfilePicForm(
            initial={"avatar": profile.avatar.url if profile.avatar else ""}
        )
        context = {"form": form1, "form_img": form2}
        return render(request, "dashboard/profile.html", context)

    def post(self, request):
        if "avatar" in request.FILES:
            form2 = forms.ProfilePicForm(request.POST, request.FILES)
            if form2.is_valid():
                user = request.user
                new_img = request.FILES.get("avatar")
                profile = models.Profile.objects.get(user=user)
                profile.avatar = new_img
                profile.save()
            return redirect("dashboard:profile")

        elif "fullname" in request.POST:
            post_data = request.POST.copy()
            post_data["phone"] = request.user.phone
            profile = models.Profile.objects.get(user__exact=request.user)
            form = forms.ProfileForm(post_data)
            form2 = forms.ProfilePicForm(
                initial={"avatar": profile.avatar.url if profile.avatar else ""}
            )
            context = {"form": form, "form_img": form2}
            if form.is_valid():
                fullname = form.cleaned_data["fullname"]
                phone = form.cleaned_data["phone"]
                email = form.cleaned_data["email"]
                address = form.cleaned_data["address"]
                city = form.cleaned_data["city"]
                zipcode = form.cleaned_data["zipcode"]
                phone2 = form.cleaned_data["phone2"]
                pass1 = form.cleaned_data["pass1"]
                pass2 = form.cleaned_data["pass2"]
                user = request.user

                user.fullname = fullname
                user.email = email
                if pass1:
                    user.set_password(pass1)
                user.save()

                models.Profile.objects.filter(user=user).update(
                    address=address, city=city, phone=phone2, zipcode=zipcode
                )

            else:
                print(form.errors)
                return render(request, "dashboard/profile.html", context)

        return redirect("dashboard:profile")


class DashboardUsersView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        if delete:
            User.objects.filter(pk=delete).delete()

        users = (
            User.objects.all()
            .order_by("date_joined")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(users, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        user_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"users": user_obj, "page_range": page_range, "paginator": paginator}
        return render(request, "dashboard/users.html", context)


class DashboardUsersAddView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = forms.UserAddForm()
        context = {"form": form}
        return render(request, "dashboard/users-edit.html", context)

    def post(self, request):
        form = forms.UserAddForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            fullname = form.cleaned_data["fullname"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            is_active = not (form.cleaned_data["is_active"])
            is_superuser = (
                True if form.cleaned_data["is_superuser"] == "admin" else False
            )
            user = None
            if password:
                try:
                    user = User.objects.filter(phone__exact=phone).first()
                    if user is None:
                        user = User(
                            fullname=fullname,
                            phone=phone,
                            email=email,
                            is_active=is_active,
                            is_superuser=is_superuser,
                            is_staff=is_superuser,
                        )
                        user.set_password(password)
                        user.save()
                        return redirect("dashboard:users")
                    else:
                        return redirect(
                            request,
                            "dashboard/users-edit.html",
                            {"form": forms.UserAddForm()},
                        )
                except Exception as e:
                    print(e)
                    return render(request, "dashboard/users-edit.html", context)
            else:
                return render(request, "dashboard/users-edit.html", context)
        else:
            return render(request, "dashboard/users-edit.html", context)


class DashboardUsersEditView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, uid):
        user = User.objects.filter(pk=uid).first()
        if user is not None:
            data = {
                "fullname": user.fullname or "",
                "phone": user.phone or "",
                "email": user.email or "",
                "password": "",
                "is_active": not (user.is_active),
                "is_superuser": "admin" if user.is_superuser else "user",
            }
            form = forms.UserAddForm(initial=data)
            context = {"form": form, "is_edit": True}
            return render(request, "dashboard/users-edit.html", context)
        else:
            raise Http404("Page not found!")

    def post(self, request, uid):
        form = forms.UserAddForm(request.POST)
        context = {"form": form, "is_edit": True}
        if form.is_valid():
            fullname = form.cleaned_data["fullname"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            is_active = not (form.cleaned_data["is_active"])
            is_superuser = (
                True if form.cleaned_data["is_superuser"] == "admin" else False
            )
            try:
                User.objects.filter(pk=uid).update(
                    fullname=fullname,
                    phone=phone,
                    email=email,
                    is_active=is_active,
                    is_superuser=is_superuser,
                    is_staff=is_superuser,
                )
                user = User.objects.get(pk=uid)
                if password:
                    user.set_password(password)
                user.save()
                return redirect("dashboard:users")
            except Exception as e:
                print(e)
                return render(request, "dashboard/users-edit.html", context)
        else:
            print(form.errors)
            return render(request, "dashboard/users-edit.html", context)


class DashboardCommentsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                blog_models.Comment.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                blog_models.Comment.objects.filter(pk=approve).update(is_approved=True)
            except:
                raise Http404("page not found!")

        if edit:
            try:
                comment = blog_models.Comment.objects.filter(pk=edit).first()
                form = forms.CommentEditForm(
                    initial={
                        "name": comment.name,
                        "email": comment.email,
                        "comment": comment.comment,
                    }
                )
                return render(request, "dashboard/comments-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        comments = (
            blog_models.Comment.objects.filter(is_approved=False)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"comments": comments, "is_su": True}
        return render(request, "dashboard/comments-list.html", context)

    def post(self, request):
        form = forms.CommentEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            comment = form.cleaned_data["comment"]
            try:
                cmid = request.GET.get("edit")
                blog_models.Comment.objects.filter(pk=cmid).update(
                    name=name, email=email, comment=comment, is_approved=True
                )

                return redirect(reverse("dashboard:comments"))
            except Exception as e:
                print(e)
                return render(request, "dashboard/comments-edit.html", {"form": form})
        else:
            return render(request, "dashboard/comments-edit.html", {"form": form})


class DashboardBlogCommentsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, post_id):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                blog_models.Comment.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                blog_models.Comment.objects.filter(pk=approve).update(is_approved=True)
            except:
                raise Http404("page not found!")

        if edit:
            try:
                comment = blog_models.Comment.objects.filter(pk=edit).first()
                form = forms.CommentEditForm(
                    initial={
                        "name": comment.name,
                        "email": comment.email,
                        "comment": comment.comment,
                    }
                )
                return render(request, "dashboard/comments-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        comments = (
            blog_models.Comment.objects.filter(post__pk=post_id)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"comments": comments, "is_blog": True}
        return render(request, "dashboard/comments-list.html", context)

    def post(self, request, post_id):
        form = forms.CommentEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            comment = form.cleaned_data["comment"]
            try:
                cmid = request.GET.get("edit")
                blog_models.Comment.objects.filter(pk=cmid).update(
                    name=name, email=email, comment=comment, is_approved=True
                )

                return redirect(
                    reverse("dashboard:blog-comments", kwargs={"post_id": post_id})
                )
            except Exception as e:
                print(e)
                return render(
                    request,
                    "dashboard/comments-edit.html",
                    {"form": form, "is_blog": True},
                )
        else:
            return render(
                request, "dashboard/comments-edit.html", {"form": form, "is_blog": True}
            )


class DashboardReviewsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                shop_models.Review.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                shop_models.Review.objects.filter(pk=approve).update(is_approved=True)
            except:
                raise Http404("page not found!")

        if edit:
            try:
                review = shop_models.Review.objects.filter(pk=edit).first()
                form = forms.ReviewEditForm(
                    initial={
                        "name": review.name,
                        "email": review.email,
                        "rate": review.rate,
                        "review": review.review,
                    }
                )
                return render(request, "dashboard/reviews-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        reviews = (
            shop_models.Review.objects.filter(is_approved=False)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"reviews": reviews, "is_su": True}
        return render(request, "dashboard/reviews-list.html", context)

    def post(self, request):
        form = forms.ReviewEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            rate = form.cleaned_data["rate"]
            review = form.cleaned_data["review"]
            try:
                rvid = request.GET.get("edit")
                shop_models.Review.objects.filter(pk=rvid).update(
                    name=name, email=email, rate=rate, review=review, is_approved=True
                )

                return redirect(reverse("dashboard:reviews"))
            except Exception as e:
                print(e)
                return render(request, "dashboard/reviews-edit.html", {"form": form})
        else:
            return render(request, "dashboard/reviews-edit.html", {"form": form})


class DashboardMainProdReviewsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                shop_models.ReviewProd.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                shop_models.ReviewProd.objects.filter(pk=approve).update(
                    is_approved=True
                )
            except:
                raise Http404("page not found!")

        if edit:
            try:
                review = shop_models.ReviewProd.objects.filter(pk=edit).first()
                form = forms.ReviewEditForm(
                    initial={
                        "name": review.name,
                        "email": review.email,
                        "rate": review.rate,
                        "review": review.review,
                    }
                )
                return render(request, "dashboard/reviews-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        reviews = (
            shop_models.ReviewProd.objects.filter(is_approved=False)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"reviews": reviews, "is_su": True}
        return render(request, "dashboard/reviews-list.html", context)

    def post(self, request):
        form = forms.ReviewEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            rate = form.cleaned_data["rate"]
            review = form.cleaned_data["review"]
            try:
                rvid = request.GET.get("edit")
                shop_models.ReviewProd.objects.filter(pk=rvid).update(
                    name=name, email=email, rate=rate, review=review, is_approved=True
                )

                return redirect(reverse("dashboard:prod-reviews"))
            except Exception as e:
                print(e)
                return render(request, "dashboard/reviews-edit.html", {"form": form})
        else:
            return render(request, "dashboard/reviews-edit.html", {"form": form})


class DashboardProdReviewsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, prod_id):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                shop_models.Review.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                shop_models.Review.objects.filter(pk=approve).update(is_approved=True)
            except:
                raise Http404("page not found!")

        if edit:
            try:
                review = shop_models.Review.objects.filter(pk=edit).first()
                form = forms.ReviewEditForm(
                    initial={
                        "name": review.name,
                        "email": review.email,
                        "rate": review.rate,
                        "review": review.review,
                    }
                )
                return render(request, "dashboard/reviews-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        reviews = (
            shop_models.Review.objects.filter(product__pk=prod_id)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"reviews": reviews, "is_prod": True}
        return render(request, "dashboard/reviews-list.html", context)

    def post(self, request, prod_id):
        form = forms.ReviewEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            rate = form.cleaned_data["rate"]
            review = form.cleaned_data["review"]
            try:
                rvid = request.GET.get("edit")
                shop_models.Review.objects.filter(pk=rvid).update(
                    name=name, email=email, rate=rate, review=review, is_approved=True
                )

                return redirect(
                    reverse("dashboard:shop-reviews", kwargs={"prod_id": prod_id})
                )
            except Exception as e:
                print(e)
                return render(
                    request,
                    "dashboard/reviews-edit.html",
                    {"form": form, "is_prod": True},
                )
        else:
            return render(
                request, "dashboard/reviews-edit.html", {"form": form, "is_prod": True}
            )


class DashboardProdProdReviewsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, prod_id):
        delete = request.GET.get("delete")
        approve = request.GET.get("approve")
        edit = request.GET.get("edit")

        if delete:
            try:
                shop_models.ReviewProd.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if approve:
            try:
                shop_models.ReviewProd.objects.filter(pk=approve).update(
                    is_approved=True
                )
            except:
                raise Http404("page not found!")

        if edit:
            try:
                review = shop_models.ReviewProd.objects.filter(pk=edit).first()
                form = forms.ReviewEditForm(
                    initial={
                        "name": review.name,
                        "email": review.email,
                        "rate": review.rate,
                        "review": review.review,
                    }
                )
                return render(request, "dashboard/reviews-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        reviews = (
            shop_models.ReviewProd.objects.filter(product__pk=prod_id)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"reviews": reviews, "is_prod": True}
        return render(request, "dashboard/reviews-list.html", context)

    def post(self, request, prod_id):
        form = forms.ReviewEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            rate = form.cleaned_data["rate"]
            review = form.cleaned_data["review"]
            try:
                rvid = request.GET.get("edit")
                shop_models.ReviewProd.objects.filter(pk=rvid).update(
                    name=name, email=email, rate=rate, review=review, is_approved=True
                )

                return redirect(
                    reverse("dashboard:prod-shop-reviews", kwargs={"prod_id": prod_id})
                )
            except Exception as e:
                print(e)
                return render(
                    request,
                    "dashboard/reviews-edit.html",
                    {"form": form, "is_prod": True},
                )
        else:
            return render(
                request, "dashboard/reviews-edit.html", {"form": form, "is_prod": True}
            )


class DashboardMessagesView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        view = request.GET.get("view")

        if delete:
            try:
                home_models.ContatcUs.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if view:
            try:
                message = home_models.ContatcUs.objects.filter(pk=view).first()
                home_models.ContatcUs.objects.filter(pk=view).update(is_seen=True)
                return render(
                    request, "dashboard/messages-view.html", {"message": message}
                )
            except:
                raise Http404("page not found!")

        messages = (
            home_models.ContatcUs.objects.filter(is_seen=False)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"messages": messages}
        return render(request, "dashboard/messages-list.html", context)


class DashboardShopCatView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        catid = request.GET.get("catid")
        delete = request.GET.get("delete")

        if catid:
            try:
                requested_cat = shop_models.Category.objects.get(pk=catid)
                form = forms.AddShopCatForm(
                    initial={
                        "title": requested_cat.title,
                        "description": requested_cat.description,
                        "parent": requested_cat.parent.pk
                        if requested_cat.parent
                        else None,
                    }
                )
            except:
                raise Http404(f"Product category with id {catid} not found!")
        else:
            form = forms.AddShopCatForm()

        if delete:
            shop_models.Category.objects.filter(pk=delete).delete()

        cats = (
            shop_models.Category.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/shop-cat.html", context)

    def post(self, request):
        form = forms.AddShopCatForm(request.POST)
        cats = (
            shop_models.Category.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            parent = form.cleaned_data["parent"]

            try:
                catid = request.GET.get("catid")
                if catid is None:
                    cat = shop_models.Category(
                        title=title,
                        description=description,
                        parent=parent,
                        user=request.user,
                    )
                    cat.save()
                else:
                    try:
                        updated_cat = shop_models.Category.objects.filter(pk=catid)
                        updated_cat.update(
                            title=title,
                            description=description,
                            parent=parent,
                            user=request.user,
                        )
                    except:
                        raise Http404(f"Product category with id {catid} not found!")
                return redirect("dashboard:shop-cat")
            except Exception as e:
                print(e)
                return render(request, "dashboard/shop-cat.html", context)
        else:
            return render(request, "dashboard/shop-cat.html", context)


class DashboardProdShopCatView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        catid = request.GET.get("catid")
        delete = request.GET.get("delete")

        if catid:
            try:
                requested_cat = shop_models.CategoryProd.objects.get(pk=catid)
                form = forms.AddProdShopCatForm(
                    initial={
                        "title": requested_cat.title,
                        "description": requested_cat.description,
                    }
                )
            except:
                raise Http404(f"Product category with id {catid} not found!")
        else:
            form = forms.AddProdShopCatForm()

        if delete:
            shop_models.CategoryProd.objects.filter(pk=delete).delete()

        cats = (
            shop_models.CategoryProd.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/shop-cat-prod.html", context)

    def post(self, request):
        form = forms.AddProdShopCatForm(request.POST)
        cats = (
            shop_models.CategoryProd.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]

            try:
                catid = request.GET.get("catid")
                if catid is None:
                    cat = shop_models.CategoryProd(
                        title=title,
                        description=description,
                        user=request.user,
                    )
                    cat.save()
                else:
                    try:
                        updated_cat = shop_models.CategoryProd.objects.filter(pk=catid)
                        updated_cat.update(
                            title=title,
                            description=description,
                            user=request.user,
                        )
                    except:
                        raise Http404(f"Product category with id {catid} not found!")
                return redirect("dashboard:prod-shop-cat")
            except Exception as e:
                print(e)
                return render(request, "dashboard/shop-cat-prod.html", context)
        else:
            return render(request, "dashboard/shop-cat-prod.html", context)


class DashboardBlogCatView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        catid = request.GET.get("catid")
        delete = request.GET.get("delete")
        if catid:
            try:
                requested_cat = blog_models.Category.objects.get(pk=catid)
                form = forms.AddBlogCatForm(
                    initial={
                        "title": requested_cat.title,
                        "description": requested_cat.description,
                        "parent": requested_cat.parent.pk
                        if requested_cat.parent
                        else None,
                    }
                )
            except:
                raise Http404(f"Blog category with id {catid} not found!")
        else:
            form = forms.AddBlogCatForm()

        if delete:
            blog_models.Category.objects.filter(pk=delete).delete()

        cats = (
            blog_models.Category.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/blog-cat.html", context)

    def post(self, request):
        form = forms.AddBlogCatForm(request.POST)
        cats = (
            blog_models.Category.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(cats, 10)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        cat_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "form": form,
            "cats": cat_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            parent = form.cleaned_data["parent"]

            try:
                catid = request.GET.get("catid")
                if catid is None:
                    cat = blog_models.Category(
                        title=title,
                        description=description,
                        parent=parent,
                        user=request.user,
                    )
                    cat.save()
                else:
                    try:
                        updated_cat = blog_models.Category.objects.filter(pk=catid)
                        updated_cat.update(
                            title=title,
                            description=description,
                            parent=parent,
                            user=request.user,
                        )
                    except:
                        raise Http404(f"Blog category with id {catid} not found!")
                return redirect("dashboard:blog-cat")
            except Exception as e:
                print(e)
                return render(request, "dashboard/blog-cat.html", context)
        else:
            return render(request, "dashboard/blog-cat.html", context)


class DashboardSurveyListView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        context = {}
        return render(request, "dashboard/survey-list.html", context)


class DashboardSurveyDetailView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request, survey_token):
        context = {}
        return render(request, "dashboard/survey-detail.html", context)


class DashboardSurveyView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        context = {}
        return render(request, "dashboard/survey.html", context)


class DashboardSMSView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = forms.SMSForm()
        context = {"form": form}
        return render(request, "dashboard/sms.html", context)

    def post(self, request):
        form = forms.SMSForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            numbers = form.cleaned_data["numbers"]
            another_time = form.cleaned_data["another_time"]
            date = form.cleaned_data["date"]
            my_time = form.cleaned_data["time"]
            text = form.cleaned_data["text"]
            if another_time:
                j_datetime = jdatetime.datetime(date.year, date.month, date.day)
                tehran_dt = f"{j_datetime.togregorian().strftime('%Y-%m-%d')}T{my_time.strftime('%H:%M')}"
                date_time = (
                    time.mktime(
                        timezone.datetime.strptime(
                            tehran_dt, "%Y-%m-%dT%H:%M"
                        ).timetuple()
                    )
                    - 12600
                )
            else:
                date_time = ""

            try:
                if another_time and (date is None or my_time is None):
                    raise Exception(
                        "Exception --> if check another_time you must enter a valid date or time!"
                    )
                sms.bulk1(
                    {
                        "message": text,
                        "receptor": numbers,
                        "linenumber": "3000278161",
                        "senddate": date_time if another_time else "",
                    }
                )
                return redirect("dashboard:sms")
            except Exception as e:
                print(e)
                return render(request, "dashboard/sms.html", context)
        else:
            return render(request, "dashboard/sms.html", context)


class DashboardBlogAddView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        postid = request.GET.get("postid")
        if postid:
            try:
                requested_post = blog_models.Post.objects.get(pk=postid)
                post_tags = [tag.name for tag in requested_post.tags.all()]
                form = forms.AddEditBlogForm(
                    initial={
                        "title": requested_post.title,
                        "description": requested_post.description,
                        "tags": "-".join(post_tags),
                        "content": requested_post.content,
                        "image_wide": None,
                        "image_cover": None,
                        "image_icon": None,
                        "category": requested_post.category.pk,
                    }
                )
            except:
                raise Http404(f"Post Item with id {postid} not found!")
        else:
            form = forms.AddEditBlogForm()
        context = {"form": form}
        return render(request, "dashboard/blog-add.html", context)

    def post(self, request):
        form = forms.AddEditBlogForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            content = form.cleaned_data["content"]
            tags = [tag.strip() for tag in form.cleaned_data["tags"].split("-")]
            image_wide = request.FILES.get("image_wide")
            image_cover = request.FILES.get("image_cover")
            image_icon = request.FILES.get("image_icon")
            category = form.cleaned_data["category"]
            try:
                postid = request.GET.get("postid")

                if postid is None:
                    post = blog_models.Post(
                        title=title,
                        description=description,
                        content=content,
                        image_wide=image_wide,
                        image_cover=image_cover,
                        image_icon=image_icon,
                        category=category,
                        user=request.user,
                    )
                    post.save()
                    for tag in tags:
                        post.tags.add(tag)
                    post.save()
                else:
                    try:
                        updated_post = blog_models.Post.objects.get(pk=postid)
                        updated_post.title = title
                        updated_post.description = description
                        updated_post.content = content
                        updated_post.category = category
                        updated_post.user = request.user
                        if image_wide:
                            updated_post.image_wide = image_wide
                        if image_cover:
                            updated_post.image_cover = image_cover
                        if image_icon:
                            updated_post.image_icon = image_icon

                        updated_post.save()
                        for tg in updated_post.tags.all():
                            tg.delete()
                        for tag in tags:
                            updated_post.tags.add(tag)
                        updated_post.save()
                    except Exception as e:
                        print(f"Error updating post: {e}")
                        raise Http404(f"Post with id {postid} not found!")
                return redirect("dashboard:blog-edit")
            except Exception as e:
                print(e)
                return render(request, "dashboard/blog-add.html", context)
        else:
            print(form.errors)
            return render(request, "dashboard/blog-add.html", context)


class DashboardShopAddView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        prodid = request.GET.get("prodid")
        if prodid:
            try:
                requested_prod = shop_models.Product.objects.get(pk=prodid)
                prod_tags = [tag.name for tag in requested_prod.tags.all()]
                form = forms.AddEditShopForm(
                    initial={
                        "title": requested_prod.title,
                        "video": requested_prod.video,
                        "description": requested_prod.description,
                        "tags": "-".join(prod_tags),
                        "content": requested_prod.content,
                        "price": requested_prod.price,
                        "discount": requested_prod.discount,
                        "disabled": requested_prod.disabled,
                        "amount": requested_prod.amount,
                        "image_cover": None,
                        "catalog1": None,
                        "catalog2": None,
                        "catalog3": None,
                        "category": requested_prod.category.pk,
                    }
                )
            except:
                raise Http404(f"Product Item with id {prodid} not found!")
        else:
            form = forms.AddEditShopForm()
        context = {"form": form}
        return render(request, "dashboard/shop-add.html", context)

    def post(self, request):
        form = forms.AddEditShopForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            title = form.cleaned_data["title"]
            video = form.cleaned_data["video"]
            description = form.cleaned_data["description"]
            content = form.cleaned_data["content"]
            tags = [tag.strip() for tag in form.cleaned_data["tags"].split("-")]
            image_cover = request.FILES.get("image_cover")
            catalog1 = request.FILES.get("catalog1")
            catalog2 = request.FILES.get("catalog2")
            catalog3 = request.FILES.get("catalog3")
            price = form.cleaned_data["price"]
            discount = form.cleaned_data["discount"]
            disabled = form.cleaned_data["disabled"]
            amount = form.cleaned_data["amount"]
            category = form.cleaned_data["category"]
            try:
                prodid = request.GET.get("prodid")

                if prodid is None:
                    prod = shop_models.Product(
                        title=title,
                        video=video,
                        description=description,
                        content=content,
                        image_cover=image_cover,
                        catalog1=catalog1,
                        catalog2=catalog2,
                        catalog3=catalog3,
                        price=price,
                        discount=discount,
                        disabled=disabled,
                        amount=amount,
                        category=category,
                        user=request.user,
                    )
                    prod.save()
                    for tag in tags:
                        prod.tags.add(tag)
                    prod.save()
                else:
                    try:
                        updated_prod = shop_models.Product.objects.get(pk=prodid)
                        updated_prod.title = title
                        updated_prod.description = description
                        updated_prod.video = video
                        updated_prod.content = content
                        updated_prod.price = price
                        updated_prod.discount = discount
                        updated_prod.disabled = disabled
                        updated_prod.amount = amount
                        updated_prod.category = category
                        updated_prod.user = request.user
                        if image_cover:
                            updated_prod.image_cover = image_cover
                        if catalog1:
                            updated_prod.catalog1 = catalog1
                        if catalog2:
                            updated_prod.catalog2 = catalog2
                        if catalog3:
                            updated_prod.catalog3 = catalog3
                        updated_prod.save()
                        for tg in updated_prod.tags.all():
                            tg.delete()
                        for tag in tags:
                            updated_prod.tags.add(tag)
                        updated_prod.save()
                    except Exception as e:
                        print(f"Error updating product: {e}")
                        raise Http404(f"Product with id {prodid} not found!")
                return redirect("dashboard:shop-edit")
            except Exception as e:
                print(e)
                return render(request, "dashboard/shop-add.html", context)
        else:
            print(form.errors)
            return render(request, "dashboard/shop-add.html", context)


class DashboardProdShopAddView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    def get(self, request):
        prodid = request.GET.get("prodid")
        if prodid:
            try:
                requested_prod = shop_models.ProductProd.objects.get(pk=prodid)
                prod_tags = [tag.name for tag in requested_prod.tags.all()]
                form = forms.AddEditProdShopForm(
                    initial={
                        "title": requested_prod.title,
                        "video": requested_prod.video,
                        "description": requested_prod.description,
                        "content": requested_prod.content,
                        "tags": "-".join(prod_tags),
                        "disabled": requested_prod.disabled,
                        "image_cover": None,
                        "catalog1": None,
                        "catalog2": None,
                        "catalog3": None,
                        "category": requested_prod.category.pk,
                        "maximum_thickness": requested_prod.maximum_thickness,
                        "wing_dimensions": requested_prod.wing_dimensions,
                        "longitudinal_movement": requested_prod.longitudinal_movement,
                        "pusher_engines": requested_prod.pusher_engines,
                        "pusher_gearboxes": requested_prod.pusher_gearboxes,
                        "power_transmission": requested_prod.power_transmission,
                        "high_pressure_gearbox": requested_prod.high_pressure_gearbox,
                        "high_pressure_engine": requested_prod.high_pressure_engine,
                        "drive_motor": requested_prod.drive_motor,
                        "mechanism_type": requested_prod.mechanism_type,
                        "cutting_milling_head_count": requested_prod.cutting_milling_head_count,
                        "worktable_dimensions": requested_prod.worktable_dimensions,
                        "total_weight": requested_prod.total_weight,
                        "operating_voltage": requested_prod.operating_voltage,
                        "axis_x_y_movement_system": requested_prod.axis_x_y_movement_system,
                        "axis_a_b_movement_system": requested_prod.axis_a_b_movement_system,
                        "axis_z_movement_system": requested_prod.axis_z_movement_system,
                        "rotary_axis_c": requested_prod.rotary_axis_c,
                        "z_axis_working_range": requested_prod.z_axis_working_range,
                        "x_y_axis_speed": requested_prod.x_y_axis_speed,
                        "z_axis_speed": requested_prod.z_axis_speed,
                        "spindle_type": requested_prod.spindle_type,
                        "power_transmission_system": requested_prod.power_transmission_system,
                        "drive_motor_type": requested_prod.drive_motor_type,
                        "jack_type": requested_prod.jack_type,
                        "gearbox_type": requested_prod.gearbox_type,
                        "rotary_gearboxes": requested_prod.rotary_gearboxes,
                        "height_control_system": requested_prod.height_control_system,
                        "machine_maximum_error": requested_prod.machine_maximum_error,
                        "controller_maximum_error": requested_prod.controller_maximum_error,
                        "cutting_milling_thickness_range": requested_prod.cutting_milling_thickness_range,
                        "spindle_distance_between_axes": requested_prod.spindle_distance_between_axes,
                        "maximum_rotary_part_opening_length": requested_prod.maximum_rotary_part_opening_length,
                        "maximum_disk_diameter": requested_prod.maximum_disk_diameter,
                        "plasma_installation_prerequisites": requested_prod.plasma_installation_prerequisites,
                        "maximum_laser_power": requested_prod.maximum_laser_power,
                        "laser_technology_type": requested_prod.laser_technology_type,
                        "machine_movement_accuracy": requested_prod.machine_movement_accuracy,
                        "drilling_accuracy": requested_prod.drilling_accuracy,
                        "cable_thickness_cable_length": requested_prod.cable_thickness_cable_length,
                        "water_pump_capacity": requested_prod.water_pump_capacity,
                        "water_collection_tank": requested_prod.water_collection_tank,
                        "glass_separation_system_after_cutting": requested_prod.glass_separation_system_after_cutting,
                        "glass_easy_movement_system": requested_prod.glass_easy_movement_system,
                        "pipe_boring_dimensions": requested_prod.pipe_boring_dimensions,
                        "controller_type": requested_prod.controller_type,
                        "g_code_reading_capability": requested_prod.g_code_reading_capability,
                        "electrical_panel": requested_prod.electrical_panel,
                        "computer_system": requested_prod.computer_system,
                        "uniform_spraying_material_reservoir": requested_prod.uniform_spraying_material_reservoir,
                        "abrasive_tank": requested_prod.abrasive_tank,
                        "abrasive_hopper": requested_prod.abrasive_hopper,
                        "waterjet_pump_power": requested_prod.waterjet_pump_power,
                    }
                )
            except:
                raise Http404(f"Product Item with id {prodid} not found!")
        else:
            form = forms.AddEditProdShopForm()
        context = {"form": form}
        return render(request, "dashboard/shop-add-prod.html", context)

    def post(self, request):
        form = forms.AddEditProdShopForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            title = form.cleaned_data["title"]
            video = form.cleaned_data["video"]
            description = form.cleaned_data["description"]
            content = form.cleaned_data["content"]
            tags = [tag.strip() for tag in form.cleaned_data["tags"].split("-")]
            image_cover = request.FILES.get("image_cover")
            catalog1 = request.FILES.get("catalog1")
            catalog2 = request.FILES.get("catalog2")
            catalog3 = request.FILES.get("catalog3")
            disabled = form.cleaned_data["disabled"]
            category = form.cleaned_data["category"]
            wing_dimensions = form.cleaned_data.get("wing_dimensions")
            maximum_thickness = form.cleaned_data.get("maximum_thickness")
            longitudinal_movement = form.cleaned_data.get("longitudinal_movement")
            pusher_engines = form.cleaned_data.get("pusher_engines")
            pusher_gearboxes = form.cleaned_data.get("pusher_gearboxes")
            power_transmission = form.cleaned_data.get("power_transmission")
            high_pressure_gearbox = form.cleaned_data.get("high_pressure_gearbox")
            high_pressure_engine = form.cleaned_data.get("high_pressure_engine")
            drive_motor = form.cleaned_data.get("drive_motor")
            mechanism_type = form.cleaned_data.get("mechanism_type")
            cutting_milling_head_count = form.cleaned_data.get("cutting_milling_head_count")
            worktable_dimensions = form.cleaned_data.get("worktable_dimensions")
            total_weight = form.cleaned_data.get("total_weight")
            operating_voltage = form.cleaned_data.get("operating_voltage")
            axis_x_y_movement_system = form.cleaned_data.get("axis_x_y_movement_system")
            axis_a_b_movement_system = form.cleaned_data.get("axis_a_b_movement_system")
            axis_z_movement_system = form.cleaned_data.get("axis_z_movement_system")
            rotary_axis_c = form.cleaned_data.get("rotary_axis_c")
            z_axis_working_range = form.cleaned_data.get("z_axis_working_range")
            x_y_axis_speed = form.cleaned_data.get("x_y_axis_speed")
            z_axis_speed = form.cleaned_data.get("z_axis_speed")
            spindle_type = form.cleaned_data.get("spindle_type")
            power_transmission_system = form.cleaned_data.get("power_transmission_system")
            drive_motor_type = form.cleaned_data.get("drive_motor_type")
            jack_type = form.cleaned_data.get("jack_type")
            gearbox_type = form.cleaned_data.get("gearbox_type")
            rotary_gearboxes = form.cleaned_data.get("rotary_gearboxes")
            height_control_system = form.cleaned_data.get("height_control_system")
            machine_maximum_error = form.cleaned_data.get("machine_maximum_error")
            controller_maximum_error = form.cleaned_data.get("controller_maximum_error")
            cutting_milling_thickness_range = form.cleaned_data.get("cutting_milling_thickness_range")
            spindle_distance_between_axes = form.cleaned_data.get("spindle_distance_between_axes")
            maximum_rotary_part_opening_length = form.cleaned_data.get("maximum_rotary_part_opening_length")
            maximum_disk_diameter = form.cleaned_data.get("maximum_disk_diameter")
            plasma_installation_prerequisites = form.cleaned_data.get("plasma_installation_prerequisites")
            maximum_laser_power = form.cleaned_data.get("maximum_laser_power")
            laser_technology_type = form.cleaned_data.get("laser_technology_type")
            machine_movement_accuracy = form.cleaned_data.get("machine_movement_accuracy")
            drilling_accuracy = form.cleaned_data.get("drilling_accuracy")
            cable_thickness_cable_length = form.cleaned_data.get("cable_thickness_cable_length")
            water_pump_capacity = form.cleaned_data.get("water_pump_capacity")
            water_collection_tank = form.cleaned_data.get("water_collection_tank")
            glass_separation_system_after_cutting = form.cleaned_data.get("glass_separation_system_after_cutting")
            glass_easy_movement_system = form.cleaned_data.get("glass_easy_movement_system")
            pipe_boring_dimensions = form.cleaned_data.get("pipe_boring_dimensions")
            controller_type = form.cleaned_data.get("controller_type")
            g_code_reading_capability = form.cleaned_data.get("g_code_reading_capability")
            electrical_panel = form.cleaned_data.get("electrical_panel")
            computer_system = form.cleaned_data.get("computer_system")
            uniform_spraying_material_reservoir = form.cleaned_data.get("uniform_spraying_material_reservoir")
            abrasive_tank = form.cleaned_data.get("abrasive_tank")
            abrasive_hopper = form.cleaned_data.get("abrasive_hopper")
            waterjet_pump_power = form.cleaned_data.get("waterjet_pump_power")
            try:
                prodid = request.GET.get("prodid")

                if prodid is None:
                    prod = shop_models.ProductProd(
                        title=title,
                        video=video,
                        description=description,
                        content=content,
                        image_cover=image_cover,
                        catalog1=catalog1,
                        catalog2=catalog2,
                        catalog3=catalog3,
                        disabled=disabled,
                        category=category,
                        wing_dimensions=wing_dimensions,
                        maximum_thickness=maximum_thickness,
                        longitudinal_movement=longitudinal_movement,
                        pusher_engines=pusher_engines,
                        pusher_gearboxes=pusher_gearboxes,
                        power_transmission=power_transmission,
                        high_pressure_gearbox=high_pressure_gearbox,
                        high_pressure_engine=high_pressure_engine,
                        drive_motor=drive_motor,
                        mechanism_type=mechanism_type,
                        cutting_milling_head_count=cutting_milling_head_count,
                        worktable_dimensions=worktable_dimensions,
                        total_weight=total_weight,
                        operating_voltage=operating_voltage,
                        axis_x_y_movement_system=axis_x_y_movement_system,
                        axis_a_b_movement_system=axis_a_b_movement_system,
                        axis_z_movement_system=axis_z_movement_system,
                        rotary_axis_c=rotary_axis_c,
                        z_axis_working_range=z_axis_working_range,
                        x_y_axis_speed=x_y_axis_speed,
                        z_axis_speed=z_axis_speed,
                        spindle_type=spindle_type,
                        power_transmission_system=power_transmission_system,
                        drive_motor_type=drive_motor_type,
                        jack_type=jack_type,
                        gearbox_type=gearbox_type,
                        rotary_gearboxes=rotary_gearboxes,
                        height_control_system=height_control_system,
                        machine_maximum_error=machine_maximum_error,
                        controller_maximum_error=controller_maximum_error,
                        cutting_milling_thickness_range=cutting_milling_thickness_range,
                        spindle_distance_between_axes=spindle_distance_between_axes,
                        maximum_rotary_part_opening_length=maximum_rotary_part_opening_length,
                        maximum_disk_diameter=maximum_disk_diameter,
                        plasma_installation_prerequisites=plasma_installation_prerequisites,
                        maximum_laser_power=maximum_laser_power,
                        laser_technology_type=laser_technology_type,
                        machine_movement_accuracy=machine_movement_accuracy,
                        drilling_accuracy=drilling_accuracy,
                        cable_thickness_cable_length=cable_thickness_cable_length,
                        water_pump_capacity=water_pump_capacity,
                        water_collection_tank=water_collection_tank,
                        glass_separation_system_after_cutting=glass_separation_system_after_cutting,
                        glass_easy_movement_system=glass_easy_movement_system,
                        pipe_boring_dimensions=pipe_boring_dimensions,
                        controller_type=controller_type,
                        g_code_reading_capability=g_code_reading_capability,
                        electrical_panel=electrical_panel,
                        computer_system=computer_system,
                        uniform_spraying_material_reservoir=uniform_spraying_material_reservoir,
                        abrasive_tank=abrasive_tank,
                        abrasive_hopper=abrasive_hopper,
                        waterjet_pump_power=waterjet_pump_power,
                        user=request.user,
                    )
                    prod.save()
                    for tag in tags:
                        prod.tags.add(tag)
                    prod.save()
                else:
                    try:
                        updated_prod = shop_models.ProductProd.objects.get(pk=prodid)
                        updated_prod.title = title
                        updated_prod.video = video
                        updated_prod.description = description
                        updated_prod.content = content
                        updated_prod.disabled = disabled
                        updated_prod.category = category
                        updated_prod.wing_dimensions = wing_dimensions
                        updated_prod.maximum_thickness = maximum_thickness
                        updated_prod.longitudinal_movement = longitudinal_movement
                        updated_prod.pusher_engines = pusher_engines
                        updated_prod.pusher_gearboxes = pusher_gearboxes
                        updated_prod.power_transmission = power_transmission
                        updated_prod.high_pressure_gearbox = high_pressure_gearbox
                        updated_prod.high_pressure_engine = high_pressure_engine
                        updated_prod.drive_motor = drive_motor
                        updated_prod.mechanism_type = mechanism_type
                        updated_prod.cutting_milling_head_count = cutting_milling_head_count
                        updated_prod.worktable_dimensions = worktable_dimensions
                        updated_prod.total_weight = total_weight
                        updated_prod.operating_voltage = operating_voltage
                        updated_prod.axis_x_y_movement_system = axis_x_y_movement_system
                        updated_prod.axis_a_b_movement_system = axis_a_b_movement_system
                        updated_prod.axis_z_movement_system = axis_z_movement_system
                        updated_prod.rotary_axis_c = rotary_axis_c
                        updated_prod.z_axis_working_range = z_axis_working_range
                        updated_prod.x_y_axis_speed = x_y_axis_speed
                        updated_prod.z_axis_speed = z_axis_speed
                        updated_prod.spindle_type = spindle_type
                        updated_prod.power_transmission_system = power_transmission_system
                        updated_prod.drive_motor_type = drive_motor_type
                        updated_prod.jack_type = jack_type
                        updated_prod.gearbox_type = gearbox_type
                        updated_prod.rotary_gearboxes = rotary_gearboxes
                        updated_prod.height_control_system = height_control_system
                        updated_prod.machine_maximum_error = machine_maximum_error
                        updated_prod.controller_maximum_error = controller_maximum_error
                        updated_prod.cutting_milling_thickness_range = cutting_milling_thickness_range
                        updated_prod.spindle_distance_between_axes = spindle_distance_between_axes
                        updated_prod.maximum_rotary_part_opening_length = maximum_rotary_part_opening_length
                        updated_prod.maximum_disk_diameter = maximum_disk_diameter
                        updated_prod.plasma_installation_prerequisites = plasma_installation_prerequisites
                        updated_prod.maximum_laser_power = maximum_laser_power
                        updated_prod.laser_technology_type = laser_technology_type
                        updated_prod.machine_movement_accuracy = machine_movement_accuracy
                        updated_prod.drilling_accuracy = drilling_accuracy
                        updated_prod.cable_thickness_cable_length = cable_thickness_cable_length
                        updated_prod.water_pump_capacity = water_pump_capacity
                        updated_prod.water_collection_tank = water_collection_tank
                        updated_prod.glass_separation_system_after_cutting = glass_separation_system_after_cutting
                        updated_prod.glass_easy_movement_system = glass_easy_movement_system
                        updated_prod.pipe_boring_dimensions = pipe_boring_dimensions
                        updated_prod.controller_type = controller_type
                        updated_prod.g_code_reading_capability = g_code_reading_capability
                        updated_prod.electrical_panel = electrical_panel
                        updated_prod.computer_system = computer_system
                        updated_prod.uniform_spraying_material_reservoir = uniform_spraying_material_reservoir
                        updated_prod.abrasive_tank = abrasive_tank
                        updated_prod.abrasive_hopper = abrasive_hopper
                        updated_prod.waterjet_pump_power = waterjet_pump_power
                        updated_prod.user = request.user
                       
                        if image_cover:
                            updated_prod.image_cover = image_cover
                        if catalog1:
                            updated_prod.catalog1 = catalog1
                        if catalog2:
                            updated_prod.catalog2 = catalog2
                        if catalog3:
                            updated_prod.catalog3 = catalog3
                        updated_prod.save()
                        for tg in updated_prod.tags.all():
                            tg.delete()
                        for tag in tags:
                            updated_prod.tags.add(tag)
                        updated_prod.save()
                    except Exception as e:
                        print(f"Error updating product: {e}")
                        raise Http404(f"Product with id {prodid} not found!")
                return redirect("dashboard:prod-shop-edit")
            except Exception as e:
                print(e)
                return render(request, "dashboard/shop-add-prod.html", context)
        else:
            print(form.errors)
            return render(request, "dashboard/shop-add-prod.html", context)


class DashboardBlogEditView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        posts = blog_models.Post.objects.all().order_by("-date_created")
        paginator = Paginator(posts, 10)  # Show 10 per page.
        page_number = request.GET.get("page", 1)
        post_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"posts": post_obj, "page_range": page_range, "paginator": paginator}
        return render(request, "dashboard/blog-edit.html", context)


class DashboardBlogDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        postid = request.GET.get("postid")
        if postid:
            try:
                blog_models.Post.objects.filter(pk=postid).delete()
            except Exception as e:
                print(e)
        return redirect("dashboard:blog-edit")


class DashboardShopEditView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        prods = shop_models.Product.objects.all().order_by("-date_created")
        paginator = Paginator(prods, 10)  # Show 10 per page.
        page_number = request.GET.get("page", 1)
        prod_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"prods": prod_obj, "page_range": page_range, "paginator": paginator}
        return render(request, "dashboard/shop-edit.html", context)


class DashboardProdShopEditView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        prods = shop_models.ProductProd.objects.all().order_by("-date_created")
        paginator = Paginator(prods, 10)  # Show 10 per page.
        page_number = request.GET.get("page", 1)
        prod_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"prods": prod_obj, "page_range": page_range, "paginator": paginator}
        return render(request, "dashboard/shop-edit-prod.html", context)


class DashboardShopDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        prodid = request.GET.get("prodid")
        if prodid:
            try:
                shop_models.Product.objects.filter(pk=prodid).delete()
            except Exception as e:
                print(e)
        return redirect("dashboard:shop-edit")


class DashboardProdShopDeleteView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        prodid = request.GET.get("prodid")
        if prodid:
            try:
                shop_models.ProductProd.objects.filter(pk=prodid).delete()
            except Exception as e:
                print(e)
        return redirect("dashboard:prod-shop-edit")


class DashboardProductImagesView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, prod_id):
        form = forms.ProductImagesForm()
        context = {"form": form}
        return render(request, "dashboard/shop-images.html", context)

    def post(self, request, prod_id):
        form = forms.ProductImagesForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            pics = [
                request.FILES.get("pic1"),
                request.FILES.get("pic2"),
                request.FILES.get("pic3"),
                request.FILES.get("pic4"),
                request.FILES.get("pic5"),
            ]
            try:
                requested_prod = shop_models.Product.objects.filter(pk=prod_id).first()
                prod_images = shop_models.ProductImages.objects.filter(
                    product=requested_prod
                ).order_by("-id")
                for i in range(0, 5):
                    if pics[i]:
                        if i < len(prod_images):
                            prod_images[i].image = pics[i]
                            prod_images[i].save()
                        else:
                            shop_models.ProductImages.objects.create(
                                product=requested_prod, user=request.user, image=pics[i]
                            )
                return redirect(reverse("dashboard:shop-edit"))
            except Exception as e:
                print(f"Error updating images: {e}")
                return render(request, "dashboard/shop-images.html", context)


class DashboardProdProductImagesView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, prod_id):
        form = forms.ProductImagesForm()
        context = {"form": form}
        return render(request, "dashboard/shop-images.html", context)

    def post(self, request, prod_id):
        form = forms.ProductImagesForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            pics = [
                request.FILES.get("pic1"),
                request.FILES.get("pic2"),
                request.FILES.get("pic3"),
                request.FILES.get("pic4"),
                request.FILES.get("pic5"),
            ]
            try:
                requested_prod = shop_models.ProductProd.objects.filter(
                    pk=prod_id
                ).first()
                prod_images = shop_models.ProductImagesProd.objects.filter(
                    product=requested_prod
                ).order_by("-id")
                for i in range(0, 5):
                    if pics[i]:
                        if i < len(prod_images):
                            prod_images[i].image = pics[i]
                            prod_images[i].save()
                        else:
                            shop_models.ProductImagesProd.objects.create(
                                product=requested_prod, user=request.user, image=pics[i]
                            )
                return redirect(reverse("dashboard:prod-shop-edit"))
            except Exception as e:
                print(f"Error updating images: {e}")
                return render(request, "dashboard/shop-images.html", context)


class DashboardSliderContentView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        edit = request.GET.get("edit")

        if delete:
            try:
                home_models.SliderContent.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if edit:
            try:
                slider = home_models.SliderContent.objects.filter(pk=edit).first()
                form = forms.SliderContentForm(
                    initial={
                        "small_title": slider.small_title,
                        "big_title": slider.big_title,
                        "description": slider.description,
                        "cta_title": slider.cta_title,
                        "cta_link": slider.cta_link,
                        "image": None,
                    }
                )
                return render(
                    request,
                    "dashboard/slider-content.html",
                    {"form": form, "is_edit": True},
                )
            except:
                raise Http404("page not found!")

        sliders = (
            home_models.SliderContent.objects.all()
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"sliders": sliders}
        return render(request, "dashboard/slider-list.html", context)

    def post(self, request):
        form = forms.SliderContentForm(request.POST, request.FILES)
        if form.is_valid():
            small_title = form.cleaned_data["small_title"]
            big_title = form.cleaned_data["big_title"]
            description = form.cleaned_data["description"]
            cta_title = form.cleaned_data["cta_title"]
            cta_link = form.cleaned_data["cta_link"]
            image = request.FILES.get("image")
            try:
                slid = request.GET.get("edit")
                requested_slider = home_models.SliderContent.objects.filter(
                    pk=slid
                ).first()
                home_models.SliderContent.objects.filter(pk=slid).update(
                    small_title=small_title,
                    big_title=big_title,
                    description=description,
                    cta_title=cta_title,
                    cta_link=cta_link,
                )
                if image:
                    requested_slider.image = image
                    requested_slider.save()

                return redirect(reverse("dashboard:slider"))
            except Exception as e:
                print(e)
                return render(
                    request,
                    "dashboard/slider-content.html",
                    {"form": form, "is_edit": True},
                )
        else:
            return render(
                request,
                "dashboard/slider-content.html",
                {"form": form, "is_edit": True},
            )


class DashboardSliderAddView(LoginRequiredMixin, SuperuserRequiredMixin, View):

    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        form = forms.SliderContentForm()
        context = {"form": form}
        return render(request, "dashboard/slider-content.html", context)

    def post(self, request):
        form = forms.SliderContentForm(request.POST, request.FILES)
        context = {"form": form}
        if form.is_valid():
            small_title = form.cleaned_data["small_title"]
            big_title = form.cleaned_data["big_title"]
            description = form.cleaned_data["description"]
            cta_title = form.cleaned_data["cta_title"]
            cta_link = form.cleaned_data["cta_link"]
            image = request.FILES.get("image")

            try:
                slider = home_models.SliderContent.objects.create(
                    small_title=small_title,
                    big_title=big_title,
                    description=description,
                    cta_title=cta_title,
                    cta_link=cta_link,
                )
                slider.image = image
                slider.save()
                return redirect("dashboard:slider")
            except:
                return render(request, "dashboard/slider-content.html", context)

        else:
            return render(request, "dashboard/slider-content.html", context)


# ordinart user permissions
class DashboardUserCommentsView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        delete = request.GET.get("delete")
        edit = request.GET.get("edit")

        if delete:
            try:
                blog_models.Comment.objects.filter(pk=delete).delete()
            except:
                raise Http404("page not found!")

        if edit:
            try:
                comment = blog_models.Comment.objects.filter(pk=edit).first()
                form = forms.CommentEditForm(
                    initial={
                        "name": comment.name,
                        "email": comment.email,
                        "comment": comment.comment,
                    }
                )
                return render(request, "dashboard/comments-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        comments = (
            blog_models.Comment.objects.filter(user=request.user)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"comments": comments}
        return render(request, "dashboard/comments-list.html", context)

    def post(self, request):
        form = forms.CommentEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            comment = form.cleaned_data["comment"]
            try:
                cmid = request.GET.get("edit")
                blog_models.Comment.objects.filter(pk=cmid).update(
                    name=name, email=email, comment=comment, is_approved=False
                )

                return redirect(reverse("dashboard:user-comments"))
            except Exception as e:
                print(e)
                return render(request, "dashboard/comments-edit.html", {"form": form})
        else:
            return render(request, "dashboard/comments-edit.html", {"form": form})


class DashboardUserReviewsView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        flag = request.GET.get("flag")
        delete = request.GET.get("delete")
        edit = request.GET.get("edit")

        if delete:
            try:
                shop_models.Review.objects.filter(
                    pk=delete
                ).delete() if flag == "1" else shop_models.ReviewProd.objects.filter(
                    pk=delete
                ).delete()
            except:
                raise Http404("page not found!")

        if edit:
            try:
                review = (
                    shop_models.Review.objects.filter(pk=edit).first()
                    if flag == "1"
                    else shop_models.ReviewProd.objects.filter(pk=edit).first()
                )
                form = forms.ReviewEditForm(
                    initial={
                        "name": review.name,
                        "email": review.email,
                        "rate": review.rate,
                        "review": review.review,
                    }
                )
                return render(request, "dashboard/reviews-edit.html", {"form": form})
            except:
                raise Http404("page not found!")

        reviews_main = (
            shop_models.ReviewProd.objects.filter(user=request.user)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        reviews_shop = (
            shop_models.Review.objects.filter(user=request.user)
            .order_by("date_created")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        context = {"reviews_main": reviews_main, "reviews_shop": reviews_shop}
        return render(request, "dashboard/reviews-list-user.html", context)

    def post(self, request):
        form = forms.ReviewEditForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            rate = form.cleaned_data["rate"]
            review = form.cleaned_data["review"]
            try:
                rvid = request.GET.get("edit")
                flag = request.GET.get("flag")

                shop_models.Review.objects.filter(pk=rvid).update(
                    name=name, email=email, rate=rate, review=review, is_approved=False
                ) if flag == "1" else shop_models.ReviewProd.objects.filter(
                    pk=rvid
                ).update(
                    name=name, email=email, rate=rate, review=review, is_approved=False
                )

                return redirect(reverse("dashboard:user-reviews"))
            except Exception as e:
                print(e)
                return render(request, "dashboard/reviews-edit.html", {"form": form})
        else:
            return render(request, "dashboard/reviews-edit.html", {"form": form})


class DashboardOrdersView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        orders = (
            shop_models.Invoice.objects.filter(
                payment__status=shop_models.Payment.STATUS_SUCCESS
            )
            .order_by("-payment__date_modified")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(orders, 10)
        page_number = request.GET.get("page", 1)
        orders_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "orders": orders_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/fin_orders.html", context)


class DashboardOrderDetailView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request, invoice_num):
        order = shop_models.Invoice.objects.filter(invoice_number=invoice_num).first()
        context = {"order": order}
        return render(request, "dashboard/fin_order_view.html", context)


class DashboardTransactionsView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        transactions = (
            shop_models.Payment.objects.all()
            .order_by("-date_modified")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(transactions, 10)
        page_number = request.GET.get("page", 1)
        transactions = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "transactions": transactions,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/fin_transactions.html", context)


class PaymentAgainView(LoginRequiredMixin, View):
    def get(self, request, invoice_num):
        psp = Client("https://sandbox.zarinpal.com/pg/services/WebGate/wsdl")
        url = f"http://{str(get_current_site(request))}{reverse('shop:complete')}"
        payment = shop_models.Payment.objects.filter(
            invoice__invoice_number=invoice_num
        ).first()
        psp_result = psp.service.PaymentRequest(
            MerchantID=settings.ZARINPAL_MID,
            Amount=payment.amount,
            Description=f"پرداخت فاکتور با شماره {payment.invoice.invoice_number}",
            Email=payment.invoice.email,
            Mobile=payment.invoice.phone,
            CallbackURL=url,
        )
        if psp_result.Status == 100:
            payment.authority = psp_result.Authority
            payment.save()
            return redirect(
                f"https://sandbox.zarinpal.com/pg/StartPay/{psp_result.Authority}"
            )
        else:
            payment.status = shop_models.Payment.STATUS_FAILED
            payment.save()
            return render(request, "error_500.html")


class DashboardUserOrdersView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        orders = (
            shop_models.Invoice.objects.filter(
                payment__status=shop_models.Payment.STATUS_SUCCESS, user=request.user
            )
            .order_by("-payment__date_modified")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(orders, 10)
        page_number = request.GET.get("page", 1)
        orders_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "orders": orders_obj,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/fin_orders.html", context)


class DashboardUserTransactionsView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        transactions = (
            shop_models.Payment.objects.filter(user=request.user)
            .order_by("-date_modified")
            .annotate(row_num=RawSQL("row_number() over ()", []))
        )
        paginator = Paginator(transactions, 10)
        page_number = request.GET.get("page", 1)
        transactions = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {
            "transactions": transactions,
            "page_range": page_range,
            "paginator": paginator,
        }
        return render(request, "dashboard/fin_transactions.html", context)


class DashboardHomeView(LoginRequiredMixin, SuperuserRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        week = shop_models.Payment.objects.filter(
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=7),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))
        month = shop_models.Payment.objects.filter(
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=30),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))
        year = shop_models.Payment.objects.filter(
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=365),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))

        weekly = (
            shop_models.Payment.objects.filter(
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=7),
                    timezone.now(),
                ],
            )
            .annotate(
                weekday=ExtractWeekDay("date_modified"),
            )
            .values(
                "weekday",
            )
            .annotate(price=Sum("amount"), count=Count("amount"))
            .values("weekday", "price", "count")
        )

        month3 = (
            shop_models.Payment.objects.filter(
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=90),
                    timezone.now(),
                ],
            )
            .aggregate(Sum("amount"))
        )

        monthly = (
            shop_models.Payment.objects.filter(
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=31),
                    timezone.now(),
                ],
            )
            .annotate(
                day=ExtractDay("date_modified"),
            )
            .values(
                "day",
            )
            .annotate(price=Sum("amount"))
            .values("day", "price")
        )
        weekly_price = [0] * 7
        weekly_count = [0] * 7
        month3_avg = [round(month3["amount__sum"]/90000)*1000]* 31 if month3["amount__sum"] else 0
        month_price = [0]* 31

        for day in weekly:
            weekly_price[day["weekday"] - 1] = day["price"]
            weekly_count[day["weekday"] - 1] = day["count"]
        for day in monthly:
            month_price[day["day"] - 1] = day["price"]
        
        weekly_fprice = [
            ["شنبه", weekly_price[6]],
            ["یکشنبه", weekly_price[0]],
            ["دوشنبه", weekly_price[1]],
            ["سه‌شنبه", weekly_price[2]],
            ["چهارشنبه", weekly_price[3]],
            ["پنج‌شنبه", weekly_price[4]],
            ["جمعه", weekly_price[5]],
        ]
        weekly_fcount = [
            ["شنبه", weekly_count[6]],
            ["یکشنبه", weekly_count[0]],
            ["دوشنبه", weekly_count[1]],
            ["سه‌شنبه", weekly_count[2]],
            ["چهارشنبه", weekly_count[3]],
            ["پنج‌شنبه", weekly_count[4]],
            ["جمعه", weekly_count[5]],
        ]
        context = {
            "week": week.get("amount__sum") if week.get("amount__sum") else 0,
            "month": month.get("amount__sum") if month.get("amount__sum") else 0,
            "year": year.get("amount__sum") if year.get("amount__sum") else 0,
            "weekly_price": weekly_fprice,
            "weekly_count": weekly_fcount,
            "month3_avg": month3_avg,
            "month_price":month_price
        }
        return render(request, "dashboard/index.html", context)



class DashboardUserHomeView(LoginRequiredMixin, View):
    login_url = "/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        week = shop_models.Payment.objects.filter(
            user=request.user,
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=7),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))
        month = shop_models.Payment.objects.filter(
            user=request.user,
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=30),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))
        year = shop_models.Payment.objects.filter(
            user=request.user,
            status=shop_models.Payment.STATUS_SUCCESS,
            date_modified__range=[
                timezone.now() - timezone.timedelta(days=365),
                timezone.now(),
            ],
        ).aggregate(Sum("amount"))

        weekly = (
            shop_models.Payment.objects.filter(
                user=request.user,
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=7),
                    timezone.now(),
                ],
            )
            .annotate(
                weekday=ExtractWeekDay("date_modified"),
            )
            .values(
                "weekday",
            )
            .annotate(price=Sum("amount"), count=Count("amount"))
            .values("weekday", "price", "count")
        )

        month3 = (
            shop_models.Payment.objects.filter(
                user=request.user,
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=90),
                    timezone.now(),
                ],
            )
            .aggregate(Sum("amount"))
        )

        monthly = (
            shop_models.Payment.objects.filter(
                user=request.user,
                status=shop_models.Payment.STATUS_SUCCESS,
                date_modified__range=[
                    timezone.now() - timezone.timedelta(days=31),
                    timezone.now(),
                ],
            )
            .annotate(
                day=ExtractDay("date_modified"),
            )
            .values(
                "day",
            )
            .annotate(price=Sum("amount"))
            .values("day", "price")
        )
        weekly_price = [0] * 7
        weekly_count = [0] * 7
        month3_avg = [round(month3["amount__sum"]/90000)*1000]* 31 if month3["amount__sum"] else 0
        month_price = [0]* 31

        for day in weekly:
            weekly_price[day["weekday"] - 1] = day["price"]
            weekly_count[day["weekday"] - 1] = day["count"]
        for day in monthly:
            month_price[day["day"] - 1] = day["price"]
        
        weekly_fprice = [
            ["شنبه", weekly_price[6]],
            ["یکشنبه", weekly_price[0]],
            ["دوشنبه", weekly_price[1]],
            ["سه‌شنبه", weekly_price[2]],
            ["چهارشنبه", weekly_price[3]],
            ["پنج‌شنبه", weekly_price[4]],
            ["جمعه", weekly_price[5]],
        ]
        weekly_fcount = [
            ["شنبه", weekly_count[6]],
            ["یکشنبه", weekly_count[0]],
            ["دوشنبه", weekly_count[1]],
            ["سه‌شنبه", weekly_count[2]],
            ["چهارشنبه", weekly_count[3]],
            ["پنج‌شنبه", weekly_count[4]],
            ["جمعه", weekly_count[5]],
        ]
        context = {
            "week": week.get("amount__sum") if week.get("amount__sum") else 0,
            "month": month.get("amount__sum") if month.get("amount__sum") else 0,
            "year": year.get("amount__sum") if year.get("amount__sum") else 0,
            "weekly_price": weekly_fprice,
            "weekly_count": weekly_fcount,
            "month3_avg": month3_avg,
            "month_price":month_price
        }
        return render(request, "dashboard/index.html", context)
