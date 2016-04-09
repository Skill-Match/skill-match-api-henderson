from django.core.management import BaseCommand
import geocoder
from skill_match.models import HendersonPark


class Command(BaseCommand):

    def handle(self, *args, **options):

        parks = HendersonPark.objects.all()
        count = 0
        for park in parks:
            if not park.location:
                g = geocoder.google(park.address + ' Henderson, NV')
                latitude = g.latlng[0]
                longitude = g.latlng[1]
                park.location = 'POINT(' + str(longitude) + ' ' + str(latitude) + ')'
                park.save()
                count += 1

        self.stdout.write("{} parks updated".format(count))

