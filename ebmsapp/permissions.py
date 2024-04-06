from rest_framework import permissions

class IsCustomer(permissions.BasePermission):
    """
    Custom permission to only allow customers to access resources.
    """

    def has_permission(self, request, view):
        # Check if the user is a customer
        return hasattr(request.user, 'customer')

class IsEventOrganiser(permissions.BasePermission):
    """
    Custom permission to only allow event organizers to access resources.
    """

    def has_permission(self, request, view):
        # Check if the user is an event organiser
        return hasattr(request.user, 'eventorganiser')
