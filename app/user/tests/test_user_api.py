"""
Test for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successfull."""
        # content
        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'Test name',
            'telegram_id': '123456789'
        }
        # make a post request
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code,
                         status.HTTP_201_CREATED)  # type: ignore
        # get created user
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)  # type: ignore

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exist"""
        payload = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'Test name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short_error(self):
        """Test an error is returned if password less then 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'Test name',
        }
        # make a post request
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates tokens for valid creadantials"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'testpassword12345',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns an error if credentials invalid."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'goodpass',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test the public features of the user API"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpassword12345',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retieving profile for logged in user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_profile(self):
        """Test updating user profile."""
        payload = {
            'name': 'Updated username',
            'password': 'newpassword1234',
            'telegram_id': '999999999'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertTrue(self.user.telegram_id, payload['telegram_id'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
