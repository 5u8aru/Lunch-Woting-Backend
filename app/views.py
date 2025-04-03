from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils.timezone import now
from .models import Restaurant, Menu, Vote, User
from .serializers import RestaurantSerializer, MenuSerializer, VoteSerializer, UserSerializer, UserRegistrationSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()  # Explicitly define the queryset
    serializer_class = MenuSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        today = now().strftime('%a').lower()  # Отримуємо поточний день тижня (наприклад, "mon")
        return Menu.objects.filter(restaurant_id=restaurant_id, day_of_week=today)

    def create(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        request.data['restaurant'] = restaurant_id  # Автоматично додаємо restaurant_id до запиту

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """Отримати меню ресторану на сьогодні"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()  # Explicitly define the queryset
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get votes for today's menus.
        """
        today = now().strftime('%a').lower()  # Get today's day of the week (e.g., "mon")
        return Vote.objects.filter(menu__day_of_week=today).select_related('menu', 'menu__restaurant')

    def create(self, request, *args, **kwargs):
        """
        Add a vote for a restaurant.
        """
        try:
            user = request.user
            restaurant_id = request.data.get('restaurant')
            api_version = request.headers.get('api-version', '1')  # Default to version 1 if not provided

            # Check if the restaurant exists
            if not Restaurant.objects.filter(id=restaurant_id).exists():
                return Response({"error": "Ресторан не існує."}, status=status.HTTP_400_BAD_REQUEST)

            # Determine the day based on the API version
            if api_version == '1':
                day_of_week = request.data.get('day_of_week')
                if not day_of_week:
                    return Response({"error": "Потрібно вказати день тижня."}, status=status.HTTP_400_BAD_REQUEST)
            elif api_version == '2':
                day_of_week = now().strftime('%a').lower()  # Automatically use today's day
            else:
                return Response({"error": "Непідтримувана версія API."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the restaurant has a menu for the specified day
            menu = Menu.objects.filter(restaurant_id=restaurant_id, day_of_week=day_of_week).first()
            if not menu:
                return Response({"error": "У цього ресторану немає меню на вказаний день."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has already voted for the specified day
            if Vote.objects.filter(user=user, menu__day_of_week=day_of_week).exists():
                return Response({"error": "Ви вже голосували за цей день."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the vote
            vote = Vote.objects.create(user=user, menu=menu)
            return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        Get voting results for today's menus.
        """
        votes = self.get_queryset()
        results = {}

        for vote in votes:
            restaurant_name = vote.menu.restaurant.name
            dish_name = vote.menu.dish
            key = f"{dish_name} ({restaurant_name})"
            if key not in results:
                results[key] = 0
            results[key] += 1

        return Response({"results": results}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_all(self, request):
        """
        Delete all existing votes.
        """
        deleted_count, _ = Vote.objects.all().delete()
        return Response({"message": f"Deleted {deleted_count} votes."}, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Додаємо явно queryset
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Щоб користувач бачив тільки свій профіль
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Endpoint для отримання даних про поточного користувача.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        Endpoint для реєстрації користувача.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
