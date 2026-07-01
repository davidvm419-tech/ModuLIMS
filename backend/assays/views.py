from django.apps import apps
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
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():

            try:
                # save data into assays and create the traceability log
                with  transaction.atomic():
                    assay = serializer.save()
                
                    AssayTraceability.objects.create(
                        assay = assay,
                        user_responsible = request.user,
                        event =  events_dict['assay_creation'],
                    )   

                    return Response(serializer.data, status=status.HTTP_201_CREATED) 
                
            except  Exception as err:
                return Response(
                    {'error': f"Error en la creación  del ensayo: {str(err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Any update must receive a reason for traceability log 
        frontend must send this traceability event along with the
        data to update.
        """
        traceability_log = request.data.get('justification', '').strip().upper()

        if not traceability_log:
            return Response(
                    {'error': STANDARD_ERROR_MESSAGE},
                    status=status.HTTP_400_BAD_REQUEST
                )

        assay = self.get_object()

        # check that request is PATCH or PUT to use the corresponding method
        partial = kwargs.pop('partial', False) or request.method == 'PATCH'

        serializer= self.get_serializer(assay,  data=request.data,  partial=partial)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    serializer.save()
            
                    # traceability log
                    AssayTraceability.objects.create(
                        assay = assay,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE ENSAYO: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as err:
                return Response(
                    {'error': f'error actualizando la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request,  pk=None):
        """
        In this case we "delete" the data by updating the active status
        and add a traceability log from the user to why this assay
        is been deactivated.
        """        
        traceability_log = request.data.get('justification', '').strip().upper()
        
        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        assay = self.get_object()
        
        # deactivate sample and create traceability log
        try:
            with transaction.atomic():
                assay.is_active = False
                assay.save()
        
                # traceability log
                AssayTraceability.objects.create(
                    assay = assay,
                    user_responsible = request.user,
                    event = f"INACTIVACIÓN DE ENSAYO: {traceability_log}",
                )

                return Response(
                    {"message": f"Ensayo {assay.name} desactivado con éxito."}, 
                    status=status.HTTP_200_OK
                )
            
        except Exception as err:
            return Response(
                {'error': f'error desactivando el ensayo: {str(err)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class AssayTraceabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire traceability endpoint for the frontend
    api/assay-traceability
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = AssayTraceability.objects.all()
    serializer_class = AssayTraceabilitySerializer

    # decorator to tell DRF that use the global pagination and to add a custom readable url
    @action(detail=False, methods=['get'], url_path=r'assay/(?P<assay_id>\d+)')
    def sample_traceability(self, request, assay_id=None):
        """
        The read only view set gives the predefined methods,
        here we get data by sample id thanks to that inheritance.
        """
        # avoid requests with none existing assays
        get_object_or_404(Assay, pk=assay_id)

        queryset = AssayTraceability.objects.filter(assay=assay_id)
        
        # tell DRF that paginate the queryset based n the global settings
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)    
            return self.get_paginated_response(serializer.data)
        
        # safeguard in case pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)       
    

class SampleAssayViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire user personal endpoint for the frontend
    GET  /api/sample-assay/<int:id>/ (retrieve)
    PATCH /api/sample-assay/<int:id>/ (partial_update)
    DELETE /api/sample-assay/int:id> (destroy)
    modelViewSet gives a template for the basic CRUD 
    and custom behavior for the desired methods.
    """
    permission_classes = [IsAuthenticated]
    queryset = SampleAssay.objects.all()
    serializer_class = SampleAssaySerializer

    http_method_names = ['get', 'patch', 'delete', 'options', 'head']

    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        Any update must receive a reason for traceability log 
        frontend must send this traceability event along with the
        data to update.
        """
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        sample_assay = self.get_object()
        
        serializer = self.get_serializer(sample_assay, data=request.data, partial=True)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    
                    # get the sample traceability model from samples module
                    SampleTraceabilityModel = apps.get_model('samples', 'SampleTraceability')

                    # traceability log
                    SampleTraceabilityModel.objects.create(
                        sample = sample_assay.sample,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE ENSAYO DE MUESTRA: {traceability_log}",
                    )

                    serializer.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
            
            except Exception as err:
                return Response(
                    {'error': f'error actualizando ensayos  de muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        In this case we delete the data to avoid a messy join table, 
        but keep a traceability log into the sample.
        """  
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        sample_assay = self.get_object()
        assay_name = sample_assay.assay.name

        try:
            with transaction.atomic():
                # get the sample traceability model from samples module
                SampleTraceabilityModel = apps.get_model('samples', 'SampleTraceability')

                # traceability log
                SampleTraceabilityModel.objects.create(
                    sample = sample_assay.sample,
                    user_responsible = request.user,
                    event = f"ELIMINACIÓN DE ENSAYO DE MUESTRA: {traceability_log}",
                )

                sample_assay.delete()

                return Response(
                    {"message": f"Ensayo {assay_name} eliminado con éxito."}, 
                    status=status.HTTP_200_OK
                )
        
        except Exception as err:
            return Response(
                {'error': f'error actualizando ensayos  de muestra: {str(err)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
