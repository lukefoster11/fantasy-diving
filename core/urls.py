from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.overview, name='overview'),
    path('meet=<int:meet_id>/', views.events, name='events'),
    path('event=<int:event_id>/', views.entries, name='entries'),
    path('event=<int:event_id>/createEntry/', views.createEntry, name='createEntry'),
]