from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Brand, Profile, Affinity


class AffinityListAPITests(APITestCase):
    """
        Test get affinities by profile and by brand and its caching
    """
    def setUp(self):
        self.brand1 = Brand.objects.create(name='Nike')
        self.brand2 = Brand.objects.create(name='Adidas')
        self.profile1 = Profile.objects.create()
        self.profile2 = Profile.objects.create()

    def test_get_brand_list(self):
        # Tests list of brand affinities are returned with correct profile_id
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile1, brand=self.brand2)
        response = self.client.get("%s?profile_id=%s" % (reverse('affinity-list'), self.profile1.id), format='json')
        data = response.data
        self.assertEqual(2, len(data))
        self.assertEqual(data[0]['profile'], self.profile1.id)
        self.assertEqual(data[0]['brand'], self.brand1.id )
        self.assertEqual(data[1]['profile'], self.profile1.id)
        self.assertEqual(data[1]['brand'], self.brand2.id)

    def test_no_brand_return_with_no_affinity(self):
        # Tests empty list is returned if profile doesn't have any brand affinity
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile1, brand=self.brand2)
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profile2.id)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(0, len(data))

    def test_404_with_invalid_profile(self):
        # Tests raise exceptions if profile does not exist
        Profile.objects.filter(pk=1234).delete()
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile1, brand=self.brand2)
        url = "%s?profile_id=%s" % (reverse('affinity-list'), 1234)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Tests return lists of profile for a given brand ID:
    def test_get_profile_list(self):
        # Tests list of profiles are returned with correct brand_id
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile2, brand=self.brand1)
        response = self.client.get("%s?brand_id=%s" % (reverse('affinity-list'), self.brand1.id), format='json')
        data = response.data
        self.assertEqual(2, len(data))
        self.assertEqual(data[0]['profile'], self.profile1.id)
        self.assertEqual(data[0]['brand'], self.brand1.id )
        self.assertEqual(data[1]['profile'], self.profile2.id)
        self.assertEqual(data[1]['brand'], self.brand1.id)

    def test_no_profile_return_with_no_affinity(self):
        # Tests empty list is return if there is not any profile related to a brand
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile2, brand=self.brand1)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brand2.id)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(0, len(data))

    def test_404_with_invalid_brand(self):
        # Tests raise exception if brand does not exist
        Brand.objects.filter(pk=1234)
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.create(profile=self.profile2, brand=self.brand1)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), 1234)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
