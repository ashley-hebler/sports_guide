from django.db import models

# Create your models here.
# games have one league
# games have one sport
# games have many teams
class Game(models.Model):
    time = models.DateTimeField('game time')
    name = models.CharField(max_length=200)
    league = models.ForeignKey('League', on_delete=models.CASCADE, null=True)
    sport = models.ForeignKey('Sport', on_delete=models.CASCADE, null=True)
    teams = models.ManyToManyField('Team')
    networks = models.ManyToManyField('Network')


    def __str__(self):
        return self.name

#teams have many games
#teams have one league
#teams have one sport
class Team(models.Model):
    name = models.CharField(max_length=200)
    league = models.ForeignKey('League', on_delete=models.CASCADE, null=True)
    rank = models.IntegerField(null=True)
    conference = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


#leagues have many games
#leagues have many teams
#leagues have one sport
class League(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey('Sport', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

#sports have many leagues
#sports have many games
#sports have many teams
class Sport(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Network(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name