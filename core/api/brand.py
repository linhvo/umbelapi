import logging
from rest_framework import viewsets, serializers, mixins
from core.models import Brand
logger = logging.getLogger(__name__)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'created', 'last_mod', 'name')


class BrandViewSet(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    model=Brand
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer