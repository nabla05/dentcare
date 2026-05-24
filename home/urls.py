from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('',          views.home,    name='home'),
    path('about/',    views.about,   name='about'),
    path('services/', views.services, name='services'),
    path('contact/',  views.contact, name='contact'),
    path('book/',     views.book,    name='book'),
    path('doctors/',  views.doctors, name='doctors'),
    path('blog/',     views.blog,    name='blog'),
]
