from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import ClientViewSet


"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
