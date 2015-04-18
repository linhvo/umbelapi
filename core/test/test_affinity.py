from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Profile, Affinity, Brand


class AffinityTests(APITestCase):
    """
        Test edit brand affinity by adding and removing affinities
    """
    def setUp(self):
        self.brand1 = Brand.objects.create(name='Nike')
        self.brand2 = Brand.objects.create(name='Adidas')
        self.profile1 = Profile.objects.create()
        self.profile2 = Profile.objects.create()

    # Tests new affinity is created with valid input

    def test_different_affinities_created_with_same_profile(self):
        data1 = {'profile': self.profile1.id, 'brand': self.brand1.id}
        data2 = {'profile': self.profile1.id, 'brand': self.brand2.id}
        response = self.client.post(reverse('affinity-list'), data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_different_affinities_created_with_same_brand(self):
        data1 = {'profile': self.profile1.id, 'brand': self.brand1.id}
        data2 = {'profile': self.profile2.id, 'brand': self.brand2.id}
        response = self.client.post(reverse('affinity-list'), data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Tests no affinity is created with invalid input
    def test_no_affinity_created_with_wrong_profile(self):
        # Test no affinity is created if a profile doesn't exist
        data = {'profile': 345, 'brand': self.brand1.id}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        affinities = Affinity.objects.filter(profile=345, brand=self.brand1.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_wrong_brand(self):
        # Test no affinity is created if a brand doesn't exist
        data = {'profile': self.profile1.id, 'brand': 123}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        affinities = Affinity.objects.filter(profile=self.profile1.id, brand=123)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_empty_data(self):
        response = self.client.post(reverse('affinity-list'), format='json')
        affinities = Affinity.objects.filter()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_same_data(self):
        # No affinity is created if with same profile and brand
        data = {'profile': self.profile1.id, 'brand': self.brand1.id}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests delete affinity
    def test_delete_affinity(self):
        # A affinity is deleted with correct id
        data = self.create_affinity(self.profile1.id, self.brand1.id)
        affinity_id = data['id']
        affinity_before_delete = Affinity.objects.count()
        response = self.client.delete(reverse('affinity-detail', args=str(affinity_id)), format='json')
        affinity_after_delete = Affinity.objects.count()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotEqual(affinity_before_delete, affinity_after_delete)

    def test_no_affinity_delete_with_wrong_id(self):
        # A affinity is not deleted with wrong id
        self.create_affinity(self.profile1.id, self.brand1.id)
        affinity_before_delete = Affinity.objects.count()
        response = self.client.delete(reverse('affinity-detail', args=[123]), format='json')
        affinity_after_delete = Affinity.objects.count()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(affinity_before_delete, affinity_after_delete, 1)

    # Tests return lists of brand affinities for a given profile ID
    def test_get_brand_list(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile1.id, self.brand2.id)
        response = self.client.get("%s?profile_id=%s" % (reverse('affinity-list'), self.profile1.id), format='json')
        data = response.data
        self.assertEqual(2, len(data))
        self.assertEqual(data[0]['profile'], self.profile1.id)
        self.assertEqual(data[0]['brand'], self.brand1.id )
        self.assertEqual(data[1]['profile'], self.profile1.id)
        self.assertEqual(data[1]['brand'], self.brand2.id)

    def test_no_brand_return_with_no_affinity(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile1.id, self.brand2.id)
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profile2.id)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(0, len(data))

    def test_raise_exception_with_invalid_profile(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile1.id, self.brand2.id)
        url = "%s?profile_id=%s" % (reverse('affinity-list'), 1234)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_profile_list(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile2.id, self.brand1.id)
        response = self.client.get("%s?brand_id=%s" % (reverse('affinity-list'), self.brand1.id), format='json')
        data = response.data
        self.assertEqual(2, len(data))
        self.assertEqual(data[0]['profile'], self.profile1.id)
        self.assertEqual(data[0]['brand'], self.brand1.id )
        self.assertEqual(data[1]['profile'], self.profile2.id)
        self.assertEqual(data[1]['brand'], self.brand1.id)

    def test_no_profile_return_with_no_affinity(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile2.id, self.brand1.id)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brand2.id)
        response = self.client.get(url, format='json')
        data = response.data
        self.assertEqual(0, len(data))

    def test_raise_exception_with_invalid_brand(self):
        self.create_affinity(self.profile1.id, self.brand1.id)
        self.create_affinity(self.profile2.id, self.brand1.id)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), 1234)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def create_affinity(self, profile, brand):
        data = {'profile': profile, 'brand': brand}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        return response.data




