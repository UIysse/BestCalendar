from django.urls import path
from . import views
from .views import update_employee_order
#from .views import get_badge_hours

urlpatterns = [
    path('', views.home, name="home"),
    path('contact/', views.contact, name='contact'),
    path('success/', views.success, name='success'),
    path('team-members/', views.team_members_page, name='team_members_page'),
    path('badgeuse/', views.badgeuse, name='badgeuse'),
    path('badge/', views.badge_log, name='badge_log'),
    path('create_employe/', views.create_employe, name='create_employe'),
    path('modify_employe/<int:employe_id>/', views.modify_employe, name='modify_employe'),
    path("update-shift/", views.update_shift, name="update_shift"),
    path('planning/', views.planning, name='planning'),  # Without parameters
    path('planning/<int:year>/<int:week>/', views.planning, name='planning_with_params'),  # With parameters
    path('planning/delete/', views.delete_employe, name='delete_employe'),
    path('admin/', views.admin_approval, name='admin_approval'),
    path("update-employee-order/", update_employee_order, name="update_employee_order"),
    #path('api/get-badge-hours/<int:employe_id>/<str:date>/', get_badge_hours, name='get_badge_hours'),
]