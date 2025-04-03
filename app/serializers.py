from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Restaurant, Menu, Vote

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

    def validate(self, data):
        # Перевіряємо, чи вже існує меню для цього ресторану на цей день
        restaurant = data.get('restaurant')
        day_of_week = data.get('day_of_week')

        if Menu.objects.filter(restaurant=restaurant, day_of_week=day_of_week).exists():
            raise serializers.ValidationError("Меню для цього ресторану на цей день вже існує.")

        return data

class VoteSerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), write_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'user', 'menu', 'restaurant', 'created_at']
        read_only_fields = ['menu', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        restaurant = data.get('restaurant')

        # Check if the restaurant exists
        if not Restaurant.objects.filter(id=restaurant.id).exists():
            raise serializers.ValidationError("Ресторан не існує.")

        # Check if the restaurant has a menu for today
        today = now().strftime('%a').lower()
        menu = Menu.objects.filter(restaurant=restaurant, day_of_week=today).first()
        if not menu:
            raise serializers.ValidationError("У цього ресторану немає меню на сьогодні.")

        # Check if the user has already voted for today's menu
        if Vote.objects.filter(user=user, menu__day_of_week=today).exists():
            raise serializers.ValidationError("Ви вже голосували сьогодні.")

        data['menu'] = menu  # Automatically associate the vote with today's menu
        return data
