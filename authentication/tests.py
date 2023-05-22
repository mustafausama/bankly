from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# Unit testing
class TestUserAuthentication(TestCase):
    # To setup a new user directly in the database
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword123"
        self.user = User.objects.create_user(
            self.username, "test@example.com", self.password
        )
        self.client = APIClient()

    # Test logging in using the correct credentials
    def test_successful_login(self):
        # a post request is created to an endpoint with the name 'token_obtain_pair' (Check urls.py)
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.username, "password": self.password},
        )
        # make sure the response status code is OK
        # make sure the response has "access" token in the body
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)

    # Test logging in using incorrect credentials
    def test_unsuccessful_login(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "wrong", "password": "wrongpassword"},
        )
        # make sure the response status code is Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Unit testing
class TestUserRegistration(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword123"
        self.email = "test@example.com"
        self.client = APIClient()

    def test_successful_registration(self):
        # Register with a username that does not exist and a valid password
        response = self.client.post(
            reverse("register"),
            {"username": self.username, "password": self.password, "email": self.email},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("username" in response.data)

    def test_registration_missing_field(self):
        # Register without a username
        response = self.client.post(reverse("register"), {"password": self.password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_username_taken(self):
        # Register with a taken username
        User.objects.create_user(self.username, self.email, self.password)
        response = self.client.post(
            reverse("register"),
            {"username": self.username, "password": self.password, "email": self.email},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Integration testing
class UserRegistrationLoginIntegrationTest(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword123"
        self.email = "test@example.com"
        self.client = APIClient()

    def test_user_registration_and_login(self):
        # Register with a username that does not exist and a valid password
        response = self.client.post(
            reverse("register"),
            {"username": self.username, "password": self.password, "email": self.email},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue("username" in response.data)

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.username, "password": self.password},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in response.data)
