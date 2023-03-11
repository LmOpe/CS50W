from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    poster = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.username,
            "content": self.content,
            "time": self.time.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }
    
    def is_valid_post(self):
        return self.content != "" and self.poster != ""

class Follow(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followings")
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followers")

    def serialize(self):
        return {
            "follower": self.follower.username,
            "following": self.following.username
        }

class Like(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="all_likes")
    liker = models.ForeignKey("User", on_delete=models.CASCADE, related_name="all_likes")

    def serialize(self):
        return {
            "post": self.post.id,
            "liker": self.liker.username
        }