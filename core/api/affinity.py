import logging
from django.http import Http404

from rest_framework import viewsets, serializers, mixins
from core.models import Affinity, Profile, Brand

logger = logging.getLogger(__name__)


class AffinitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Affinity
        fields = ('id', 'profile', 'brand')


class AffinityViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    model = Affinity
    serializer_class = AffinitySerializer

    def get_queryset(self):
        queryset = Affinity.objects.all()
        # return brand affinity list for existing profile_id
        profile_id = self.request.QUERY_PARAMS.get('profile_id', None)
        if profile_id is not None:
            logger.info("Received profile_id=%s, looking up" % profile_id)
            try:
                Profile.objects.get(pk=profile_id)
            except Profile.DoesNotExist:
                logger.error('profile_id=%s is not existing' % profile_id)
                raise Http404
            logger.info("Profile %s found. Filtering by profile" % profile_id)
            queryset = queryset.filter(profile_id=profile_id)

        # return profile list for brand_id
        brand_id = self.request.QUERY_PARAMS.get('brand_id', None)
        if brand_id is not None:
            logger.info("Received brand_id=%s, looking up" % brand_id)
            try:
                Brand.objects.get(pk=brand_id)
            except Brand.DoesNotExist:
                logger.error('brand_id=%s is not existing' % brand_id)
                raise Http404
            logger.info("Brand %s found. Filtering by brand" % brand_id)
            queryset = queryset.filter(brand_id=brand_id)
        return queryset

