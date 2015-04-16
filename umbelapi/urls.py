from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter
from core.api.profile import UserProfileViewSet
from core.api.brand import BrandViewSet
from core.api.affinity import AffinityViewSet

router = SimpleRouter()
router.register(r'profiles', UserProfileViewSet, base_name='profile')
router.register(r'brands', BrandViewSet, base_name='brand')
router.register(r'affinities', AffinityViewSet, base_name='affinity')


urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
)


