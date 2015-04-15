import logging
from django.http import HttpResponse, Http404
from rest_framework import viewsets, serializers, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from core.api.brand import BrandSerializer
from core.models import UserProfile, Brand

logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    # brands = serializers.SerializerMethodField('get_brands')
    brands = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='brands'
    )
    class Meta:
        model = UserProfile
        fields = ('id', 'brands')

    # def get_brands(self, profile):
    #     serializer = BrandSerializer(instance=profile.brands.all(), many=True, context=self.context)
    #     return serializer.data

# class UserProfileList(APIView):
#     queryset = UserProfile.objects.all()
#
#     def post(self, request, format=None):
#         serializer = UserProfileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserProfileDetail(APIView):
#     def get(self, request):
#         pass

class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    model=UserProfile
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
