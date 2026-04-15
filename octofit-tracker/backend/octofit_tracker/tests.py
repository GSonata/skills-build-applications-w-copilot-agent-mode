from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Team, Activity, Workout, Leaderboard
from datetime import datetime, timedelta

User = get_user_model()


class TeamAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.team1 = Team.objects.create(name='Team A', description='First team')
        self.team2 = Team.objects.create(name='Team B', description='Second team')

    def test_list_teams(self):
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_create_team_authenticated(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.client.force_authenticate(user=user)
        data = {'name': 'Team C', 'description': 'New team'}
        response = self.client.post('/api/teams/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Team C')

    def test_create_team_unauthenticated(self):
        data = {'name': 'Team D', 'description': 'Another new team'}
        response = self.client.post('/api/teams/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_team(self):
        response = self.client.get(f'/api/teams/{self.team1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Team A')

    def test_team_members(self):
        user1 = User.objects.create_user(username='user1', email='user1@example.com', password='pass', team=self.team1)
        user2 = User.objects.create_user(username='user2', email='user2@example.com', password='pass', team=self.team1)
        response = self.client.get(f'/api/teams/{self.team1.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UserAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.team = Team.objects.create(name='Test Team')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            team=self.team
        )

    def test_list_users(self):
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_retrieve_user(self):
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_activities(self):
        self.client.force_authenticate(user=self.user)
        activity = Activity.objects.create(
            user=self.user,
            type='running',
            duration=30,
            distance=5.0
        )
        response = self.client.get(f'/api/users/{self.user.id}/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class ActivityAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_activity(self):
        data = {
            'user_id': self.user.id,
            'type': 'running',
            'duration': 30,
            'distance': 5.0,
            'calories_burned': 300
        }
        response = self.client.post('/api/activities/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['type'], 'running')

    def test_list_activities(self):
        Activity.objects.create(
            user=self.user,
            type='cycling',
            duration=45,
            distance=10.0
        )
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_my_activities(self):
        Activity.objects.create(
            user=self.user,
            type='swimming',
            duration=30
        )
        response = self.client.get('/api/activities/my_activities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_today_activities(self):
        today = datetime.now()
        Activity.objects.create(
            user=self.user,
            type='yoga',
            duration=60,
            activity_date=today
        )
        response = self.client.get('/api/activities/today/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_activity_requires_authentication(self):
        self.client.force_authenticate(user=None)
        data = {
            'user_id': self.user.id,
            'type': 'running',
            'duration': 30
        }
        response = self.client.post('/api/activities/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class WorkoutAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.workout = Workout.objects.create(
            name='Full Body Workout',
            description='Complete full body workout',
            difficulty='medium',
            duration=60,
            exercises='Squats, Push-ups, Rows, Pull-ups'
        )

    def test_list_workouts(self):
        response = self.client.get('/api/workouts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_workout(self):
        response = self.client.get(f'/api/workouts/{self.workout.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Full Body Workout')

    def test_workouts_by_difficulty(self):
        Workout.objects.create(
            name='Easy Stretch',
            description='Basic stretching',
            difficulty='easy',
            duration=20,
            exercises='Stretches'
        )
        response = self.client.get('/api/workouts/by_difficulty/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('easy', response.data)
        self.assertIn('medium', response.data)

    def test_filter_workouts_by_difficulty(self):
        response = self.client.get('/api/workouts/?difficulty=medium')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class LeaderboardAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass'
        )
        self.team = Team.objects.create(name='Test Team')
        self.user1.team = self.team
        self.user1.save()
        self.user2.team = self.team
        self.user2.save()

        self.leaderboard1 = Leaderboard.objects.create(
            user=self.user1,
            score=500,
            total_activities=10,
            total_duration=300,
            rank=1
        )
        self.leaderboard2 = Leaderboard.objects.create(
            user=self.user2,
            score=300,
            total_activities=5,
            total_duration=150,
            rank=2
        )

    def test_list_leaderboard(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_leaderboard_ordering(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # First entry should have higher score
        self.assertGreaterEqual(
            response.data['results'][0]['score'],
            response.data['results'][1]['score']
        )

    def test_current_user_leaderboard(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/leaderboard/current_user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.user1.id)

    def test_team_leaderboard(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/leaderboard/team_leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_leaderboard_requires_authentication(self):
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recalculate_scores(self):
        self.client.force_authenticate(user=self.user1)
        # Create some activities
        for i in range(3):
            Activity.objects.create(
                user=self.user1,
                type='running',
                duration=30,
                calories_burned=300
            )
        response = self.client.post('/api/leaderboard/recalculate_scores/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if scores were updated
        updated_leaderboard = Leaderboard.objects.get(user=self.user1)
        self.assertEqual(updated_leaderboard.total_activities, 3)


class APIRootTest(APITestCase):
    def test_api_root_endpoint(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('endpoints', response.data)
        self.assertIn('teams', response.data['endpoints'])
        self.assertIn('users', response.data['endpoints'])
        self.assertIn('activities', response.data['endpoints'])
        self.assertIn('workouts', response.data['endpoints'])
        self.assertIn('leaderboard', response.data['endpoints'])

    def test_root_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
