from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import ClientViewSet, ClientTraceabilityViewSet

"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

# clients urls
router.register(r'clients', ClientViewSet, basename='client')

#clients traceability urls
router.register(r'clients-traceability', ClientTraceabilityViewSet, basename='client-traceability')

urlpatterns = [
    path('', include(router.urls))
]
