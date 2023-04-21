from django.urls import path

from . import views

app_name = 'mainbot'

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path('stop/', views.stopporcess, name='stopporcess'),
    path('test/', views.test, name='test'),
    path('getremain/', views.getremain, name='getremain'),

]
