import random
from django.core.management.base import BaseCommand, CommandError
from core.models import Profile, Brand, Affinity


class Command(BaseCommand):
    help = 'Randomly generate some affinities for all profiles'

    def handle(self, *args, **options):
        affinities = []
        profiles = Profile.objects.all()
        brands = Brand.objects.all()
        Affinity.objects.all().delete()
        # max number of affinities per profile
        max_affinity_count = 100
        for profile in profiles:
            selected_brands = random.sample(brands, random.randint(0, max_affinity_count))
            affinities += [Affinity(profile=profile, brand=brand) for brand in selected_brands]

        Affinity.objects.bulk_create(affinities, 500)