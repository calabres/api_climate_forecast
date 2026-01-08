from django.contrib import admin
from django.urls import path
from core import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/skill', views.api_skill, name='api_skill'),
    path('api/smart_forecast', views.api_smart_forecast, name='api_smart_forecast'),
    
    # OpenAPI Schema & Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
