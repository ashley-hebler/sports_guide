from django.contrib import admin

from .models import Game, Team, League, Sport, Network

admin.site.register(Game)
admin.site.register(Team)
admin.site.register(League)
admin.site.register(Sport)
admin.site.register(Network)