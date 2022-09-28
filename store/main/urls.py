from django.urls import path

from .views import index, other_page, detail, StoreLoginView, profile, StoreLogoutView, ChangeInfoUserFormView, \
    UserPasswordChangeView, RegisterUserView, RegisterDoneView, user_activate, DeleteUserView, by_category, \
    profile_product_detail, profile_product_add, profile_product_change, profile_product_delete

app_name = 'main'

urlpatterns = [
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/profile/change/<int:pk>/', profile_product_change, name='profile_product_change'),
    path('accounts/profile/delete/<int:pk>/', profile_product_delete, name='profile_product_delete'),
    path('accounts/profile/add/', profile_product_add, name='profile_product_add'),
    path('accounts/profile/<int:pk>/', profile_product_detail, name='profile_product_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/profile/delete', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeInfoUserFormView.as_view(), name='profile_change'),
    path('accounts/login/', StoreLoginView.as_view(), name='login'),
    path('accounts/logout/', StoreLogoutView.as_view(), name='logout'),
    path('accounts/password/change', UserPasswordChangeView.as_view(), name='password_change'),
    path('<int:category_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_category, name='by_category'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]