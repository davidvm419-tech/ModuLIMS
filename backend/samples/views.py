from django.apps import apps
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lims.constants import events_dict
from .models import SampleType, Sample, SampleTraceability
from .serializers import SampleTypeSerializer, SampleSerializer, SampleTraceabilitySerializer   
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
   

STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar la muestra.'


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

    def destroy(self, request, pk=None):
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

class SampleViewSet(viewsets.ModelViewSet):
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
        """
        custom sample code to have category prefix-year-xxxx
        example: PT2026-1, when sample is created the assays are injected
        into the sample assays table and then the code is assigned.
        """
        serializer = self.get_serializer(data=request.data)
        assays_data = request.data.get('assays', [])

        if len(assays_data) <= 0:
            return Response(
                {"error": 'La muestra debe tener al menos un ensayo'},
                status=status.HTTP_400_BAD_REQUEST 
            )

        if serializer.is_valid():
            # create code and traceability log
            try:
                # failsafe to avoid errant data when creating a new sample
                with transaction.atomic():
                    sample = serializer.save()
                    
                    # assign sample assays
                    # get the sample assays model from assays module
                    SampleAssayModel = apps.get_model('assays', 'SampleAssay')

                    # insert the assays into the sample assays
                    for item in  assays_data:
                        SampleAssayModel.objects.create(
                            sample=sample,
                            assay_id=item['assay_id'],
                            specification=item['specification'].strip(),
                            units=item['units'].strip(),
                        )
                    
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

                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = events_dict['sample_creation'],
                    )

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                
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
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        sample = self.get_object()

        # check that request is PATCH or PUT to use the corresponding method
        partial = kwargs.pop('partial', False) or request.method == 'PATCH'
        
        serializer = self.get_serializer(sample, data=request.data, partial=partial)

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
    
    def destroy(self, request, pk=None):
        """
        In this case we "delete" the data by updating the active status
        and add a traceability log from the user to why this sample
        has to be deactivated.
        """        
        traceability_log = request.data.get('justification', '').strip().upper()
        
        # check message for traceability exists
        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        sample = self.get_object()
        
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
    api/sample-traceability
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
    