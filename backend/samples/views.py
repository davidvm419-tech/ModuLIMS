from .models import Client, SampleCategory, Sample, SampleTraceability
from django.shortcuts import get_object_or_404
from samples.serializers import ClientSerializer, SampleCategorySerializer, SampleSerializer, SampleTraceabilitySerializer   
from rest_framework.response import Response
from rest_framework import status, viewsets   

# Create your views here.


# view sets hide the underlying implementation of  CRUD details
class ClientViewSet(viewsets.ViewSet):
    """
    This view will get the entire Client endpoint for the frontend
    api/clients
    api/clients/<id>
    for GET, POST< PUT/PATCH and DELETE operations
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
    