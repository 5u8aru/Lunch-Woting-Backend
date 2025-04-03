import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Restaurant, Menu, Vote
from django.utils.timezone import now

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)
    return _create_user

@pytest.fixture
def create_restaurant():
    def _create_restaurant(name):
        return Restaurant.objects.create(name=name)
    return _create_restaurant

@pytest.fixture
def create_menu():
    def _create_menu(restaurant, dish, day_of_week):
        return Menu.objects.create(restaurant=restaurant, dish=dish, day_of_week=day_of_week)
    return _create_menu

@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post('/api/users/register/', {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword123'
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['message'] == 'User registered successfully'

@pytest.mark.django_db
def test_get_restaurants(api_client, create_restaurant):
    create_restaurant('Restaurant A')
    create_restaurant('Restaurant B')
    response = api_client.get('/api/restaurants/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

@pytest.mark.django_db
def test_create_vote_api_version_1(api_client, create_user, create_restaurant, create_menu):
    user = create_user('testuser', 'testpassword')
    restaurant = create_restaurant('Restaurant A')
    create_menu(restaurant, 'Pizza', 'mon')
    api_client.force_authenticate(user=user)

    response = api_client.post('/api/votes/', {
        'restaurant': restaurant.id,
        'day_of_week': 'mon'
    }, HTTP_API_VERSION='1')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['menu'] is not None

@pytest.mark.django_db
def test_create_vote_api_version_2(api_client, create_user, create_restaurant, create_menu):
    user = create_user('testuser', 'testpassword')
    restaurant = create_restaurant('Restaurant A')
    create_menu(restaurant, 'Pizza', now().strftime('%a').lower())
    api_client.force_authenticate(user=user)

    response = api_client.post('/api/votes/', {
        'restaurant': restaurant.id
    }, HTTP_API_VERSION='2')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['menu'] is not None

@pytest.mark.django_db
def test_get_votes(api_client, create_user, create_restaurant, create_menu):
    user = create_user('testuser', 'testpassword')
    restaurant = create_restaurant('Restaurant A')
    menu = create_menu(restaurant, 'Pizza', now().strftime('%a').lower())
    Vote.objects.create(user=user, menu=menu)
    api_client.force_authenticate(user=user)

    response = api_client.get('/api/votes/')
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert len(response.data['results']) == 1

@pytest.mark.django_db
def test_delete_all_votes(api_client, create_user, create_restaurant, create_menu):
    user = create_user('testuser', 'testpassword')
    restaurant = create_restaurant('Restaurant A')
    menu = create_menu(restaurant, 'Pizza', now().strftime('%a').lower())
    Vote.objects.create(user=user, menu=menu)
    api_client.force_authenticate(user=user)

    response = api_client.delete('/api/votes/delete_all/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Deleted 1 votes.'
