from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Account(models.Model):
    INDIVIDUAL = "individual"
    COMPANY = "company"
    USER_TYPE_CHOICES = [
        (INDIVIDUAL, "Individual"),
        (COMPANY, "Company"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.CharField(
        max_length=50, choices=USER_TYPE_CHOICES, default=INDIVIDUAL
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    def mark_as_read(self):
        self.is_read = True
        self.save()


class Transaction(models.Model):
    class Meta:
        ordering = ["-timestamp"]

    WITHDRAW = "withdraw"
    PAY_BILL = "pay_bill"
    TRANSFER = "transfer"
    TRANSACTION_TYPE_CHOICES = [
        (WITHDRAW, "Withdraw"),
        (PAY_BILL, "Pay Bill"),
        (TRANSFER, "Transfer Money"),
    ]

    sender = models.ForeignKey(
        Account, related_name="sent_transactions", on_delete=models.CASCADE
    )
    # Null receipient means the recipient is outside our database (in case of the withdraw transaction)
    recipient = models.ForeignKey(
        Account,
        related_name="received_transactions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE_CHOICES, default=WITHDRAW
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    sender_notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sender_transactions",
    )
    recipient_notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipient_transactions",
    )

    def save(self, *args, **kwargs):
        if self.transaction_type == self.WITHDRAW and self.recipient is not None:
            raise ValidationError(
                "Recipient must be empty for 'withdraw' transactions."
            )

        if self.transaction_type == self.PAY_BILL and (
            self.recipient is None or self.recipient.account_type != Account.COMPANY
        ):
            raise ValidationError(
                "Recipient must be a company account for 'pay_bill' transactions."
            )

        if self.transaction_type == self.TRANSFER and (
            self.recipient is None or self.recipient == ""
        ):
            raise ValidationError(
                "Recipient must be specified for 'transfer' transactions."
            )

        if self.sender.balance - self.amount < 0:
            raise ValidationError(
                "Sender must have sufficient balance to perform the transaction."
            )

        if self.recipient is not None and self.sender == self.recipient:
            raise ValidationError("Self transactions are not allowed")

        created = not self.pk

        if created:
            sender_message = f"You sent {self.amount} EGP in a transaction."
            sender_notification = Notification.objects.create(
                user=self.sender.user, message=sender_message
            )

            self.sender_notification = sender_notification
            if self.recipient:
                recipient_message = f"You received {self.amount} EGP in a transaction."
                recipient_notification = Notification.objects.create(
                    user=self.recipient.user, message=recipient_message
                )

                self.recipient_notification = recipient_notification

            # Update the balances
            self.sender.balance -= self.amount
            self.sender.save()
            if self.recipient:
                self.recipient.balance += self.amount
                self.recipient.save()

        super().save(*args, **kwargs)
