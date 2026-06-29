from django.db import transaction
from django.shortcuts import get_object_or_404
from lims.constants import events_dict
from .models import Assay, AssayTraceability, SampleAssay
from .serializers import AssaySerializer, AssayTraceabilitySerializer, SampleAssaySerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
   

STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar el ensayo.'


class  AssayViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire sample type endpoint for the frontend
    GET  /api/assay/ (list)
    POST /api/assay/ (create)
    GET  /api/assay/<int:id>/ (retrieve)
    PUT  /api/assay/<int:id>/ (update)
    PATCH /api/assay/<int:id>/ (partial_update)
    DELETE /api/assay/<int:id>/ (destroy)
    ModelViewSet hides the logic of list, create, retrieve, update, partial_update
    and destroy unless you override them or create a custom one.
    """
    permission_classes = [IsAuthenticated]
    queryset = Assay.objects.filter(is_active=True)
    serializer_class =  AssaySerializer
    pagination_class = None # pagination disabled for frontend selects when creating samples
    
    def create(self, request):
        """
        Add the assay creation into the traceability table
        """
        

class AssayTraceabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire traceability endpoint for the frontend
    api/assay-traceability
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = AssayTraceability.objects.all()
    serializer_class = AssayTraceabilitySerializer


class SampleAssayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire sample assays endpoint for the frontend
    api/sample-assay
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = SampleAssay.objects.all()
    serializer_class = SampleAssaySerializer
    