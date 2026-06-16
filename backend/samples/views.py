from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from lims.constants import events_dict
from samples.models import Client, SampleType, Sample, SampleTraceability
from samples.serializers import ClientSerializer, SampleTypeSerializer, SampleSerializer, SampleTraceabilitySerializer   
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets   


STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar la muestra.'

# view sets hide the underlying implementation of  CRUD details
class ClientViewSet(viewsets.ViewSet):
    """
    This view will get the entire Client endpoint for the frontend
    api/clients
    api/clients/int:<id>
    for GET, POST PUT/PATCH and DELETE operations
    """
    permission_classes = [IsAuthenticated]

    # it gives the GET method
    def list(self, request):
        # get only active clients
        queryset = Client.objects.filter(is_active=True).order_by('name')
        serializer = ClientSerializer(queryset, many=True)
        # best practice to send the status code like this
        return Response(serializer.data, status=status.HTTP_200_OK)   

    # it gives the POST method
    def create(self, request):
        serializer = ClientSerializer(data=request.data)

        # Django runs valid data behind the scenes
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # it gives the GET method for some specific data
    def retrieve(self, request, pk=None):
        queryset = Client.objects.filter(is_active=True)
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data,  status=status.HTTP_200_OK)  

    # it gives the PUT/PATCH methods to update a complete dataset
    def update(self, request, pk=None):
        queryset = Client.objects.filter(is_active=True)
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # it gives the PUT/PATCH methods to update a specific part of  a dataset
    def partial_update(self, request, pk=None):
        queryset = Client.objects.filter(is_active=True)
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # it gives the DELETE method 
    def destroy(self, request, pk=None):
        """
        In this case we "delete" the data by updating the active status
        """
        queryset  = Client.objects.filter(is_active=True)
        client = get_object_or_404(queryset, pk=pk)
        client.is_active = False
        client.save()

        return Response(
            {"message": f"Cliente {client.name} desactivado con éxito."},
            status=status.HTTP_200_OK
        )
    

class SampleTypeViewSet(viewsets.ViewSet):
    """
    This view will get the entire Sample endpoint for the frontend
    api/sample-category
    api/sample-category/int:<id>
    for GET, POST PUT/PATCH and DELETE operations
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = SampleType.objects.filter(is_active=True).order_by('name')
        serializer = SampleTypeSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = SampleTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
    def retrieve(self, request, pk=None):
        queryset = SampleType.objects.filter(is_active=True)
        category = get_object_or_404(queryset, pk=pk)
        serializer = SampleTypeSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        queryset = SampleType.objects.filter(is_active=True)
        category = get_object_or_404(queryset, pk=pk)
        serializer = SampleTypeSerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        queryset = SampleType.objects.filter(is_active=True)
        category = get_object_or_404(queryset, pk=pk)
        serializer = SampleTypeSerializer(category, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        In this case we "delete" the data by updating the active status
        """
        queryset = SampleType.objects.filter(is_active=True)
        category = get_object_or_404(queryset, pk=pk)
        category.is_active = False
        category.save()
        return Response(
            {"message": f"categoria {category.name} desactivada con éxito."},
            status=status.HTTP_200_OK
        )

class SampleViewSet(viewsets.ViewSet):
    """
    This view will get the entire Sample endpoint for the frontend
    api/samples
    api/samples/int:<id>
    for GET, POST PUT/PATCH and DELETE operations
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Sample.objects.filter(is_active=True).order_by('-received_date')
        serializer = SampleSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        """"
        custom sample code to have category prefix-year-xxxx
        example: PT2026-1
        """
        serializer = SampleSerializer(data=request.data)

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
                    
                    # assign sample assays
                    '''
                    add when assay module is implemented
                    ''' 
                    sample.save()

                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = events_dict['creation'],
                    )

                    return Response(SampleSerializer(sample).data, status=status.HTTP_201_CREATED)
                
            except Exception as err:
                return Response(
                    {'error':f'Error en el ingreso de la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        queryset = Sample.objects.filter(is_active=True)
        sample = get_object_or_404(queryset, pk=pk)
        serializer = SampleSerializer(sample)
        return Response(serializer.data, status=status.HTTP_200_OK)   

    def update(self, request, pk=None):
        """
        Any update must receive a reason for traceability log 
        frontend must send this traceability event along with the
        data to update.
        """
        queryset = Sample.objects.filter(is_active=True)
        sample = get_object_or_404(queryset, pk=pk)
        
        traceability_log = request.data.get('justification')
        
        # check message for traceability exists
        if not traceability_log or not traceability_log.strip():
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        serializer = SampleSerializer(sample, data=request.data)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    serializer.save()
            
                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = f"Modificación de muestra: {traceability_log.strip().upper()}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as err:
                return Response(
                    {'error': f'error actualizando la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        """
        Any update must receive a reason for traceability log 
        frontend must send this traceability event along with the
        data to update.
        """
        queryset = Sample.objects.filter(is_active=True)
        sample = get_object_or_404(queryset, pk=pk)
        
        traceability_log = request.data.get('justification')
        
        # check message for traceability exists
        if not traceability_log or not traceability_log.strip():
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        serializer = SampleSerializer(sample, data=request.data, partial=True)

        if serializer.is_valid():
            # update data and create traceability log
            try:
                with transaction.atomic():
                    serializer.save()
            
                    # traceability log
                    SampleTraceability.objects.create(
                        sample = sample,
                        user_responsible = request.user,
                        event = f"Modificación de muestra: {traceability_log.strip().upper()}",
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
        queryset = Sample.objects.filter(is_active=True)
        sample = get_object_or_404(queryset, pk=pk)
        
        traceability_log = request.data.get('justification')
        
        # check message for traceability exists
        if not traceability_log or not traceability_log.strip():
            return Response(
                {"error": STANDARD_ERROR_MESSAGE},
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
                    event = f"Inactivación de muestra: {traceability_log.strip().upper()}",
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
    queryset = SampleTraceability.objects.all().order_by('-event_date')
    serializer_class = SampleTraceabilitySerializer 

    def get_queryset(self):
        """
        The read only view set gives the  predefined methods,
        here we get data by sample id thanks to that inheritance.
        """
        queryset = super().get_queryset()
        sample_id = self.request.query_params.get('sample_id')

        if sample_id is not None:
            queryset = queryset.filter(sample=sample_id)

        return queryset       
    
