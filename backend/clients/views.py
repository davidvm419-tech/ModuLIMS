from django.db import transaction
from django.shortcuts import get_object_or_404
from lims.constants import events_dict
from .models import Client, ClientTraceability
from .serializers import ClientSerializer, ClientTraceabilitySerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar el cliente.'

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

    def create(self, request, *args, **kwargs):
        """
        Add the client creation into the traceability table
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    client = serializer.save()

                    # traceability log
                    ClientTraceability.objects.create(
                        client = client,
                        user_responsible = request.user,
                        event = events_dict['client_creation']
                    )

                    return Response(self.get_serializer(client).data, status=status.HTTP_201_CREATED)

            except Exception as err:
                return Response(
                    {'error': f"Error al crear cliente: {str(err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Update the client data in case that is needed.
        """
        traceability_log = request.data.get('justification', '').strip().upper()

        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = self.get_object()

        # check that request is PATCH or PUT to use only one method
        partial = kwargs.pop('partial', False) or request.method == 'PATCH'
        
        serializer = self.get_serializer(client, data=request.data, partial=partial)
        
        if serializer.is_valid():

            try:
                with transaction.atomic():
                    serializer.save()

                    # traceability log
                    ClientTraceability.objects.create(
                        client = client,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE CLIENTE: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as err:
                return Response(
                    {'error': f'error actualizando cliente: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        In this case we "delete" the data by updating the active status
        so the default behavior is overwrite
        """
        traceability_log = request.data.get('justification', '').strip().upper()
        
        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        client = self.get_object()
        
        try:
            with transaction.atomic():
                client.is_active = False
                client.save()

                # traceability log
                ClientTraceability.objects.create(
                    client = client,
                    user_responsible = request.user,
                    event = f"INACTIVACIÓN DE CLIENTE: {traceability_log}"
                )

                return Response(
                    {'message': f"Cliente {client.name} desactivado con éxito."},
                    status=status.HTTP_200_OK
                )
            
        except Exception as err:
            return Response(
                {'error': f'error desactivando al usuario: {str(err)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class ClientTraceabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire traceability endpoint for the frontend
    api/client-traceability
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = ClientTraceability.objects.all()
    serializer_class = ClientTraceabilitySerializer 

    # decorator to tell DRF that use the global pagination and to add a custom readable url
    @action(detail=False, methods=['get'], url_path=r'client/(?P<client_id>\d+)')
    def client_traceability(self, request, client_id=None):
        """
        The read only view set gives the predefined methods,
        here we get data by user id thanks to that inheritance.
        """

        # avoid requests with none existing users
        get_object_or_404(Client, pk=client_id)

        queryset = ClientTraceability.objects.filter(client=client_id)
        
        # tell DRF that paginate the queryset based n the global settings
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)    
            return self.get_paginated_response(serializer.data)
        
        # safeguard in case pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  
    