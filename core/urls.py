from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.overview, name='overview'),
    path('<int:meet_id>/', views.detail, name='detail'),
    path('<int:meet_id>/<int:event_id>', views.entries, name='entries')
]