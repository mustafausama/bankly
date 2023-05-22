from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Account, Transaction, Notification
from .serializers import (
    AccountSerializer,
    AccountRetrievalSerializer,
    TransactionSerializer,
    NotificationSerializer,
)
from .permissions import IsAccountOwner


class AccountCreateView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountListView(ListAPIView):
    serializer_class = AccountRetrievalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class TransactionCreateView(CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]


class BankStatementListView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsAccountOwner]

    def get_queryset(self):
        account_id = self.kwargs["account_id"]
        queryset = Transaction.objects.filter(
            Q(sender__id=account_id) | Q(recipient__id=account_id)
        )
        return queryset


class UnreadNotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(user=user, is_read=False)
        return queryset
