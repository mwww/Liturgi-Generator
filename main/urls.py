from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutUs, name='aboutUs'),
    path('generator/', views.generator, name='generator'),
]
