from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class User(AbstractUser):
    pass


class Auction(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    photo_url = models.SlugField(max_length=500, blank=True)
    category = models.CharField(max_length=20, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField()
    created_on = models.DateTimeField()

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    winner = models.CharField(max_length=30, blank=True) 
    close = models.BooleanField()

    def __str__(self):
        return f"{self.listing}"

class Category(models.Model):
    list_object = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="lists")
    
    def __str__(self):
        return f"{self.list_object.category}"

class Watchlist(models.Model):
    list_id = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")

    def __str__(self):
        return f"{self.owner} has item with id {self.list_id} in their watchlist"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=True)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.content}"