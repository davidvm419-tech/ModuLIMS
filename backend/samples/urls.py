from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import SampleTypeViewSet, SampleViewSet, SampleTraceabilityViewSet


"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

# samples types urls
router.register(r'sample-types', SampleTypeViewSet, basename='sample-type')

# samples urls
router.register(r'samples', SampleViewSet, basename='sample')

# samples traceability urls
router.register(r'samples-traceability', SampleTraceabilityViewSet, basename='sample-traceability')

urlpatterns = [
    path('', include(router.urls)),
]
