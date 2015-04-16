import logging
from django.http import HttpResponse, Http404
from rest_framework import status, serializers
from rest_framework import viewsets, serializers, mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from core.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'created', 'last_mod', 'name')


class BrandViewSet(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    model=Brand
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer