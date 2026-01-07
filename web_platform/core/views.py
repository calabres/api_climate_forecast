
from django.shortcuts import render
from django.http import JsonResponse
from .analysis import get_skill_matrix, get_best_models

def index(request):
    return render(request, 'core/index.html')

def api_skill(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        month = int(request.GET.get('month', 1))
        
        # Devuelve { 'acc': {...}, 'bias': {...} }
        data = get_skill_matrix(lat, lon, month)
        
        if "error" in data:
            return JsonResponse(data, status=400) # Enviar error como JSON
            
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_smart_forecast(request):
    try:
        lat = float(request.GET.get('lat'))
        lon = float(request.GET.get('lon'))
        month = int(request.GET.get('month', 1))
        
        data = get_best_models(lat, lon, month)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
