"""contest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from contest_app import views

urlpatterns = [
    re_path(r'^give_users/(?P<name>\w+)/$', views.give_users, name='give_users'),
    path('match_answers/', views.match_answers, name='match_answers'),
    path('judging_page/', views.judging_page, name='judging_page'),
    re_path(r'^quiz_answers/(?P<user_id>\w+)/$', views.quiz_answers, name='quiz_answers'),
    path('quiz_questions/', views.quiz_questions, name='quiz_questions'),
    re_path(r'^quiz/(?P<user_id>\w+)/$', views.quiz, name='quiz'),
    path('register/', views.register, name='register'),
    path('admin_register/', views.admin_register, name='admin_register'),
    re_path(r'^uploads/(?P<user_id>\w+)/$', views.uploads, name='uploads'),
    path('slokas/', views.sloka, name='sloka'),
    path('verify_payment', views.verify_payment, name='verify_payment'),
    path('create_new_order', views.create_an_order, name='create_new_order'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index')
]
