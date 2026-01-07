from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/skill', views.api_skill, name='api_skill'),
    path('api/smart_forecast', views.api_smart_forecast, name='api_smart_forecast'),
]
