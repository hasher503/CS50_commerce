"""models for auction app"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """users"""
    watchlist = models.ManyToManyField('Listing', related_name="watchers", blank=True)


class Category(models.Model):
    """categories for sold items"""
    category = models.CharField(max_length=10)

    def __str__(self):
        return self.category

class Listing(models.Model):
    """items being sold"""
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="seller")
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="winner")
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    description = models.CharField(max_length=500)
    img_url = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.seller}'s {self.title}"

class Bid(models.Model):
    """a decimal price bid on one item by one user"""
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item")
    bid_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"bid on {self.item} for {self.bid_price} by {self.bidder}"

class Comment(models.Model):
    """A text comment on one item by one user"""
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commented_item")
    comment = models.CharField(max_length=1000)
    datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment on {self.item} by {self.commenter}"
