from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import *
from decimal import Decimal
from django.contrib import messages




def index(request):
    listings = Auction.objects.filter(active=True)
    return render(request, "auctions/index.html",{
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url="auctions/login.html")
def create(request):
    if request.POST:
        title = request.POST["item"]
        description = request.POST["desc"]
        bid = request.POST["bid"]
        photo_url = request.POST["url"]
        category = request.POST["category"]
        if not title or not description or not bid:
            message = "Please enter the required fields"
            return render(request, "auctions/create.html",{
                "message": message
            })
        owner = User.objects.get(username=request.user.username)
        active = True
        created_on = datetime.now()
        auction = Auction(title=title, description=description, current_price=bid, photo_url=photo_url, category=category, owner=owner, active=active, created_on=created_on)
        auction.save()

        for x in Auction.objects.all():
            if category == x:
                break
            else:
                cate = Category(list_object=Auction.objects.filter(category=category).first())
                cate.save()
                break
        return HttpResponseRedirect(reverse("create"))

    else:
        return render(request, "auctions/create.html")


def listing(request, listing_id):
    l = Auction.objects.filter(pk=listing_id)
    bids = len(l.first().bids.all())
    message = None
    temp = []
    for x in l.first().bids.all():
        temp.append(x.bid)
    
    if not temp:
        message = "Place your bid"

    else:
        max_bid = max(temp)

        if Auction.objects.filter(pk=listing_id).first().bids.filter(bid=max_bid).first().bidder.username == request.user.username:
            message = "Your bid is the current bid"
        else:
            message = "Place your bid"
    
    owner = l.first().owner.username
    close = False
    if owner == request.user.username:
        close = True
    if l.first().bids.first() is not None:
        winner = l.first().bids.first().winner
        if winner and winner == request.user.username:
            message = "You have won this auction"
    list = l.first()
    current_price = None
    if temp:
        current_price = max(temp)
    
    comments = list.comments.all()
    return render(request, "auctions/listing.html",{
        "listing": list,
        "bids": bids,
        "message": message,
        "close": close,
        "owner": owner,
        "current_price": current_price,
        "comments": comments
    })


def add_watchlist(request, listing_id):
    if "watchlist" in request.POST:
        user= User.objects.filter(username=request.user.username).first()
        if user.watchlists.filter(list_id=listing_id):
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
        else:
            watchlist = Watchlist(list_id = listing_id, owner= user)
            watchlist.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    else:
        user= User.objects.filter(username=request.user.username).first()
        removeWatchlist = user.watchlists.filter(list_id=listing_id).delete()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

def bid(request):
    id = request.POST["listing_id"]
    id = int(id)
    listing = Auction.objects.filter(pk=id).first()
    price = listing.current_price
    bids= listing.bids.all()
    user_name = request.user.username

    if "close" in request.POST:
        owner = Auction.objects.filter(pk=id).first().owner.username
        if user_name == owner:
            temp = []
            for x in bids:
                temp.append(x.bid)
            if temp:
                winner = bids.filter(bid=max(temp)).first().bidder.username
                set_all_winner = bids.filter(bid=max(temp)).all()
                for set_winner in set_all_winner:
                    set_winner.winner = winner
                    set_winner.save()
            listing.active = False
            listing.save()
            close_all = listing.bids.all()
            for close in close_all:
                close.close = True
                close.save()
            messages.success(request, "Bid closed succesfully")
            return HttpResponseRedirect(reverse("listing", args=(id,)))

    user_bid = request.POST["user_bid"]

    if not request.POST["user_bid"]:
        messages.error(request, "Bid cannot be empty")
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    user_bid = Decimal(user_bid)
    if user_bid >= price:
        if not bids:
            bid = Bid(listing=listing, bid=user_bid, bidder=User.objects.filter(username=user_name).first(), close=False)
            bid.save()
            return HttpResponseRedirect(reverse("listing", args=(id,)))
        else:
            temp = []
            for x in bids:
                temp.append(x.bid)
            if user_bid > max(temp):
                bid = Bid(listing=listing, bid=user_bid, bidder=User.objects.filter(username=user_name).first(), close=False)
                bid.save()
                return HttpResponseRedirect(reverse("listing", args=(id,)))
            else:
                messages.error(request, "Bid must be greater than the current bids")
                return HttpResponseRedirect(reverse("listing", args=(id,)))

    else:
        messages.error(request, "Bid must be equal to or greater than the current price")
        return HttpResponseRedirect(reverse("listing", args=(id,)))


def comment(request):
    id = request.POST["listing_id"]
    content = request.POST["comment"]
    if not content:
        messages.warning(request, "Input field cannot be empty")
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    user = request.user.username

    listing = Auction.objects.filter(pk=id).first()

    commenter = User.objects.filter(username=user).first()
    comment = Comment(commenter=commenter, content=content, listing=listing)
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(id,)))


@login_required(login_url="auctions/login.html")
def watchlist(request):
    user = User.objects.filter(username=request.user.username).first()
    listings = user.watchlists.all()
    items = []
    for x in listings:
        items.append(Auction.objects.filter(pk=x.list_id).first())
    
    return render(request, "auctions/watchlist.html",{
        "items": items
    })



def categories(request):
    categorys = Category.objects.all()
    all_category = []
    for category in categorys:
        if category.list_object.category in all_category:
            l = None
        else:
            all_category.append(category.list_object.category)
    return render(request, "auctions/categories.html",{
        "categories": all_category
    })

def categorylist(request, category):
    listing = Auction.objects.filter(category=category, active=True)
    return render(request, "auctions/categorylist.html",{
    "listings": listing,
    "category": category
})
