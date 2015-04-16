from django.db import models


class UserProfile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)
    affinities = models.ManyToManyField('Brand', through='Affinity')


class Brand(models.Model):
    name = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)


class Affinity(models.Model):
    profile = models.ForeignKey('UserProfile')
    brand = models.ForeignKey('Brand')
    created = models.DateTimeField(auto_now_add=True)


