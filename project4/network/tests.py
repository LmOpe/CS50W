from django.test import Client, TestCase

from .models import User, Post, Follow

# Create your tests here.
class NetworkTestCase(TestCase):

    def setUp(self):

        # Create Users.
        u1 = User.objects.create(username="LmO", password="ASJKHSL")
        u2 = User.objects.create(username="Law", password="ASJKAABHSL")
        u3 = User.objects.create(username="LmOpe", password="ASJ23HSL")


        # Create posts.
        p1 = Post.objects.create(poster=u1, content="Hi")
        p2 = Post.objects.create(poster=u1, content="Helo")
        p3 = Post.objects.create(poster=u1, content="Hello")
        p5 = Post.objects.create(poster=u2, content="")

        # Create followers
        f1 = Follow.objects.create(follower=u1, following=u3)
        f1 = Follow.objects.create(follower=u1, following=u2)
        f1 = Follow.objects.create(follower=u2, following=u1)
        f1 = Follow.objects.create(follower=u2, following=u3)
        f1 = Follow.objects.create(follower=u3, following=u1)

    def test_follower_count(self):
        a = User.objects.get(username="Law")
        self.assertEqual(a.followers.count(), 1)

    def test_following_count(self):
        a = User.objects.get(username="LmOpe")
        self.assertEqual(a.followings.count(), 1)

    def test_post_count(self):
        a = User.objects.get(username="LmO")
        self.assertEqual(a.posts.count(), 3)
    
    def test_is_valid_post(self):
        u = User.objects.get(username="LmO")
        p = Post.objects.get(poster=u, content="Hello")
        self.assertTrue(p.is_valid_post())
    
    def test_is_not_valid_post(self):
        u = User.objects.get(username="Law")
        p = Post.objects.get(poster=u, content="")
        self.assertFalse(p.is_valid_post())