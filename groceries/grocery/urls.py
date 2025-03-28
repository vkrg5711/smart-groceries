from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create_list/', views.create_list, name='create_list'),
    path('list/<int:list_id>/edit/', views.edit_list, name='edit_list'),
    path('list/<int:list_id>/delete/', views.delete_list, name='delete_list'),
    path('list/<int:list_id>/share/', views.get_share_link, name='get_share_link'),
    path('share/<str:token>/', views.share_list, name='share_list'),
]
