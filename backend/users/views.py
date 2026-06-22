from django.db import transaction
from django.shortcuts import get_object_or_404
from lims.constants import events_dict
from .models import User, UserTraceability
from .serializers import UserAdminSerializer, UserProfileSerializer, UserTraceabilitySerializer    
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

STANDARD_ERROR_MESSAGE = 'Se requiere de una justificación para modificar los datos del usuario.'

class UserAdminViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire user endpoint for the frontend
    GET  /api/user-administration/ (list)
    POST /api/user-administration/ (create)
    GET  /api/user-administration/<int:id>/ (retrieve)
    PUT  /api/user-administration/<int:id>/ (update)
    PATCH /api/user-administration/<int:id>/ (partial_update)
    DELETE /api/user-administration/<int:id>/ (destroy)
    ModelViewSet gives a template for the basic CRUD 
    and custom behavior for the desired methods.
    """
    permission_classes = [IsAuthenticated]
    queryset =  User.objects.all()
    serializer_class = UserAdminSerializer

    def create(self, request, *args, **kwargs):
        """
        Add the user creation into the traceability table
        """

        password = request.data.get('password', '').strip()

        # verify password rules
        if len(password) < 8:
            return Response(
                {'error': 'La contraseña requiere al menos 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != request.data.get('password_confirmation', '').strip():
            return Response(
                {'error': 'Las contraseñas no coinciden'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():

            try:
                with transaction.atomic():
        
                    user = serializer.save()

                    # store hashed password
                    user.set_password(password)
                    user.save()

                    # traceability log
                    UserTraceability.objects.create(
                        user = user,
                        user_responsible = request.user,
                        event = events_dict['user_creation']
                    )

                    return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)

            except Exception as err:
                return Response(
                    {'error': f"Error al crear usuario: {str(err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        Update the user data in case that is needed.
        """
        traceability_log = request.data.get('justification', '').strip().upper()

        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)

        # check that request is  PATCH or  PUT  t use only noe method
        partial = kwargs.pop('partial', False) or request.method == 'PATCH'
        
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        
        if serializer.is_valid():

            try:
                with transaction.atomic():
                    serializer.save()

                    # traceability log
                    UserTraceability.objects.create(
                        user = user,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE USUARIO: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as err:
                return Response(
                    {'error': f'error actualizando usuario: {str(err)}'},
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
        
        try:
            with transaction.atomic():

                user = self.get_object()
                user.is_active = False
                user.save()

                # traceability log
                UserTraceability.objects.create(
                    user = user,
                    user_responsible = request.user,
                    event = f"INACTIVACIÓN DE USUARIO: {traceability_log}"
                )

                return Response(
                    {"message": f"Usuario {user.username} desactivada con éxito."}, 
                    status=status.HTTP_200_OK
                )
            
        except Exception as err:
            return Response(
                {'error': f'error desactivando al usuario: {str(err)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    This view will get the entire user personal endpoint for the frontend
    GET  /api/user/<int:id>/ (retrieve)
    PATCH /api/user/<int:id>/ (partial_update)
    modelViewSet gives a template for the basic CRUD 
    and custom behavior for the desired methods.
    """
    permission_classes = [IsAuthenticated]
    queryset =  User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer

    http_method_names = ['get', 'patch', 'options',  'head']
        
    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        user can update password and sign if needed
        """
        # validate user
        if request.user.id != int(pk):
            return Response(
                {'error': 'acceso restringido'},
                status=status.HTTP_403_FORBIDDEN
            )

        traceability_log = request.data.get('justification', '').strip().upper()

        if not traceability_log:
            return Response(
                {'error': STANDARD_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)
  
        old_password = request.data.get('old_password', '').strip()
        new_password = request.data.get('new_password', '').strip()

        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():

            try:
                with transaction.atomic():
                    
                    user = serializer.save()
                    
                    # check if user updates the password not only the sign
                    if old_password or new_password:
                        if not old_password or not new_password:
                            return Response(
                                {'error': 'espacio de antigua y nueva contraseña es requerido'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                            
                        # check old password
                        if not user.check_password(old_password):
                            return Response(
                                {'error': 'contraseña actual incorrecta'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        # verify password rules
                        if len(new_password) < 8:
                            return Response(
                                {'error': 'La contraseña requiere al menos 8 caracteres'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        if new_password != request.data.get('new_password_confirmation', '').strip():
                            return Response(
                                {'error': 'Las nuevas contraseñas no coinciden'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        # update data in database
                        user.set_password(new_password)
                        user.save()

                    # traceability log
                    UserTraceability.objects.create(
                        user = user,
                        user_responsible = request.user,
                        event = f"MODIFICACIÓN DE INFORMACIÓN: {traceability_log}",
                    )

                    return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as err:
                return Response(
                    {'error': f'error actualizando información: {str(err)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserTraceabilityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This view will get the entire traceability endpoint for the frontend
    api/user-traceability
    for GET operations, editing and deleting is forbidden.
    """
    permission_classes = [IsAuthenticated]
    queryset = UserTraceability.objects.all()
    serializer_class = UserTraceabilitySerializer 

    # decorator to tell DRF that use the global pagination and to add a custom readable url
    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>\d+)')
    def user_traceability(self, request, user_id=None):
        """
        The read only view set gives the predefined methods,
        here we get data by user id thanks to that inheritance.
        """

        # avoid requests with none existing users
        get_object_or_404(User, pk=user_id)

        queryset = UserTraceability.objects.filter(user=user_id)
        
        # tell DRF that paginate the queryset based n the global settings
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)    
            return self.get_paginated_response(serializer.data)
        
        # safeguard in case pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  