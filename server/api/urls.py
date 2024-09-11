from django.urls import path
from . import views

urlpatterns = [
    path('',views.main),
    path('jamming/', views.JammingAPI.as_view()),
    path('traffic/', views.TrafficAPI.as_view()),
    path('warning/',views.WarningAPI.as_view()),
    path('handle/',views.HandleAPI.as_view()),
]