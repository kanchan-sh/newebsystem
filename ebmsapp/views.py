from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer,EventSerializer,TicketSerializer,BookingSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from . permissions import IsCustomer, IsEventOrganiser
from .models import Event,Ticket
from .task import snd_mail,ticket_booked_mail,notify_customers_on_event_update


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                user_data = {
                        'first_name': user.first_name,
                        'email': user.email,  # Assuming the user's email is stored in the 'email' field
                    }
                snd_mail.delay(user_data)

            refresh = RefreshToken.for_user(user)
            return Response({
                'data' : serializer.data,
                'message' : 'registraion mail sent sucessfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        # User is authenticated, generate token
        refresh = RefreshToken.for_user(user)
        return Response(
            {
            'message' : 'Login Sucessful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'status' : status.HTTP_200_OK, 
            }
        )
    else:
        # Authentication failed
        return Response(
            {
            "detail": "Invalid credentials"
            }, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEventOrganiser])
def create_event(request):
    if request.method == 'POST':
        data = request.data
        user = request.user
        user_id = user.id
        data['organizer'] = user_id
        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            event = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])  # Use PUT method for updating
@permission_classes([IsAuthenticated, IsEventOrganiser])
def update_event(request, pk):
    try:
        event = Event.objects.get(pk=pk, organizer=request.user)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        data = request.data
        user = request.user
        user_id = user.id
        data['organizer'] = user_id
        serializer = EventSerializer(event, data=data)

        if serializer.is_valid():
            serializer.save()
            notify_customers_on_event_update.delay(event.id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEventOrganiser])
def create_ticket(request):
    if request.method == 'POST':
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            event_ticket = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])  # Use PUT method for updating
@permission_classes([IsAuthenticated, IsEventOrganiser])
def update_ticket(request, pk):
    try:
        ticket = Ticket.objects.get(id=pk)
    except Ticket.DoesNotExist:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = TicketSerializer(ticket, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomer])
def create_bookings(request):
    if request.method == 'POST':
        data=request.data
        data['customer'] = request.user.id
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            # Calculate total cost based on quantity and ticket price
            ticket = serializer.validated_data['ticket']
            quantity = serializer.validated_data['quantity']
            total_cost = ticket.ticket_price * quantity
            data['total_cost'] = total_cost
            
            # Ensure availability
            if ticket.ticket_availability < quantity:
                return Response({'error': 'Not enough tickets available'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the booking
            booking = serializer.save()

            # Update ticket availability
            ticket.ticket_availability -= quantity
            ticket.save()
            user = request.user  # Get the user who made the booking
            if user:
                user_data = {
                        'first_name': user.first_name,
                        'email': user.email,  # Assuming the user's email is stored in the 'email' field
                    }
            ticket_booked_mail.delay(user_data)  # Call the send_mail task

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)