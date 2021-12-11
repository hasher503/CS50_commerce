"""auction app URLs"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("item/<str:item_id>", views.item, name="item"),
    path("categories", views.category_view, name="category_view"),
    path("categories/<str:cat>", views.category_view, name="category_view2"),
    path("item/<str:item_id>/comment", views.comment, name="comment"),
    path("item/<str:item_id>/watchlist", views.watch_item, name="watch_item"),
    path("watchlist", views.watch_view, name="watch_view"),
    path("closed", views.all_closed, name="all_closed"),
    path("item/<str:item_id>/closed", views.close_item, name="close_item")
]
