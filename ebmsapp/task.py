from .celery import app
from django.core.mail import send_mail
from newebsystem import settings
from .models import Booking,User,Event


@app.task(bind=True)
def snd_mail(self,user):
    if user:
        mail_subject = "User Registration"
        message = f"Hi {user['first_name']}\nWelcome to the Event Booking Management System!!!"
        to_mail = user['email']
        send_mail(
            subject = mail_subject,
            message = message,
            from_email = settings.EMAIL_HOST_USER,
            recipient_list = [to_mail,]
        )
    return 'completed'

@app.task(bind=True)
def ticket_booked_mail(self,user):
    if user:
        mail_subject = "Ticket Confirmation"
        message = f"Hi {user['first_name']}\nCongrutulations!!! your ticket is confirmed."
        to_mail = user['email']

        send_mail(
            subject = mail_subject,
            message = message,
            from_email = settings.EMAIL_HOST_USER,
            recipient_list = [to_mail,]
        )
    return 'completed'


@app.task(bind=True)
def notify_customers_on_event_update(self,event_id):
    event = Event.objects.get(id=event_id)

    bookings_for_event = Booking.objects.filter(event_id=event.id)

    customers = User.objects.filter(booking__in=bookings_for_event).distinct()
    
    for customer in customers:
        mail_subject = "Event Update Notification"
        message = f"Hi {customer.first_name},\nThe event you booked tickets for has been updated."
        to_mail = customer.email
        
        send_mail(
            subject=mail_subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_mail],
        )




