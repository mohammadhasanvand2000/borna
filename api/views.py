from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import SessionAuthentication

from django.db.models import F, ExpressionWrapper, IntegerField
from django.conf import settings
from shop import models as shop_models


User = get_user_model()


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


def _empty_cart():
    return {}


def _update_cart(cart, flag, id):
    product = (
        shop_models.Product.objects.filter(pk=id)
        .annotate(
            final_price=ExpressionWrapper(
                F("price") * (1 - F("discount") / 100.0),
                output_field=IntegerField(),
            )
        )
        .first()
    )
    if not cart["items"]:
        if flag == 1:
            cart["items"] = [
                {
                    "id": product.id,
                    "title": product.title,
                    "price": product.final_price,
                    "pic": product.image_cover.url if product.image_cover else None,
                    "count": 1,
                    "total": 1 * product.final_price,
                }
            ]
        else:
            cart["items"] = []

        total = 0
        for item in cart["items"]:
            total += item["total"]
        cart["total"] = total
        return cart
    for item in cart["items"]:
        if item["id"] == id:
            item["count"] = item["count"] + 1 if flag == 1 else item["count"] - 1
            item["total"] = item["count"] * product.final_price
            break
    else:
        cart["items"].append(
            {
                "id": product.id,
                "title": product.title,
                "price": product.final_price,
                "pic": product.image_cover.url if product.image_cover else None,
                "count": 1 if flag == 1 else 0,
                "total": (1 if flag == 1 else 0) * product.final_price,
            }
        )
    cart["items"] = [item for item in cart["items"] if item["count"] > 0]
    total = 0
    for item in cart["items"]:
        total += item["total"]
    cart["total"] = total
    return cart


class UpdateCartAPI(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get(self, request, flag=None, id=None):
        try:
            cart = request.session.get("cart", _empty_cart())
            if cart:
                return Response(
                    {
                        "status": 200,
                        "data": {"cart": cart},
                        "message": "Cart is yours :)",
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"status": 200, "data": {"cart": {}}, "message": "Cart is empty!"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": 200,
                    "data": {"cart": {}},
                    "message": f"ERROR: {e if settings.DEBUG else 'Something went wrong!'}",
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, flag, id):
        try:
            cart = request.session.get("cart", _empty_cart())
            if not "items" in cart:
                cart["items"] = []
                cart["total"] = 0
            cart = _update_cart(cart, flag, id)
            request.session["cart"] = cart
            return Response(
                {"status": 200, "data": {"cart": cart}, "message": "Cart is yours :)"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "status": 200,
                    "data": {"cart": {}},
                    "message": f"ERROR: {e if settings.DEBUG else 'Something went wrong!'}",
                },
                status=status.HTTP_200_OK,
            )
