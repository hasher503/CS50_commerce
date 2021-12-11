"""auction app views"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


from .models import User, Listing, Category, Bid
from .forms import NewListingForm, BidForm, CommentForm

def index(request):
    """homepage"""
    listings = Listing.objects.filter(active=True).order_by('-pk')
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    """login a user"""
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
    """logout user"""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """register a new user"""
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
    return render(request, "auctions/register.html")


@login_required
def create(request):
    """create a new auction listing item"""

    # if POST request, save NewListingForm info
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user # add user info from this request
            listing.save()  # commit to DB
            return HttpResponseRedirect(reverse("index"))
        # if indvalid form, return to user
        return render(request, "auctions/create.html", {
            "newlistingform": form
        })

    # if GET request, display NewListingForm
    return render(request, "auctions/create.html", {
        "newlistingform": NewListingForm()
    })


@login_required
def item(request, item_id):
    """display an individual auction item"""
    auction_item = Listing.objects.get(pk=item_id) # THIS Listing
    bidform = BidForm() # new blank BidForm
    commentform = CommentForm() # new blank CommentForm
    comments = auction_item.commented_item.all() # all comments on this item
    onlist = watching(request.user, item_id) # watchlist boolean - calls watching() below
    price = auction_item.price # lowest price seller will accept OR previous highest offer (if any)
    prev_bid = Bid.objects.filter(item=auction_item).last() # highest bid on this item (if any)
    if prev_bid:
        prev_bid = prev_bid.bid_price # if there was no previous bid, this is None

    # if POST request, attempt to save bid
    if request.method == "POST":
        bidform = BidForm(request.POST)
        if bidform.is_valid:
            bid = bidform.save(commit=False) # retrieve info submitted from form
            # add bid User and bid Listing but don't save it yet
            bid.bidder = request.user
            bid.item = auction_item

            # if previous bid exists, new bid must be higher
            if prev_bid:
                if bid.bid_price > prev_bid:
                    bid.save() # submit this completed Bid to DB
                    # update the price on this Listing
                    auction_item.price = bid.bid_price
                    auction_item.save()
                    # Refresh the page with blank BidForm and congrats message
                    return render(request, "auctions/item.html", {
                        "item": auction_item,
                        "bidnum": len(Bid.objects.filter(item=auction_item)),
                        "bidform": BidForm(),
                        "bidmessage": "Congratulations! You are currently the highest bidder.",
                        "onlist": onlist,
                        "commentform": commentform,
                        "comments": comments
                    })
            # if no previous bids, this bid must be equal to seller's min price
            else:
                if bid.bid_price >= price:
                    bid.save() # submit this completed Bid to DB
                    # update the price on this Listing
                    auction_item.price = bid.bid_price
                    auction_item.save(update_fields=['price'])
                    # Refresh the page with blank BidForm and congrats message
                    return render(request, "auctions/item.html", {
                        "item": auction_item,
                        "bidnum": len(Bid.objects.filter(item=auction_item)),
                        "bidform": BidForm(),
                        "bidmessage": "Congratulations! You are the first bidder.",
                        "onlist": onlist,
                        "commentform": commentform,
                        "comments": comments
                    })

        # if indvalid bid form or bid price too low, return to user
        return render(request, "auctions/item.html", {
            "item": auction_item,
            "bidnum": len(Bid.objects.filter(item=auction_item)),
            "bidform": bidform,
            "bidmessage": "Invalid bid. New bid must be a decimal greater than previous bid.",
            "onlist": onlist,
            "commentform": commentform,
            "comments": comments
        })
    # GET request: if auction item is CLOSED for bidding, render template with alert, without forms
    if not auction_item.active:
        return render(request, "auctions/item.html", {
            "item": auction_item,
            "comments": comments
        })

    # otherwise regular GET request: pass in EMPTY froms
    return render(request, "auctions/item.html", {
        "item": auction_item,
        "bidnum": len(Bid.objects.filter(item=auction_item)),
        "bidform": bidform,
        "onlist": onlist,
        "commentform": commentform,
        "comments": comments
    })


@login_required
def category_view(request, cat=None):
    """display auction item categories the user can choose"""
    categories = Category.objects.all()
    if cat:
        # get all listings with category cat, pass into render
        cat_pk = Category.objects.get(category=cat).pk
        cat_items = Listing.objects.filter(category=cat_pk, active=True).order_by('-pk')
        return render(request, "auctions/categories.html", {
            "one_category": cat,
            "cat_items": cat_items
        })
    # if no arguments, render list of all category choices
    return render(request, "auctions/categories.html", {
            "categories": categories
        })

@login_required
def comment(request, item_id):
    """Comment on an auction item"""
    if request.method == "POST":
        commentform = CommentForm(request.POST)
        auction_item = Listing.objects.get(pk=item_id)
        if commentform.is_valid:
            this_comm = commentform.save(commit=False) # retrieve comment but don't commit
            this_comm.commenter = request.user # save commenter user
            this_comm.item = auction_item # save Listing
            this_comm.save() # submit completed form to DB
            return HttpResponseRedirect(reverse('item', kwargs={
                "item_id": item_id
            }))

@login_required
def watch_view(request):
    """display all items on a user's watchlist"""
    this_user = request.user
    watchlist = this_user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def watch_item(request, item_id):
    """"add or remove an item from watchlist"""
    listing = Listing.objects.get(pk=item_id)
    user = request.user
    if request.method == "POST":
        # if on the watchlist, remove
        if watching(user, item_id):
            user.watchlist.remove(listing)
        else:
            # if not on the watchlist, add
            user.watchlist.add(listing)

        return HttpResponseRedirect(reverse("item", kwargs={
            "item_id": item_id
        }))

@login_required
def all_closed(request):
    """view all auctions that have been won"""
    listings = Listing.objects.filter(active=False)
    return render(request, "auctions/closed.html", {
        "listings": listings
    })

@login_required
def close_item(request, item_id):
    """ Change a Listing status from Active to Not Active """
    if request.method == "POST":
        auction_item = Listing.objects.get(pk=item_id)
        auction_item.active = False
        auction_item.save()

        # get highest bid on this item, set winning User
        winbid = Bid.objects.filter(item=auction_item).last()
        auction_item.winner = winbid.bidder
        auction_item.save()

        return HttpResponseRedirect(reverse("item", kwargs={
            "item_id": item_id
        }))

def watching(user, itemid):
    """see if an item is on a user's watchlist"""
    listing = Listing.objects.get(pk=itemid)
    if listing in user.watchlist.all():
        return True
    return False