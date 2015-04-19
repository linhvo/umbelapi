import logging
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
import time

logger = logging.getLogger(__name__)


class Profile(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)
    affinities = models.ManyToManyField('Brand', through='Affinity')

@receiver(post_save, sender=Profile)
def clear_profile_cache(sender, instance, **kwargs):
    """
    Post save signal of Profile model that clear appropriate cache for Affinity Api
    :param sender:
    :param instance:
    :param kwargs: if kwarg cascade is False (True by default), we'll also clear the cache of all profiles that
     like this brand
    """
    key = settings.PROFILE_CACHE_FORMAT_STRING % instance.id
    timestamp = int(time.time())
    logger.debug("Updating %s to %s" % (key, timestamp))
    cache.set(key, timestamp)
    if kwargs.get('cascade', True):
        # also need to clear brand cache of all the brands that this user like
        profile_cache_items = {settings.BRAND_CACHE_FORMAT_STRING % brand.id: timestamp for brand in instance.affinities.all()}
        logger.debug("Cascade is True, Updating %s" % profile_cache_items)
        cache.set_many(profile_cache_items)


class Brand(models.Model):
    name = models.CharField(max_length=100, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    last_mod = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=Brand)
def clear_brand_cache(sender, instance, **kwargs):
    """
    Post save signal of brand model that clear appropriate cache for Affinity Api
    :param sender:
    :param instance: brand instance
    :param kwargs: if kwarg cascade is False (True by default), we'll also clear the cache of all profiles that
     like this brand
    """
    key = settings.BRAND_CACHE_FORMAT_STRING % instance.id
    timestamp = int(time.time())
    logger.debug("Updating %s to %s" % (key, timestamp))
    cache.set(key, timestamp)
    # also need to clear all cache of profiles that like this brand
    if kwargs.get('cascade', True):
        affinities = Affinity.objects.filter(brand=instance).select_related()
        brand_cache_items = {settings.PROFILE_CACHE_FORMAT_STRING % affinity.profile.id: timestamp for affinity in
                             affinities}
        logger.debug("Cascade is True, Updating %s" % brand_cache_items)
        cache.set_many(brand_cache_items)


class Affinity(models.Model):
    profile = models.ForeignKey('Profile')
    brand = models.ForeignKey('Brand')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "brand")

@receiver(post_save, sender=Affinity)
@receiver(post_delete, sender=Affinity)
def clear_affinity_cache(sender, instance, **kwargs):
    # Clear cache and set a new cache key for profile and brand when affinity is updated
    clear_brand_cache(None, instance.brand, cascade=False)
    clear_profile_cache(None, instance.profile, cascade=False)
