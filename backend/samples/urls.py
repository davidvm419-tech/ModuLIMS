from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import ClientViewSet, SampleTypeViewSet


"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

# client urls
router.register(r'clients', ClientViewSet, basename='client')

# samples categories urls
router.register(r'sample-category', SampleTypeViewSet, basename='sample-category')

urlpatterns = [
    path('', include(router.urls)),
]
