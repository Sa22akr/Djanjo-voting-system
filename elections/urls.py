from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('vote/', views.vote, name='vote'),
    path('results/', views.results, name='results'),
]