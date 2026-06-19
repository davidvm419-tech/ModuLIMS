from django.urls import path, include
from rest_framework.routers import DefaultRouter
from  .views import UserAdminViewSet, UserProfileViewSet, UserTraceabilityViewSet    
# from .views import 


"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

# user administration urls
router.register(r'users-administration', UserAdminViewSet, basename='user-administration')

# self user edition urls
router.register(r'users', UserProfileViewSet, basename='user')

# users traceability urls
router.register(r'users-traceability', UserTraceabilityViewSet, basename='user-traceability')


urlpatterns = [
    path('', include(router.urls)),
]
