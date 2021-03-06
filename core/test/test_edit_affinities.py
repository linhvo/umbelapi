from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Profile, Affinity, Brand


class AffinityEditAPITests(APITestCase):
    """
        Test edit brand affinity by adding and removing affinities
    """
    def setUp(self):
        self.brand1 = Brand.objects.create(name='Nike')
        self.brand2 = Brand.objects.create(name='Adidas')
        self.profile1 = Profile.objects.create()
        self.profile2 = Profile.objects.create()

    # Test affinities are created with correct input:
    def test_different_affinities_created_with_same_profile(self):
        data1 = {'profile': self.profile1.id, 'brand': self.brand1.id}
        data2 = {'profile': self.profile1.id, 'brand': self.brand2.id}
        response = self.client.post(reverse('affinity-list'), data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        affinities = Affinity.objects.filter(profile=self.profile1.id)
        self.assertEqual(len(affinities), 2)
        self.assertEqual(affinities[0].brand, self.brand1)
        self.assertEqual(affinities[1].brand, self.brand2)

    def test_different_affinities_created_with_same_brand(self):
        data1 = {'profile': self.profile1.id, 'brand': self.brand1.id}
        data2 = {'profile': self.profile2.id, 'brand': self.brand1.id}
        response = self.client.post(reverse('affinity-list'), data1, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        affinities = Affinity.objects.filter(brand=self.brand1.id)
        self.assertEqual(len(affinities), 2)
        self.assertEqual(affinities[0].profile, self.profile1)
        self.assertEqual(affinities[1].profile, self.profile2)

    # Tests no affinity is created with invalid input:
    def test_no_affinity_created_with_wrong_profile(self):
        # Test no affinity is created if a profile doesn't exist
        Profile.objects.filter(pk=345).delete()
        data = {'profile': 345, 'brand': self.brand1.id}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        affinities = Affinity.objects.filter(profile=345, brand=self.brand1.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_wrong_brand(self):
        # Test no affinity is created if a brand doesn't exist
        Brand.objects.filter(pk=123).delete()
        data = {'profile': self.profile1.id, 'brand': 123}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        affinities = Affinity.objects.filter(profile=self.profile1.id, brand=123)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_empty_data(self):
        Affinity.objects.all().delete()
        response = self.client.post(reverse('affinity-list'), format='json')
        affinities = Affinity.objects.filter()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(affinities), 0)

    def test_no_affinity_created_with_same_data(self):
        # No affinity is created if with a same profile and brand
        data = {'profile': self.profile1.id, 'brand': self.brand1.id}
        response = self.client.post(reverse('affinity-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(reverse('affinity-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Tests delete affinity:
    def test_delete_affinity(self):
        # A affinity is deleted with correct id
        affinity = Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        affinity_before_delete = Affinity.objects.count()
        response = self.client.delete(reverse('affinity-detail', args=str(affinity.id)), format='json')
        affinity_after_delete = Affinity.objects.count()
        deleted_affinity = Affinity.objects.filter(pk=affinity.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(affinity_before_delete, affinity_after_delete + 1)
        self.assertEqual(len(deleted_affinity), 0)

    def test_no_affinity_delete_with_wrong_id(self):
        Affinity.objects.create(profile=self.profile1, brand=self.brand1)
        Affinity.objects.filter(pk=123).delete()
        affinity_before_delete = Affinity.objects.count()
        response = self.client.delete(reverse('affinity-detail', args=[123]), format='json')
        affinity_after_delete = Affinity.objects.count()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(affinity_before_delete, affinity_after_delete, 1)
