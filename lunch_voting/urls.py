from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.views import RestaurantViewSet, MenuViewSet, VoteViewSet, UserViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'votes', VoteViewSet)
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/restaurants/<int:restaurant_id>/menus/', MenuViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/votes/', VoteViewSet.as_view({'post': 'create', 'get': 'list'})),  # Added endpoint
    path('api/votes/delete_all/', VoteViewSet.as_view({'delete': 'delete_all'})),  # Added endpoint
]
