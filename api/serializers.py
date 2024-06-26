from datetime import date, timedelta
from rest_framework import serializers
from games.models import Game, Sport, Team


class GameSerializer(serializers.ModelSerializer):
    time_formatted = serializers.SerializerMethodField()
    date_formatted = serializers.SerializerMethodField()
    class Meta:
        model = Game
        # display nested fields
        depth = 1
        fields = ['id', 'time', 'time_formatted', 'date_formatted', 'name', 'league', 'sport', 'teams', 'networks', 'event', 'watch_links']
    
    def get_time_formatted(self, obj):
        #hour:minute am/pm no leading zeros
        local_time = obj.time.astimezone()    
        return local_time.astimezone().strftime("%-I:%M %p")
    
    def get_date_formatted(self, obj):
        # date no leading zeros and day of week
        local_time = obj.time.astimezone()
        return local_time.astimezone().strftime("%A, %B %-d, %Y")


class SportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        depth = 1
        fields = ['name', 'id']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        depth = 1
        fields = ['name', 'league', 'id', 'rank', 'conference']    
