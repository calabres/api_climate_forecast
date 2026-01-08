from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .analysis import get_skill_matrix, get_best_models
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

def index(request):
    return render(request, 'core/index.html')

@extend_schema(
    parameters=[
        OpenApiParameter("lat", OpenApiTypes.FLOAT, OpenApiParameter.QUERY, description="Latitude value", required=True),
        OpenApiParameter("lon", OpenApiTypes.FLOAT, OpenApiParameter.QUERY, description="Longitude value", required=True),
        OpenApiParameter("month", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Base month (1-12 or 'auto')", required=False, default="1"),
    ],
    responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    description="Returns the skill matrix (Correlation and Bias) for all models at a specific point."
)
@api_view(['GET'])
def api_skill(request):
    try:
        lat = float(request.query_params.get('lat'))
        lon = float(request.query_params.get('lon'))
        raw_month = request.query_params.get('month', '1')
        
        if raw_month == 'auto':
            month = 'auto'
        else:
            month = int(raw_month)
        
        data = get_skill_matrix(lat, lon, month)
        
        if "error" in data:
            return JsonResponse(data, status=400) 
            
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': f"Missing or invalid parameters: {str(e)}"}, status=400)

@extend_schema(
    parameters=[
        OpenApiParameter("lat", OpenApiTypes.FLOAT, OpenApiParameter.QUERY, description="Latitude value", required=True),
        OpenApiParameter("lon", OpenApiTypes.FLOAT, OpenApiParameter.QUERY, description="Longitude value", required=True),
        OpenApiParameter("month", OpenApiTypes.STR, OpenApiParameter.QUERY, description="Base month (1-12 or 'auto')", required=False, default="1"),
    ],
    responses={200: OpenApiTypes.OBJECT},
    description="Returns the best model recommendation and calibrated forecast for each lead time."
)
@api_view(['GET'])
def api_smart_forecast(request):
    try:
        lat = float(request.query_params.get('lat'))
        lon = float(request.query_params.get('lon'))
        raw_month = request.query_params.get('month', '1')
        
        if raw_month == 'auto':
            month = 'auto'
        else:
            month = int(raw_month)
        
        data = get_best_models(lat, lon, month)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': f"Missing or invalid parameters: {str(e)}"}, status=400)
