from django.db import models


class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)


class Brand(models.Model):
    name = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)
    profiles = models.ManyToManyField(UserProfile, related_name='brands')



