import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from django.core.management import BaseCommand
from skill_match.models import HendersonPark, Amenity


class Command(BaseCommand):
    """
        This command uses beautifulsoup4 to scrape the Henderson website of
        Park Names and amenities
    """

    def handle(self, *args, **options):

        # Get List of parks from Parks Henderson Parks homepage
        first_response = requests.get('http://www.cityofhenderson.com/henderson-'
                          'happenings/parks-and-trails/locations-and-features')
        soup = BeautifulSoup(first_response.content, 'html.parser')
        park_list = soup.find('ul', class_="sfNavVertical sfNavList")
        park_urls = []

        # Create List of url's for each park detail page
        for park in park_list.find_all('li'):
            park_urls.append('http://www.cityofhenderson.com' +
                             park.a.get('href'))

        count = 0
        amenity_count = 0

        # For each url to a park detail page, get the details, create a
        # Henderson Park object, and link amenities.
        for park_url in park_urls:
            response = requests.get(park_url)
            s5 = BeautifulSoup(response.content, 'html.parser')
            name = s5.h1.find_next_sibling('h2').string

            # Parse address accordingly to get address string
            address_block = s5.find('div', class_='sfContentBlock').contents[0]
            if address_block.name == 'p':
                address = address_block.contents[0]
            else:
                if address_block == NavigableString:
                    address = address_block
                else:
                    address = "No address provided"

            img = s5.find('div', id='page-box').img

            # Check to see if the park is already in the database
            already_exists = HendersonPark.objects.filter(name=name)
            if not already_exists:
                # Create the HendersonPark object
                this_park = HendersonPark.objects.create(name=name,
                                                         url=park_url,
                                                         address=address)
                # If there is an image, add it.
                if img:
                    img_src = 'http://www.cityofhenderson.com' + img['src']
                    this_park.img_url = img_src
                    this_park.save()

                # Count the number of park objects created.
                count += 1

                # Find all the amenities on the park detail page.
                h3_s = s5.find_all('h3')

                # If there is an 'h3' with the string Park Amenities, locate
                # the sibling list(ul) of amenities
                amenity_h3 = None
                for h3 in h3_s:
                    if h3.string == 'Park amenities' or h3.string == \
                            'Park Amenities':
                        amenity_h3 = h3
                if amenity_h3:
                    # Get sibling list of amenities
                    amenity_ul = amenity_h3.find_next_sibling('ul')

                    # For each amenity, parse accordingly to get string
                    for li in amenity_ul.find_all('li'):
                        if li.a:
                            if type(li.contents[0]) == Tag:
                                amenity_name = li.a.string
                            else:
                                amenity_name = li.contents[0] + li.a.string
                        else:
                            amenity_name = li.string

                        # Strip amenity of whitespace
                        amenity_name = amenity_name.strip().title()

                        # Check to see if amenity already exists
                        amenity_exists = Ammenity.objects.filter(
                                name=amenity_name)
                        # If it exists, use the existing amenity
                        if amenity_exists:
                            amenity = amenity_exists[0]
                        # Else create a new amenity
                        else:
                            amenity = Amenity.objects.create(
                                    name=amenity_name)
                            amenity_count += 1
                        # Add park to amenity's ManyToMany parks field
                        amenity.parks.add(this_park)
                        amenity.save()

        self.stdout.write("{} Henderson Parks {} Amenities added to Database"
                          .format(count, amenity_count))
