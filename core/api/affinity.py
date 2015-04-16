import logging
from django.http import HttpResponse, Http404
from rest_framework import viewsets, serializers, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView
from core.api.brand import BrandSerializer
from core.api.profile import UserProfileSerializer
from core.models import UserProfile, Brand, Affinity
from rest_framework_extensions.mixins import NestedViewSetMixin

logger = logging.getLogger(__name__)


class AffinitySerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(
        read_only=False,
        queryset=Brand.objects.all()
    )

    profile = serializers.PrimaryKeyRelatedField(
        read_only=False,
        queryset=UserProfile.objects.all()
    )

    # brand = BrandSerializer(
    #     many=False,
    #     read_only=True
    # )
    #
    # profile = UserProfileSerializer(
    #     many=False,
    #     read_only=True
    # )

    class Meta:
        model = Affinity
        fields = ('id', 'profile', 'brand')

class AffinityViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    model=Affinity
    queryset = Affinity.objects.all()
    serializer_class = AffinitySerializer