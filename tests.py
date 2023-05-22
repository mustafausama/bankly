from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from banking.models import Account, Transaction


class BigBangIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_big_bang(self):
        # User Registration
        registration_data = {
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com",
        }
        response = self.client.post(reverse("register"), registration_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("username" in response.data)
        self.assertEqual(response.data["username"], registration_data["username"])
        registration_data["id"] = response.data["id"]

        # User Login
        login_data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(reverse("token_obtain_pair"), login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        self.assertTrue("refresh" in response.data)
        refresh_token = response.data["refresh"]

        # User refresh login
        refresh_data = {"refresh": refresh_token}
        response = self.client.post(reverse("token_refresh"), refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
        access_token = response.data["access"]
        # Attach the access_token to all the following requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Create Account
        account_data = {"account_type": "individual"}
        response = self.client.post(reverse("account_create"), account_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("account_type" in response.data)
        self.assertEqual(response.data["account_type"], account_data["account_type"])

        # Hard-update balance (as an admin) using the ORM
        account = Account.objects.get(user__username="testuser")
        account.balance = 1000
        account.save()

        self.assertEqual(account.balance, 1000)

        # Create Transaction
        transaction_data = {
            "sender": Account.objects.get(user__username="testuser").id,
            "transaction_type": Transaction.WITHDRAW,
            "amount": 500,
        }
        response = self.client.post(reverse("transaction_create"), transaction_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check Account list
        response = self.client.get(reverse("account_list"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["balance"], "500.00")

        # Check Bank Statement
        response = self.client.get(
            reverse("bank_statement_list", kwargs={"account_id": account.id})
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["amount"], "500.00")
        self.assertEqual(response.data[0]["transaction_type"], Transaction.WITHDRAW)
        self.assertEqual(response.data[0]["sender"], registration_data["id"])
        self.assertIsNone(response.data[0]["recipient"])

        # Check Unread Notifications
        response = self.client.get(reverse("unread_notifications"))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["message"], "You sent 500.00 EGP in a transaction."
        )
        self.assertEqual(response.data[0]["is_read"], False)
