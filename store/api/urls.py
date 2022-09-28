from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from api.views import products, ProductDetailView, comments, APICategoryViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
router = DefaultRouter()
router.register('categories', APICategoryViewSet)

urlpatterns = [
    path('products/<int:pk>/comments/', comments),
    path('products/<int:pk>', ProductDetailView.as_view()),
    path('products/', products),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT authentication
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('drf-auth/', include('rest_framework.urls')),  # session based authentication
    re_path(r'^auth/', include('djoser.urls')),  # token based authentication
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]