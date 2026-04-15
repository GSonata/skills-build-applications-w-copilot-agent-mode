from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from octofit_tracker.models import Team, Activity, Leaderboard, Workout

class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        User = get_user_model()
        # Borrar datos existentes
        User.objects.all().delete()
        Team.objects.all().delete()
        Activity.objects.all().delete()
        Leaderboard.objects.all().delete()
        Workout.objects.all().delete()

        # Crear equipos
        marvel = Team.objects.create(name='Marvel')
        dc = Team.objects.create(name='DC')

        # Crear usuarios
        ironman = User.objects.create_user(username='ironman', email='ironman@marvel.com', password='1234', team=marvel)
        spiderman = User.objects.create_user(username='spiderman', email='spiderman@marvel.com', password='1234', team=marvel)
        batman = User.objects.create_user(username='batman', email='batman@dc.com', password='1234', team=dc)
        superman = User.objects.create_user(username='superman', email='superman@dc.com', password='1234', team=dc)

        # Crear actividades
        Activity.objects.create(user=ironman, type='run', duration=30)
        Activity.objects.create(user=spiderman, type='cycle', duration=45)
        Activity.objects.create(user=batman, type='swim', duration=60)
        Activity.objects.create(user=superman, type='run', duration=50)

        # Crear workouts
        Workout.objects.create(name='Cardio Blast', description='Intenso cardio', duration=40)
        Workout.objects.create(name='Strength Power', description='Fuerza total', duration=60)

        # Crear leaderboard
        Leaderboard.objects.create(user=ironman, score=100)
        Leaderboard.objects.create(user=spiderman, score=90)
        Leaderboard.objects.create(user=batman, score=95)
        Leaderboard.objects.create(user=superman, score=98)

        self.stdout.write(self.style.SUCCESS('Base de datos poblada con datos de prueba.'))
