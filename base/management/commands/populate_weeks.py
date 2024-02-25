from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime
from ...models import Week  # Adjust the import path according to your project structure

class Command(BaseCommand):
    help = 'Populates the database with week entries for the current year'

    def handle(self, *args, **options):
        # Step 1: Delete existing entries
        Week.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing week entries have been deleted.'))

        # Step 2: Repopulate
        current_year = timezone.now().year
        for week in range(1, 53):  # Adjust based on the actual number of weeks needed
            first_day = datetime.datetime.strptime(f'{current_year} {week} 1', '%G %V %u').date()
            Week.objects.get_or_create(week_number=week, defaults={'first_day': first_day})

        self.stdout.write(self.style.SUCCESS('Successfully repopulated week entries'))
