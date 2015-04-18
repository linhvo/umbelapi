from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Profile


class ProfileTests(APITestCase):
    def test_create_profile(self):
        """
        Ensure we can create a new profile object.
        """
        profiles = Profile.objects.count()
        response = self.client.post(reverse('profile-list'), format='json')
        new_profiles = Profile.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(profiles + 1, new_profiles)

