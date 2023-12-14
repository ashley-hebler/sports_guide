from django.core.management.base import BaseCommand, CommandError

from games.models import Team

class Command(BaseCommand):
    """
    Delete games from a certain league or all games from past
    """
    help = 'Delete all teams'

    
    def handle(self, *args, **options):
        teams = Team.objects.all()
        print(f"Deleting all {teams.count()} teams")
        teams.delete()
        

