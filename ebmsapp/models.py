from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

    
class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)

class EventOrganiser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)

class Event(models.Model):
    event_name = models.CharField(max_length=100)
    event_date = models.DateField()
    event_venue = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)

class Ticket(models.Model):
    ticket_type = models.CharField(max_length=70)
    ticket_price = models.DecimalField(max_digits=70, decimal_places=2)
    ticket_availability = models.IntegerField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket = models.ForeignKey (Ticket,on_delete=models.CASCADE)  # Allow multiple tickets per booking
    quantity = models.PositiveIntegerField(default=1)  # Quantity of tickets booked
    booking_date = models.DateTimeField(default=timezone.now)  # Booking date and time
    total_cost = models.DecimalField(default=0,max_digits=10, decimal_places=2)  # Total cost of the booking

    def save(self, *args, **kwargs):
        # Calculate total cost based on quantity and ticket price
        self.total_cost = self.ticket.ticket_price * self.quantity
        super().save(*args, **kwargs)