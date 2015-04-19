import logging
import datetime
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.utils.encoding import force_text

from rest_framework import viewsets, serializers, mixins
from rest_framework.exceptions import ValidationError
from rest_framework_extensions.cache.mixins import CacheResponseMixin, ListCacheResponseMixin
from rest_framework_extensions.key_constructor.bits import FormatKeyBit, QueryParamsKeyBit, UniqueMethodIdKeyBit, \
    PaginationKeyBit, KeyBitBase
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor
from core.models import Affinity, Profile, Brand

logger = logging.getLogger(__name__)


class AffinitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Affinity
        fields = ('id', 'profile', 'brand')


class ModelLastUpdateKeyBit(KeyBitBase):

    def __init__(self, format_string, field_name):
        super(KeyBitBase, self ).__init__()
        self.format_string = format_string
        self.field_name = field_name

    def get_data(self, request, **kwargs):
        # Update  by creating new key based on current timestamp
        query_param = request.QUERY_PARAMS.get(self.field_name)
        if not query_param:
            logger.debug('Query param %s isn\'t provided. Return None for for this key bit' % self.field_name)
            return None

        key = self.format_string % query_param
        value = cache.get(key, None)
        logger.debug('Getting cache item for key %s. Value %s' % (key, value))
        if not value:
            value = datetime.datetime.utcnow()
            logger.debug('Key %s not found. Initialize to %s' % (key, value))
            cache.set(key, value=value)
        return force_text(value)


class AffinityListKeyConstructor(DefaultKeyConstructor):
    all_query_params = QueryParamsKeyBit('*')
    pagination = PaginationKeyBit()
    profile_last_updated = ModelLastUpdateKeyBit(settings.PROFILE_CACHE_FORMAT_STRING, 'profile_id')
    brand_last_updated = ModelLastUpdateKeyBit(settings.BRAND_CACHE_FORMAT_STRING, 'brand_id')


class AffinityViewSet(ListCacheResponseMixin,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    model = Affinity
    serializer_class = AffinitySerializer
    list_cache_key_func = AffinityListKeyConstructor()

    def get_queryset(self):
        profile_id = self.request.QUERY_PARAMS.get('profile_id', None)
        brand_id = self.request.QUERY_PARAMS.get('brand_id', None)

        # return brand affinity list for existing profile_id
        queryset = Affinity.objects.all()
        if profile_id is not None:
            logger.debug("Received profile_id=%s, looking up" % profile_id)
            try:
                Profile.objects.get(pk=profile_id)
            except Profile.DoesNotExist:
                logger.error('profile_id=%s is not existing' % profile_id)
                raise Http404
            logger.debug("Profile %s found. Filtering by profile" % profile_id)
            queryset = queryset.filter(profile_id=profile_id)

        # return profile list for brand_id

        if brand_id is not None:
            logger.debug("Received brand_id=%s, looking up" % brand_id)
            try:
                Brand.objects.get(pk=brand_id)
            except Brand.DoesNotExist:
                logger.error('brand_id=%s is not existing' % brand_id)
                raise Http404
            logger.debug("Brand %s found. Filtering by brand" % brand_id)
            queryset = queryset.filter(brand_id=brand_id)
        return queryset
