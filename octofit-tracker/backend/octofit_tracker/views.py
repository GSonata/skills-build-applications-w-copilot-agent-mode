from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import User, Team, Activity, Workout, Leaderboard
from .serializers import (
    UserSerializer, TeamSerializer, ActivitySerializer,
    WorkoutSerializer, LeaderboardSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a team"""
        team = self.get_object()
        members = team.members.all()
        serializer = UserSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        """Get team leaderboard"""
        team = self.get_object()
        team_members = team.members.all()
        leaderboard = Leaderboard.objects.filter(user__in=team_members).order_by('-score')
        serializer = LeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        """Get all activities for a user"""
        user = self.get_object()
        activities = user.activities.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(activities, request)
        serializer = ActivitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def leaderboard_entry(self, request, pk=None):
        """Get user's leaderboard entry"""
        user = self.get_object()
        try:
            leaderboard = user.leaderboard_entry
            serializer = LeaderboardSerializer(leaderboard)
            return Response(serializer.data)
        except Leaderboard.DoesNotExist:
            return Response(
                {'error': 'No leaderboard entry found'},
                status=status.HTTP_404_NOT_FOUND
            )


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['type', 'user__username']
    ordering_fields = ['activity_date', 'duration', 'calories_burned']
    ordering = ['-activity_date']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filter activities by user if query param is provided"""
        queryset = Activity.objects.all()
        user_id = self.request.query_params.get('user_id', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        """Get current user's activities"""
        activities = Activity.objects.filter(user=request.user).order_by('-activity_date')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(activities, request)
        serializer = ActivitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's activities for current user"""
        from django.utils import timezone
        today = timezone.now().date()
        activities = Activity.objects.filter(
            user=request.user,
            activity_date__date=today
        ).order_by('-activity_date')
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all()
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'target_muscle_groups']
    ordering_fields = ['difficulty', 'duration', 'created_at']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filter workouts by difficulty if query param is provided"""
        queryset = Workout.objects.all()
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty is not None:
            queryset = queryset.filter(difficulty=difficulty)
        return queryset

    @action(detail=False, methods=['get'])
    def by_difficulty(self, request):
        """Get workouts grouped by difficulty"""
        difficulties = ['easy', 'medium', 'hard']
        result = {}
        for difficulty in difficulties:
            result[difficulty] = WorkoutSerializer(
                Workout.objects.filter(difficulty=difficulty),
                many=True
            ).data
        return Response(result)


class LeaderboardViewSet(viewsets.ModelViewSet):
    queryset = Leaderboard.objects.all().order_by('-score')
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['score', 'rank', 'total_activities']
    ordering = ['-score']
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['get'])
    def current_user(self, request):
        """Get current user's leaderboard entry"""
        try:
            leaderboard = request.user.leaderboard_entry
            serializer = LeaderboardSerializer(leaderboard)
            return Response(serializer.data)
        except Leaderboard.DoesNotExist:
            return Response(
                {'error': 'No leaderboard entry found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def team_leaderboard(self, request):
        """Get team leaderboard for current user"""
        if not request.user.team:
            return Response(
                {'error': 'User is not part of a team'},
                status=status.HTTP_400_BAD_REQUEST
            )
        team_members = request.user.team.members.all()
        leaderboard = Leaderboard.objects.filter(
            user__in=team_members
        ).order_by('-score')
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(leaderboard, request)
        serializer = LeaderboardSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'])
    def recalculate_scores(self, request):
        """Recalculate all leaderboard scores based on activities"""
        users = User.objects.all()
        for user in users:
            activities = user.activities.all()
            total_activities = activities.count()
            total_duration = sum([a.duration for a in activities])
            calories = sum([a.calories_burned or 0 for a in activities])

            leaderboard, created = Leaderboard.objects.get_or_create(user=user)
            leaderboard.total_activities = total_activities
            leaderboard.total_duration = total_duration
            leaderboard.score = total_activities * 100 + total_duration
            leaderboard.save()

        # Update ranks
        leaderboard_entries = Leaderboard.objects.all().order_by('-score')
        for rank, entry in enumerate(leaderboard_entries, 1):
            entry.rank = rank
            entry.save()

        return Response({'status': 'Scores recalculated'})
