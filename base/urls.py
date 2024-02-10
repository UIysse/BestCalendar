from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('contact/', views.contact, name='contact'),
    path('success/', views.success, name='success'),
    path('team-members/', views.team_members_page, name='team_members_page'),
    path('create_employe/', views.create_employe, name='create_employe'),
    path('modify_employe/<int:employe_id>/', views.modify_employe, name='modify_employe'),
    path('planning/', views.planning, name='planning'),  # Without parameters
    path('planning/<int:year>/<int:week>/', views.planning, name='planning_with_params'),  # With parameters
    path('planning/delete/', views.delete_employe, name='delete_employe'),
    path('admin/', views.admin_approval, name='admin_approval'),
]