from datetime import date, timedelta
from rest_framework import serializers
from games.models import Game, Sport


class GameSerializer(serializers.ModelSerializer):
    time_formatted = serializers.SerializerMethodField()
    date_formatted = serializers.SerializerMethodField()
    class Meta:
        model = Game
        # display nested fields
        depth = 1
        fields = ['id', 'time', 'time_formatted', 'date_formatted', 'name', 'league', 'sport', 'teams', 'networks']
    
    def get_time_formatted(self, obj):
        #hour:minute am/pm
        return obj.time.strftime("%I:%M %p")
    
    def get_date_formatted(self, obj):
        # date no leading zeros
        return obj.time.strftime("%B %-d, %Y")


class SportsSerializer(serializers.Serializer):
    class Meta:
        model = Sport
        fields = ['na']
    
        
