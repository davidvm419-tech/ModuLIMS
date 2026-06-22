from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lims.constants import events_dict
from .models import Client, SampleType, Sample, SampleTraceability
from .serializers import ClientSerializer, SampleTypeSerializer, SampleSerializer, SampleTraceabilitySerializer   
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
   

STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar la muestra.'

# view sets hide the underlying implementation of  CRUD details
class ClientViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire Client endpoint for the frontend
    GET  /api/clients/ (list)
    POST /api/clients/ (create)
    GET  /api/clients/<int:id>/ (retrieve)
    PUT  /api/clients/<int:id>/ (update)
    PATCH /api/clients/<int:id>/ (partial_update)
    DELETE /api/clients/<int:id>/ (destroy)
    ModelViewSet hides the logic of list, create, retrieve, update, partial_update
    and destroy unless you override them or create a custom one.
    """
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.filter(is_active=True)
    serializer_class = ClientSerializer 
    pagination_class = None # pagination disabled for frontend selects when creating samples

    # it gives the DELETE method 
    def destroy(self, request, *args, **kwargs):
        """
        In this case we "delete" the data by updating the active status
        so the default behavior is overwrite
        """

        client = self.get_object()
        client.is_active = False
        client.save()

        return Response(
            {'message': f"Cliente {client.name} desactivado con éxito."},
            status=status.HTTP_200_OK
        )
    

class SampleTypeViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire sample type endpoint for the frontend
    GET  /api/sample-type/ (list)
    POST /api/sample-type/ (create)
    GET  /api/sample-type/<int:id>/ (retrieve)
    PUT  /api/sample-type/<int:id>/ (update)
    PATCH /api/sample-type/<int:id>/ (partial_update)
    DELETE /api/sample-type/<int:id>/ (destroy)
    ModelViewSet hides the logic of list, create, retrieve, update, partial_update
    and destroy unless you override them or create a custom one.
    """
    permission_classes = [IsAuthenticated]
    queryset = SampleType.objects.filter(is_active=True)
    serializer_class =SampleTypeSerializer
    pagination_class = None # pagination disabled for frontend selects when creating samples

    def destroy(self, request, *args, **kwargs):
        """
        In this case we "delete" the data by updating the active status
        so the default behavior is overwrite
        """

        category = self.get_object()
        category.is_active = False
        category.save()

        return Response(
            {"message": f"categoria {category.name} desactivada con éxito."},
            status=status.HTTP_200_OK
        )

class SampleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    """
    This view will get the entire sample type endpoint for the frontend
    GET  /api/sample/ (list)
    POST /api/sample/ (create)
    GET  /api/sample/<int:id>/ (retrieve)
    PUT  /api/sample/<int:id>/ (update)
    PATCH /api/sample/<int:id>/ (partial_update)
    DELETE /api/sample/<int:id>/ (destroy)
    GenericViewSet with mixins give a template for the basic CRUD 
    and custom behavior for the desired methods.
    """
    permission_classes = [IsAuthenticated]
    queryset = Sample.objects.filter(is_active=True)
    serializer_class = SampleSerializer

    def create(self, request, *args, **kwargs):
        """"
        custom sample code to have category prefix-year-xxxx
        example: PT2026-1
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # create code and traceability log
            try:
                # failsafe to avoid errant data when creating a new sample
                with transaction.atomic():
                    sample = serializer.save()
                    
                    # get date, and last valid sample
                    date =timezone.now()
                    year = date.year
                    last_sample = Sample.objects.filter(
                        code__contains=str(year), 
                        type=sample.type
                    ).exclude(id=sample.id).order_by('-id').first()
                    
                    # get prefix for code assignment
                    prefix = sample.type.prefix
                    
                    # check to assign the new code
                    if last_sample and last_sample.code:     
                        try:
                            # get previous sample code
                            code_parts = last_sample.code.split('-')
                            previous_code = int(code_parts[1])
                            next_code = previous_code + 1

                        except (IndexError, ValueError):
                            next_code = 1
                    else:
                        next_code = 1
                    
                    # assign code to sample
                    sample.code = f"{prefix}{year}-{next_code}"  
                    
                    sample.save()

                    # assign sample assays
                    '''
                    add when assay module is implemented
                    ''' 

                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = events_dict['sample_creation'],
                    )

                    return Response(self.get_serializer(sample).data, status=status.HTTP_201_CREATED)
                
            except Exception as err:
                return Response(
                    {'error': f"Error en el ingreso de la muestra: {str(err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    def update(self, request, pk=None, *args, **kwargs):
        """
        Any update must receive a reason for traceability log 
        frontend must send this traceability event along with the
        data to update.
        """
        queryset = self.get_queryset()
        sample = get_object_or_404(queryset, pk=pk)
        
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        serializer = self.get_serializer(sample, data=request.data)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    serializer.save()
            
                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE MUESTRA: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as err:
                return Response(
                    {'error': f'error actualizando la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        
        queryset = self.get_queryset()
        sample = get_object_or_404(queryset, pk=pk)
        
        serializer = self.get_serializer(sample, data=request.data, partial=True)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    serializer.save()
            
                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE MUESTRA: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as err:
                return Response(
                    {'error': f'error actualizando la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        In this case we "delete" the data by updating the active status
        and add a traceability log from the user to why this sample
        has to be deactivated.
        """
        queryset = self.get_queryset()
        sample = get_object_or_404(queryset, pk=pk)
        
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        # deactivate sample and create traceability log
        try:
            with transaction.atomic():
                sample.is_active = False
                sample.save()
        
                # traceability log
                SampleTraceability.objects.create(
                    sample = sample,
                    user_responsible = request.user,
                    event = f"INACTIVACIÓN DE MUESTRA: {traceability_log}",
                )

                return Response(
                    {"message": f"Muestra {sample.code} desactivada con éxito."}, 
                    status=status.HTTP_200_OK
                )
            
        except Exception as err:
            return Response(
                {'error': f'error desactivando la muestra: {str(err)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class SampleTraceabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire traceability endpoint for the frontend
    api/traceability
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = SampleTraceability.objects.all()
    serializer_class = SampleTraceabilitySerializer 

    # decorator to tell DRF that use the global pagination and to add a custom readable url
    @action(detail=False, methods=['get'], url_path=r'sample/(?P<sample_id>\d+)')
    def sample_traceability(self, request, sample_id=None):
        """
        The read only view set gives the predefined methods,
        here we get data by sample id thanks to that inheritance.
        """
        # avoid requests with none existing samples
        get_object_or_404(Sample, pk=sample_id)

        queryset = SampleTraceability.objects.filter(sample=sample_id)
        
        # tell DRF that paginate the queryset based n the global settings
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)    
            return self.get_paginated_response(serializer.data)
        
        # safeguard in case pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)       
    