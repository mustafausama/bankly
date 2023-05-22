from rest_framework import permissions
from .models import Account

# The authenticated user must be the owner of the account in use
class IsAccountOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        account_id = view.kwargs.get("account_id")
        account_exists = Account.objects.filter(
            id=account_id, user=request.user
        ).exists()
        return account_exists
