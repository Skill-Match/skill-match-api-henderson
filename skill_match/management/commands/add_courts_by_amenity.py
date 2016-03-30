from django.core.management import BaseCommand
from django.db.models import Q
from skill_match.models import HendersonPark, Court


class Command(BaseCommand):
    """
        This command creates Court objects with a foreign key to HendersonPark
        objects. It checks the amenity_set of the HendersonPark for a
    """
    def handle(self, *args, **options):

        parks = HendersonPark.objects.all()
        count = 0
        # For each park, check to see if the amenity set contains a sport.
        # If that Court does not already exist, create a new Court object
        for park in parks:
            if park.amenity_set.filter(name__icontains='tennis'):
                # Only create new court if court does not exist already
                if not park.court_set.filter(sport='Tennis'):
                    Court.objects.create(park=park, sport='Tennis')
                    count += 1
            if park.amenity_set.filter(name__icontains='basketball'):
                if not park.court_set.filter(sport='Basketball'):
                    Court.objects.create(park=park, sport='Basketball')
                    count += 1
            if park.amenity_set.filter(name__icontains='volleyball'):
                if not park.court_set.filter(sport='Volleyball'):
                    Court.objects.create(park=park, sport='Volleyball')
                    count += 1
            if park.amenity_set.filter(name__icontains='pickleball'):
                if not park.court_set.filter(sport='Pickleball'):
                    Court.objects.create(park=park, sport='Pickleball')
                    count += 1
            if park.amenity_set.filter(
                            Q(name__icontains='multi-purpose field') |
                            Q(name__icontains='multi-use field')):
                if not park.court_set.filter(sport='Football'):
                    Court.objects.create(park=park, sport='Football')
                    count += 1
                if not park.court_set.filter(sport='Soccer'):
                    Court.objects.create(park=park, sport='Soccer')
                    count += 1

        self.stdout.write("{} Courts added".format(count))
