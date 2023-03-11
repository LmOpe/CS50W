import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


def index(request):
    return render(request, "network/index.html")
    
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="network/login.html")
def new_post(request):
    if request.method == "POST":
        # Get post content
        data = json.loads(request.body)
        content = data.get("content")
        poster = request.user

        # Attempt to add post to database
        if content:
            post = Post(poster=poster, content=content, likes=0)
            post.save()
            return JsonResponse({
            "message": "Posted."
        }, status=201)
        else:
            return JsonResponse({
            "error": "Post content cannot be empty."
        }, status=400)

    else:
        return JsonResponse({"error": "POST request required."}, status=400)
    
def posts(request):
    if int(request.GET.get('check')) == 1:
        user = User.objects.filter(username=request.user).first()
        posts = []
        user_post = []
        followings = user.followings.all()
        if followings:
            for following in followings:
                user_post = following.following.posts.all()
                for post in user_post:
                    posts.append(post)
        posts.sort(key=lambda x:x.id)
        posts.reverse()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'network/index.html', {
            'page_obj': page_obj,
            'check': int(request.GET.get('check'))
            })
    else:
        posts = Post.objects.order_by("-time").all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'network/index.html', {
            'page_obj': page_obj,
            'check': int(request.GET.get('check'))
            })

def profile(request, username):
    user = User.objects.filter(username=username).first()
    if user:   
        followers = user.followers.all()
        followings = user.followings.all()
        posts = user.posts.order_by("-time").all()
        result = [[post.serialize() for post in posts], [follower.serialize() for follower in followers], [following.serialize() for following in followings]]
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({"error": "User does not exist"}, status=404)

@csrf_exempt
def follow(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get('edit'):
            if data.get('content'):
                post = Post.objects.filter(poster=request.user, content=data.get('previous_content')).first()
                post.content = data.get('content')
                post.save()
                return JsonResponse({
                "message": "Post Edited."
            }, status=201)
            else:
                return JsonResponse({
                "error": "Post content cannot be empty."
            }, status=400)
        elif data.get('follow'):       
            follower = User.objects.filter(username=data.get("follower")).first()
            following = User.objects.filter(username=data.get("following")).first()
            follow = Follow(follower=follower, following=following)
            follow.save()
            return JsonResponse({"message": "User followed"}, status=201)
        else:
            follower = User.objects.filter(username=data.get("follower")).first()
            following = User.objects.filter(username=data.get("following")).first()
            follow = Follow.objects.filter(follower=follower, following=following).all()
            follow.delete()
            for each in follow:
                each.save()
            return JsonResponse({"message": "User unfollowed"}, status=201)

@csrf_exempt
def like(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        id = data.get('id')
        user = data.get('user')
        post = Post.objects.filter(pk=id).first()
        liker = User.objects.filter(username=user).first()
        if liker.all_likes.filter(post=post).first() and liker.all_likes.filter(post=post).first().post == post:
            like = Like.objects.filter(post=post, liker=liker).all()
            like.delete()
            for each in like:
                each.save()
            post.likes = post.likes - 1
            post.save()
            return JsonResponse({"message": "Unliked"}, status=201)
        else:
            post.likes = post.likes + 1
            post.save()
            like = Like(post=post, liker=liker)
            like.save()
            return JsonResponse({"message": "Liked"}, status=201)