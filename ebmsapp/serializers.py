from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer, EventOrganiser,Event,Ticket,Booking

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    user_type = serializers.ChoiceField(choices=(('customer', 'Customer'), ('event_organiser', 'Event Organiser')), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type','first_name','last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        user_type = attrs.get('user_type')
        if user_type not in ['customer', 'event_organiser']:
            raise serializers.ValidationError("Invalid user_type")

        return attrs
    def create(self, validated_data):
        user_type = validated_data.pop('user_type', None)  
        user = User.objects.create_user(**validated_data)

        if user_type == 'customer':
            Customer.objects.create(user=user)
        elif user_type == 'event_organiser':
            EventOrganiser.objects.create(user=user)

        return user
    
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def create(self,validated_data):
        event = Event.objects.create(**validated_data)
        return event
    def update(self, instance, validated_data):
        """
        Update and return an existing `Event` instance, given the validated data.
        """
        instance.event_name = validated_data.get('event_name', instance.event_name)
        instance.event_date = validated_data.get('event_date', instance.event_date)
        instance.event_venue = validated_data.get('event_venue', instance.event_venue)
        instance.organizer = validated_data.get('organizer', instance.organizer)
        instance.save()
        return instance
    
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

    def validate(self, attrs):
        event_id = attrs.get('event')
        event = Event.objects.filter(id=event_id.id)
        if event is None:
            raise serializers.ValidationError("Event Does not exist")
        return attrs

    def create(self,validated_data):
        event = Ticket.objects.create(**validated_data)
        return event
    
    def update(self, instance, validated_data):
        """
        Update and return an existing `Event` instance, given the validated data.
        """
        instance.ticket_type = validated_data.get('ticket_type', instance.ticket_type)
        instance.ticket_price = validated_data.get('ticket_price', instance.ticket_price)
        instance.ticket_availability = validated_data.get('ticket_availability', instance.ticket_availability)
        instance.event = validated_data.get('event', instance.event)
        instance.save()
        return instance

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customer','event', 'ticket', 'quantity', 'booking_date', 'total_cost']

    def create(self,validated_data):
        event = Booking.objects.create(**validated_data)
        return event
    