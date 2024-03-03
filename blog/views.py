from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import ExpressionWrapper, IntegerField, Count, Q, F, Subquery
from . import models
from . import forms
from taggit import models as tag_model

class TagListView(View):
    
    def get(self, request, tag_slug=None):
        tags = None
        posts=[]
        if tag_slug:
            tags = tag_model.Tag.objects.filter(slug=tag_slug)
            posts = models.Post.objects.filter(tags__in=tags)
       
        paginator = Paginator(posts, 9)  # Show 25 user per page.
        page_number = request.GET.get("page", 1)
        post_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"posts": post_obj, "page_range": page_range, "paginator": paginator}
        return render(request, "blog/blog_list.html", context)

class BlogListView(View):
    def get(self, requset):
        posts = (
            models.Post.objects.all()
            .order_by("-date_created")
            .annotate(
                comments_count=ExpressionWrapper(
                    Count("comments", filter=Q(comments__is_approved=True)),
                    output_field=IntegerField(),
                ),
            )
        )
        paginator = Paginator(posts, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        post_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"posts": post_obj, "page_range": page_range, "paginator": paginator}
        return render(requset, "blog/blog_list.html", context)

class BlogCatListView(View):
    def get(self, requset, blog_id):
        posts = (
            models.Category.objects.filter(pk=blog_id).first().posts.all()
            .order_by("-date_created")
            .annotate(
                comments_count=ExpressionWrapper(
                    Count("comments", filter=Q(comments__is_approved=True)),
                    output_field=IntegerField(),
                ),
            )
        )
        paginator = Paginator(posts, 9)  # Show 25 user per page.
        page_number = requset.GET.get("page", 1)
        post_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(
            number=page_number, on_each_side=2, on_ends=1
        )
        context = {"posts": post_obj, "page_range": page_range, "paginator": paginator}
        return render(requset, "blog/blog_list.html", context)

class BlogDetailView(View):
    def get(self, requset, blog_id):
        form = forms.CommentForm(requset.POST)
        try:
            post = models.Post.objects.get(pk=blog_id)
            posts_latest = models.Post.objects.all().order_by("-date_created")[:3]
            posts_fav = models.Post.objects.all().order_by("-date_created")[:3]
            comments = (
                models.Comment.objects.filter(
                    post__pk__exact=blog_id, parent=None
                )
                .order_by("-date_created")
            )
            all_comments = (
                models.Comment.objects.filter(
                    post__pk__exact=blog_id, is_approved=True
                )
                .order_by("-date_created")
            )
            all_cats = models.Category.objects.filter(parent__exact=None).order_by("date_created")[:6]
            context = {
                "post": post,
                "posts_latest": posts_latest,
                "posts_fav": posts_fav,
                "comments": comments,
                "all_comments":all_comments,
                "form": form,
                "all_cats":all_cats
            }
            return render(requset, "blog/blog_detail.html", context)
        except Exception as e:
            print(e)
            raise Http404("Page not found!")

    def post(self, request, blog_id):
        form = forms.CommentForm(request.POST)
        try:
            cmid = request.GET.get("reply_to")
            post = models.Post.objects.get(pk=blog_id)
            comment_parent = models.Comment.objects.filter(pk=cmid).first()
            posts_latest = models.Post.objects.all().order_by("-date_created")[:3]
            posts_fav = models.Post.objects.all().order_by("-date_created")[:3]
            all_cats = models.Category.objects.filter(parent__exact=None).order_by("date_created")[:6]
            comments = models.Comment.objects.filter(
                post__pk__exact=blog_id, parent=None
            ).order_by("-date_created")
            all_comments = models.Comment.objects.filter(
                post__pk__exact=blog_id, is_approved=True
            ).order_by("-date_created")
            context = {
                "post": post,
                "posts_latest": posts_latest,
                "posts_fav": posts_fav,
                "comments": comments,
                "all_comments":all_comments,
                "form": form,
                "all_cats":all_cats
            }
            if form.is_valid():
                name = form.cleaned_data["name"]
                email = form.cleaned_data["email"]
                comment = form.cleaned_data["comment"]
                if request.user.is_authenticated:
                    user = request.user
                    models.Comment.objects.create(
                        name=user.fullname,
                        email=user.email,
                        user=user,
                        post=post,
                        comment=comment,
                        parent=comment_parent if cmid else None,
                        is_approved=True if request.user.is_superuser else False
                    )
                else:
                    models.Comment.objects.create(
                        name=name,
                        email=email.strip(),
                        user=None,
                        post=post,
                        comment=comment,
                        parent=comment_parent if cmid else None,
                    )

                return redirect(
                    reverse("blog:blog-detail", kwargs={"blog_id": blog_id})
                )
            else:
                return render(request, "blog/blog_detail.html", context)
        except Exception as e:
            print(e)
            raise Http404("Page not found!")
