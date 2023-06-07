from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework import status
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Account, Transaction
from .views import BankStatementListView, UnreadNotificationListView
from .models import Notification


# Unit testing
class TestAccountCreation(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            self.username, "test@example.com", self.password
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_individual_account(self):
        response = self.client.post(
            reverse("account_create"), {"account_type": Account.INDIVIDUAL}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_type"], Account.INDIVIDUAL)

    def test_create_company_account(self):
        response = self.client.post(
            reverse("account_create"), {"account_type": Account.COMPANY}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_type"], Account.COMPANY)

    def test_create_default_account(self):
        response = self.client.post(reverse("account_create"), {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["account_type"], Account.INDIVIDUAL)

    def test_create_invalid_account(self):
        response = self.client.post(
            reverse("account_create"), {"account_type": "INVALID_TYPE"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Unit testing
class TestAccountRetrieval(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_with_no_accounts = User.objects.create_user(
            "user_with_no_accounts",
            "user_with_no_accounts@example.com",
            "testpassword123",
        )
        self.user_with_one_account = User.objects.create_user(
            "user_with_one_account",
            "user_with_one_account@example.com",
            "testpassword123",
        )
        self.user_with_two_accounts = User.objects.create_user(
            "user_with_two_accounts",
            "user_with_two_accounts@example.com",
            "testpassword123",
        )

        Account.objects.create(
            user=self.user_with_one_account, balance=0, account_type=Account.INDIVIDUAL
        )
        Account.objects.create(
            user=self.user_with_two_accounts, balance=0, account_type=Account.INDIVIDUAL
        )
        Account.objects.create(
            user=self.user_with_two_accounts, balance=0, account_type=Account.COMPANY
        )

    def test_user_with_no_accounts(self):
        self.client.force_authenticate(user=self.user_with_no_accounts)
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_with_one_account(self):
        self.client.force_authenticate(user=self.user_with_one_account)
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_with_two_accounts(self):
        self.client.force_authenticate(user=self.user_with_two_accounts)
        response = self.client.get(reverse("account_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


# Unit testing and Integration testing
class TestTransactionConstraintsAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.sender = User.objects.create_user(
            "sender", "sender@example.com", "testpassword123"
        )
        self.recipient = User.objects.create_user(
            "recipient", "recipient@example.com", "testpassword123"
        )

        self.sender_account = Account.objects.create(user=self.sender, balance=100)
        self.recipient_account = Account.objects.create(user=self.recipient, balance=0)

    # Unit testing
    def test_withdraw_transaction_with_recipient(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.WITHDRAW,
            "amount": 50,
            "recipient": self.recipient_account.id,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["recipient"][0],
            "Recipient must be empty for 'withdraw' transactions.",
        )

    # Unit testing
    def test_pay_bill_transaction_with_incorrect_recipient_type(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.PAY_BILL,
            "amount": 50,
            "recipient": self.recipient_account.id,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["recipient"][0],
            "Recipient must be a company account for 'pay_bill' transactions.",
        )

    # Unit testing
    def test_transfer_transaction_without_recipient(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 50,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["recipient"][0],
            "Recipient must be specified for 'transfer' transactions.",
        )

    # Unit testing
    def test_transaction_with_insufficient_balance(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 150,
            "recipient": self.recipient_account.id,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["amount"][0],
            "Sender must have sufficient balance to perform the transaction.",
        )

    # Unit testing
    def test_transaction_with_unauthorized_sender(self):
        unauthorized_user = User.objects.create_user(
            "unauthorized", "unauthorized@example.com", "testpassword123"
        )
        unauthorized_account = Account.objects.create(
            user=unauthorized_user, balance=100
        )

        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 50,
            "recipient": self.recipient_account.id,
            "sender": unauthorized_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(
            response.data["detail"],
            "Sender account does not belong to the authenticated user.",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Unit testing
    def test_self_transactions(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 50,
            "recipient": self.sender_account.id,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(
            response.data["recipient"][0],
            "Self transactions are not allowed",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Integration testing
    def test_successful_transfer_transaction(self):
        self.client.force_authenticate(user=self.sender)
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 70,
            "recipient": self.recipient_account.id,
            "sender": self.sender_account.id,
        }
        response = self.client.post(reverse("transaction_create"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Refresh account instances
        self.sender_account.refresh_from_db()
        self.recipient_account.refresh_from_db()

        # Assert sender and recipient account balances
        self.assertEqual(self.sender_account.balance, 30)
        self.assertEqual(self.recipient_account.balance, 70)


# Admin transaction constraints
# Unit testing and Integration testing
class TestTransactionConstraintsModel(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            "sender", "sender@example.com", "testpassword123"
        )
        self.recipient = User.objects.create_user(
            "recipient", "recipient@example.com", "testpassword123"
        )

        self.sender_account = Account.objects.create(user=self.sender, balance=100)
        self.recipient_account = Account.objects.create(user=self.recipient, balance=0)

    def create_transaction(self, data):
        return Transaction.objects.create(**data)

    # Unit testing
    def test_withdraw_transaction_with_recipient(self):
        data = {
            "transaction_type": Transaction.WITHDRAW,
            "amount": 50,
            "recipient": self.recipient_account,
            "sender": self.sender_account,
        }

        with self.assertRaisesMessage(
            ValidationError,
            "Recipient must be empty for 'withdraw' transactions.",
        ):
            self.create_transaction(data)

    # Unit testing
    def test_pay_bill_transaction_with_incorrect_recipient_type(self):
        data = {
            "transaction_type": Transaction.PAY_BILL,
            "amount": 50,
            "recipient": self.recipient_account,
            "sender": self.sender_account,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "Recipient must be a company account for 'pay_bill' transactions.",
        ):
            self.create_transaction(data)

    # Unit testing
    def test_transfer_transaction_without_recipient(self):
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 50,
            "sender": self.sender_account,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "Recipient must be specified for 'transfer' transactions.",
        ):
            self.create_transaction(data)

    # Unit testing
    def test_transaction_with_insufficient_balance(self):
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 150,
            "recipient": self.recipient_account,
            "sender": self.sender_account,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "Sender must have sufficient balance to perform the transaction.",
        ):
            self.create_transaction(data)

    # Unit testing
    def test_self_transaction(self):
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 50,
            "recipient": self.sender_account,
            "sender": self.sender_account,
        }
        with self.assertRaisesMessage(
            ValidationError,
            "Self transactions are not allowed",
        ):
            self.create_transaction(data)

    # Integration testing
    def test_successful_transfer_transaction(self):
        data = {
            "transaction_type": Transaction.TRANSFER,
            "amount": 70,
            "recipient": self.recipient_account,
            "sender": self.sender_account,
        }
        transaction = self.create_transaction(data)
        self.assertEqual(transaction.transaction_type, Transaction.TRANSFER)
        self.assertEqual(transaction.amount, 70)
        self.assertEqual(transaction.recipient.id, self.recipient_account.id)
        self.assertEqual(transaction.sender.id, self.sender_account.id)


# Integration testing
class TransactionsIntegrationTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user1 = User.objects.create_user(
            username="user1", password="testpassword1"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpassword2"
        )

        self.account1 = Account.objects.create(user=self.user1, balance=1000)
        self.account2 = Account.objects.create(user=self.user2, balance=2000)

        # Create multiple transactions
        self.transactions = [
            Transaction.objects.create(
                sender=self.account1,
                recipient=self.account2,
                transaction_type=Transaction.TRANSFER,
                amount=200,
            ),
            Transaction.objects.create(
                sender=self.account2,
                recipient=self.account1,
                transaction_type=Transaction.TRANSFER,
                amount=300,
            ),
            Transaction.objects.create(
                sender=self.account1,
                recipient=None,
                transaction_type=Transaction.WITHDRAW,
                amount=150,
            ),
        ]

    def test_get_notificatios(self):
        view = UnreadNotificationListView.as_view()
        url = "/accounts/notifications/unread/"
        request1 = self.factory.get(url)
        force_authenticate(request1, user=self.user1)
        response1 = view(request1)
        request2 = self.factory.get(url)
        force_authenticate(request2, user=self.user2)
        response2 = view(request2)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response1.data[0]["message"], "You sent 200 EGP in a transaction."
        )
        self.assertEqual(
            response1.data[1]["message"], "You received 300 EGP in a transaction."
        )
        self.assertEqual(
            response1.data[2]["message"], "You sent 150 EGP in a transaction."
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response2.data[0]["message"], "You received 200 EGP in a transaction."
        )
        self.assertEqual(
            response2.data[1]["message"], "You sent 300 EGP in a transaction."
        )

    def test_get_bank_statements(self):
        view = BankStatementListView.as_view()
        url = f"/accounts/{self.account1.id}/statements/"
        request = self.factory.get(url)
        force_authenticate(request, user=self.user1)

        response = view(request, account_id=self.account1.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Assert transaction details
        self.assertEqual(response.data[0]["transaction_type"], Transaction.WITHDRAW)
        self.assertEqual(response.data[0]["amount"], "150.00")
        self.assertEqual(response.data[0]["sender"], self.account1.id)
        self.assertIsNone(response.data[0]["recipient"])

        self.assertEqual(response.data[1]["transaction_type"], Transaction.TRANSFER)
        self.assertEqual(response.data[1]["amount"], "300.00")
        self.assertEqual(response.data[1]["sender"], self.account2.id)
        self.assertEqual(response.data[1]["recipient"], self.account1.id)

        self.assertEqual(response.data[2]["transaction_type"], Transaction.TRANSFER)
        self.assertEqual(response.data[2]["amount"], "200.00")
        self.assertEqual(response.data[2]["sender"], self.account1.id)
        self.assertEqual(response.data[2]["recipient"], self.account2.id)


# Unit testing
class NotificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user, message="Test notification"
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "Test notification")
        self.assertFalse(notification.is_read)

    def test_notification_mark_as_read(self):
        notification = Notification.objects.create(
            user=self.user, message="Test notification"
        )
        notification.mark_as_read()
        self.assertTrue(notification.is_read)

    def test_notification_str_representation(self):
        notification = Notification.objects.create(
            user=self.user, message="Test notification"
        )
        self.assertEqual(str(notification), "Test notification")


# Unit testing
class TransactionTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", password="testpassword1"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="testpassword2"
        )

        self.account1 = Account.objects.create(
            user=self.user1, account_type=Account.INDIVIDUAL, balance=1000
        )
        self.account2 = Account.objects.create(
            user=self.user2, account_type=Account.COMPANY, balance=2000
        )

    def test_pay_bill(self):
        transaction = Transaction.objects.create(
            sender=self.account1,
            recipient=self.account2,
            transaction_type=Transaction.PAY_BILL,
            amount=500,
        )

        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(transaction.sender, self.account1)
        self.assertEqual(transaction.recipient, self.account2)
        self.assertEqual(transaction.transaction_type, Transaction.PAY_BILL)
        self.assertEqual(transaction.amount, 500)

        # Verify account balances after the transaction
        self.account1.refresh_from_db()
        self.account2.refresh_from_db()
        self.assertEqual(
            self.account1.balance, 500
        )  # Account1 balance decreased by 500
        self.assertEqual(
            self.account2.balance, 2500
        )  # Account2 balance increased by 500

    def test_withdraw_transaction(self):
        transaction = Transaction.objects.create(
            sender=self.account1,
            recipient=None,
            transaction_type=Transaction.WITHDRAW,
            amount=500,
        )

        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(transaction.sender, self.account1)
        self.assertIsNone(transaction.recipient)
        self.assertEqual(transaction.transaction_type, Transaction.WITHDRAW)
        self.assertEqual(transaction.amount, 500)

        # Verify account balance after the transaction
        self.account1.refresh_from_db()
        self.assertEqual(
            self.account1.balance, 500
        )  # Account1 balance decreased by 500
