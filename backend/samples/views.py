from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from samples.models import Client, SampleType, Sample, SampleTraceability
from samples.serializers import ClientSerializer, SampleTypeSerializer, SampleSerializer, SampleTraceabilitySerializer   
from rest_framework.response import Response
from rest_framework import status, viewsets   

# Create your views here.


# view sets hide the underlying implementation of  CRUD details
class ClientViewSet(viewsets.ViewSet):
    """
    This view will get the entire Client endpoint for the frontend
    api/clients
    api/clients/int:<id>
    for GET, POST PUT/PATCH and DELETE operations
    """

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
        queryset = Client.objects.all()
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data,  status=status.HTTP_200_OK)  

    # it gives the PUT/PATCH methods to update a complete dataset
    def update(self, request, pk=None):
        queryset = Client.objects.all()
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # it gives the PUT/PATCH methods to update a specific part of  a dataset
    def partial_update(self, request, pk=None):
        queryset = Client.objects.all()
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
        queryset  = Client.objects.all()
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
        queryset = SampleType.objects.all()
        category = get_object_or_404(queryset, pk=pk)
        serializer = SampleTypeSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        queryset = SampleType.objects.all()
        category = get_object_or_404(queryset, pk=pk)
        serializer = SampleTypeSerializer(category, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        queryset = SampleType.objects.all()
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
        queryset = SampleType.objects.all()
        category = get_object_or_404(queryset, pk=pk)
        category.is_active = False
        category.save()
        return Response(
            {"message": f"categoria {category.name} desactivada con éxito,"},
            status=status.HTTP_200_OK
        )

class SampleViewSet(viewsets.ViewSet):
    """
    This view will get the entire Sample endpoint for the frontend
    api/samples
    api/samples/int:<id>
    for GET, POST PUT/PATCH and DELETE operations
    """

    def list(self, request):
        queryset = Sample.objects.filter(is_active=True).order_by('-received_date')
        serializer = SampleSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, pk=None):
        '''
        custom sample code to have category prefix-year-xxxx
        example: PT2026-1
        '''
        serializer = SampleSerializer(data=request.data)

        if serializer.is_valid():
            # create code, time  stamp and traceability
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
                    # add the code to create traceability log in the traceability table

                    # save data
            except Exception as err:
                return Response(
                    {'error':f'Error en el ingreso de la muestra: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors,  status=status.HTTP_400_BAD_REQUEST)

    