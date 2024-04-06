
from django.urls import path
from .views import register,login,create_event,update_event,create_ticket,update_ticket,create_bookings
urlpatterns = [
    
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('events/', create_event, name='events'),
    path('events/<int:pk>/', update_event, name='event-update'),
    path('tickets/', create_ticket, name='ticket-create'),
    path('tickets/<int:pk>/', update_ticket, name='ticket-update'),
    path('bookings/', create_bookings, name='booking-create'),

]