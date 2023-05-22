from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Account, Transaction, Notification


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "account_type"]


class AccountRetrievalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "user", "balance", "account_type"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "transaction_type", "amount", "recipient", "sender"]

    def validate_sender(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise PermissionDenied(
                "Sender account does not belong to the authenticated user."
            )
        return value

    def validate(self, data):
        transaction_type = data.get("transaction_type")
        amount = data.get("amount")
        recipient = data.get("recipient")
        sender = data.get("sender")

        if transaction_type == Transaction.WITHDRAW and recipient is not None:
            raise serializers.ValidationError(
                {"recipient": "Recipient must be empty for 'withdraw' transactions."}
            )

        if (
            transaction_type == Transaction.PAY_BILL
            and recipient.account_type != Account.COMPANY
        ):
            raise serializers.ValidationError(
                {
                    "recipient": "Recipient must be a company account for 'pay_bill' transactions."
                }
            )

        if transaction_type == Transaction.TRANSFER and recipient is None:
            raise serializers.ValidationError(
                {
                    "recipient": "Recipient must be specified for 'transfer' transactions."
                }
            )

        if sender.balance - amount < 0:
            raise serializers.ValidationError(
                {
                    "amount": "Sender must have sufficient balance to perform the transaction."
                }
            )

        if sender == recipient:
            raise serializers.ValidationError(
                {"recipient": "Self transactions are not allowed"}
            )
        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
