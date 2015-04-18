from rest_framework import viewsets, serializers, mixins
from core.models import Profile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'created', 'last_mod')


class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    model=Profile
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer