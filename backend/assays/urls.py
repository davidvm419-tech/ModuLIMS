from django.urls import path, include
from rest_framework.routers import DefaultRouter    
from .views import AssayViewSet,  AssayTraceabilityViewSet, SampleAssayViewSet

"""
Router will create the paths for every method 
in the corresponding view
"""
router = DefaultRouter()  

# assays urls
router.register(r'assays', AssayViewSet, basename='assay')

# assays traceability urls
router.register(r'assays-traceability', AssayTraceabilityViewSet, basename='assay-traceability')

# sample assays  urls
router.register(r'samples-assays', SampleAssayViewSet, basename='sample-assay')


urlpatterns = [
    path('', include(router.urls))
]
