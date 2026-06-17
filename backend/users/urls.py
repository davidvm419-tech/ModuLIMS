from django.urls import path, include
from rest_framework.routers import DefaultRouter    
# from .views import 


"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  


urlpatterns = [
    path('', include(router.urls)),
]
