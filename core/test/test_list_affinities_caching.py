from django.core.cache import cache
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from core.models import Brand, Profile, Affinity


class AffinityListCachingAPITests(APITestCase):
    """
        Test caching aspect of affinities list
    """
    def setUp(self):
        Affinity.objects.all().delete()
        Brand.objects.all().delete()
        Profile.objects.all().delete()
        self.brands = [Brand.objects.create(name=n) for n in ['Nike', 'Adidas', 'Puma']]
        self.profiles = [Profile.objects.create() for i in range(2)]
        self.p1_affinities = [Affinity.objects.create(profile=self.profiles[0], brand=b) for b in self.brands]
        self.p2_affinities = [Affinity.objects.create(profile=self.profiles[1], brand=b) for b in self.brands[0:2]]

    def get_and_assert_query_count(self, url, action, first_count, second_count):
        """
        helper that will get the provided url twice and verify the # of queries run.
        Then it'll invoke a provided action function and perform the get again
        this time, verify the # of query against first_count
        :param url:
        :param action: lambda function that does something that will invalidate the cache
        :param first_count: The # of queries run in the first and final (after invoking
         action) GET
        :param second_count: The # of queries run in the 2nd GET (should be < first_count)
        """
        cache.clear()
        with self.assertNumQueries(first_count):
            self.client.get(url, format='json')
        with self.assertNumQueries(second_count):
            self.client.get(url, format='json')
        action()
        with self.assertNumQueries(first_count):
            self.client.get(url, format='json')

    def test_basic_caching(self):
        # test that we don't query the database if the response was previously cached
        # and after cache is cleared, we'll query the db again
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profiles[0].id)
        self.get_and_assert_query_count(url, cache.clear, 2, 0)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brands[0].id)
        self.get_and_assert_query_count(url, cache.clear, 2, 0)

    def test_update_profile_clear_cache(self):
        # test that cached content won't be returned after a profile is updated
        update_profile = lambda: self.profiles[0].save()
        # updating a profile should clear its own affinity API
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profiles[0].id)
        self.get_and_assert_query_count(url, update_profile, 2, 0)

        # updating a profile should also invalidate all 'get profile by brand' for
        # all brands that this profile has affinity with
        for affinity in self.p1_affinities:
            url = "%s?brand_id=%s" % (reverse('affinity-list'), affinity.brand.id)
            self.get_and_assert_query_count(url, update_profile, 2, 0)

    def test_update_brand_clear_cache(self):
        # test that cached content won't be returned after a brand is updated
        update_brand = lambda: self.brands[0].save()
        # updating a brand should clear its own affinity API
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brands[0].id)
        self.get_and_assert_query_count(url, update_brand, 2, 0)

        # updating a brand should also invalidate all 'get brand by profile' for
        # all profiles that have affinity with this brand
        for affinity in Affinity.objects.filter(brand=self.brands[0]):
            url = "%s?profile_id=%s" % (reverse('affinity-list'), affinity.profile.id)
            self.get_and_assert_query_count(url, update_brand, 2, 0)

    def test_update_affinity_clear_cache(self):
        # test that by updating an affinity, both'get profiles by brand'
        # and 'get brands by profile' api will be invalidated
        action = lambda: self.p1_affinities[0].save()
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profiles[0].id)
        self.get_and_assert_query_count(url, action, 2, 0)
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.p1_affinities[0].brand.id)
        self.get_and_assert_query_count(url, action, 2, 0)

    def test_delete_affinity_clear_cache(self):
        # test that by deleting an affinity, both get profiles by brand'
        # and 'get brands by profile' api will be invalidated
        action = lambda: self.p1_affinities[0].delete()
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profiles[0].id)
        self.get_and_assert_query_count(url, action, 2, 0)
        # recreate the affinity
        self.p1_affinities[0] = Affinity.objects.create(profile=self.profiles[0], brand=self.brands[0])
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brands[0].id)
        self.get_and_assert_query_count(url, action, 2, 0)

    def test_create_affinity_clear_cache(self):
        # test that by creating an affinity, both get profiles by brand'
        # and 'get brands by profile' api will be invalidated
        action = lambda: Affinity.objects.create(brand=self.brands[2], profile=self.profiles[1])
        url = "%s?profile_id=%s" % (reverse('affinity-list'), self.profiles[1].id)
        self.get_and_assert_query_count(url, action, 2, 0)

        # delete the affinity we just created
        Affinity.objects.get(brand=self.brands[2], profile=self.profiles[1]).delete()
        url = "%s?brand_id=%s" % (reverse('affinity-list'), self.brands[2].id)
        self.get_and_assert_query_count(url, action, 2, 0)

