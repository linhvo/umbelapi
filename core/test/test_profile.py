from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Profile


class ProfileTests(APITestCase):
    def test_create_profile(self):
        """
        Ensure we can create a new profile object.
        """
        Profile.objects.all().delete()
        response = self.client.post(reverse('profile-list'), format='json')
        profiles = Profile.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(profiles), 1)
        self.assertIsNotNone(profiles[0].id)
        self.assertIsNotNone(profiles[0].created)

