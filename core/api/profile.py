import logging
from django.http import HttpResponse, Http404
from rest_framework import viewsets, serializers, mixins
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import APIView
from core.api.brand import BrandSerializer
from core.models import UserProfile, Brand
from rest_framework_extensions.mixins import NestedViewSetMixin

logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'created', 'last_mod')


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    model=UserProfile
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer