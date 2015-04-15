from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from core.api.profile import UserProfileViewSet

router = DefaultRouter()
router.register(r'profiles', UserProfileViewSet)
urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
)


