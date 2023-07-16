from django.core.management.base import BaseCommand, CommandError


from datetime import datetime
from django.utils import timezone

from games.models import Game, League
from .utils import str2bool

class Command(BaseCommand):
    """
    Delete games from a certain league or all games from past
    """
    help = 'Clean games'

    def add_arguments(self, parser):
        parser.add_argument('--all_games', type=str, help='Delete all games past and future', default='False')
        parser.add_argument('--league', type=str, help='Clean only league passed', default='')
    
    def handle(self, *args, **options):

        all_games = options['all_games']
        if all_games:
            all_games = str2bool(all_games)
        league = options['league']
        league_id = None
        games = None
        if league:
            try:
                league_id = League.objects.get(name=league).id
            except League.DoesNotExist:
                raise CommandError('League "%s" does not exist' % league)

        # delete either all games or games from past depending on params
        if all_games:
            if league_id:
                games = Game.objects.filter(league=league_id)
                print(f"Deleting all {games.count()} games from league: {league}")
            else:
                games = Game.objects.all()
                print(f"Deleting all {games.count()} games")
        else:
            # delete games from past
            one_week_ago = timezone.make_aware(datetime.now(), timezone.get_default_timezone()) - timezone.timedelta(days=7)
            if league_id:
                games = Game.objects.filter(league=league_id, time__lte=one_week_ago)
                print(f"Deleting old {games.count()} games from league: {league}")
            else:
                games = Game.objects.filter(time__lte=one_week_ago)
                print(f"Deleting old {games.count()} games")
        if games:
            games.delete()
        else:
            print("No games to delete")

