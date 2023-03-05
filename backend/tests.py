import os

import yaml
from django.test import TestCase
from rest_framework.authtoken.models import Token
from .models import Shop, ProductInfo, Order, User, Contact, ConfirmEmailToken
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ApiTests(APITestCase):
    def login_user(self):
        user = User.objects.create(
            first_name='Test',
            last_name='Testov',
            email='test99@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            type='buyer',
            is_active=True
        )
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_register_account(self):
        count = User.objects.count()
        user = {
            'first_name': 'Test',
            'last_name': 'Testov',
            'email': 'test99@test.com',
            'password': 'dgdfhjfhdbhsfjdf777',
            'company': 'macdocknack',
            'position': 'manager',
            'type': 'buyer',
        }

        url = reverse('backend:user-register')
        response = self.client.post(url, user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)
        self.assertEqual(User.objects.count(), count + 1)

    def test_confirm_register(self):
        user = User.objects.create_user(
                first_name='Test',
                last_name='Testov',
                email='test99@test.com',
                password='dgdfhjfhdbhsfjdf777',
                company='macdocknack',
                position='manager'
            )
        token = ConfirmEmailToken.objects.create(user_id=user.id).key
        url = reverse('backend:user-register-confirm')
        data = {'email': user.email, 'token': token}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_create_contact(self):
        user = User.objects.create_user(
            first_name='Test',
            last_name='Testov',
            email='test99@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            is_active=True
        )
        url = reverse('backend:user-contact')
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        data = {'city': 'msk', 'street': 'pokrovka', 'phone': '+7123456789'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_partner_update(self):
        user = User.objects.create_user(
            first_name='Test',
            last_name='Testov',
            email='test9@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            type='shop',
            is_active=True
        )
        url = reverse('backend:partner-update')
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        # with open('backend/shop1.yaml') as f:
        updated_data = {'partner': user.id,
                        'url': 'https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml'}
        response = self.client.post(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_partner_state(self):
        self.test_partner_update()
        url = reverse('backend:partner-state')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Status', response.json())
        self.assertEqual(response.json['Status'], True)
        for item in response.json['data']:
            self.assertIn('url', item)
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('state', item)

    def test_update_partner_state(self):
        self.test_partner_update()
        url = reverse('backend:partner-state')
        response = self.client.post(url, data={'state': 'on'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.json())
        self.assertIn('Status', response.json())
        self.assertEqual(response.json()['Status'], True)

    def test_get_account_details(self):
        url = reverse('backend:user-details')
        user = User.objects.create_user(
            first_name='Test',
            last_name='Testov',
            email='test99@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            is_active=True
        )
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_account_details(self):
        url = reverse('backend:user-details')
        user = User.objects.create_user(
            first_name='Test',
            last_name='Testov',
            email='test99@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            is_active=True
        )
        updated_user = {'last_name': 'Testovsky'}
        token = Token.objects.create(user=user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.post(url, updated_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_reset_password(self):
        url = reverse('backend:password-reset')
        User.objects.create_user(
            first_name='Test',
            last_name='Testov',
            email='test99@test.com',
            password='dgdfhjfhdbhsfjdf777',
            company='macdocknack',
            position='manager',
            is_active=True
        )
        data = {'email': 'test99@test.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_info(self):
        url = reverse('backend:shops')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.data)

    def test_add_to_basket(self):
        self.login_user()
        self.test_partner_update()
        url = reverse('backend:basket')
        user = User.objects.get(email='test99@test.com')
        id_ = 1
        quantity = 2
        response = self.client.put(url, items={'product_info': id_, 'quantity': quantity})
        self.assertTrue(Order.objects.filter(user_id=user.id, state='basket').exists())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.data)
        self.assertIn('Status', response.data)
        self.assertEqual(response.data['Status'], True)

    def test_basket(self):
        self.test_add_to_basket()
        url = reverse('backend:basket')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Errors', response.data)
        self.assertIn('Status', response.data)
        self.assertEqual(response.data['Status'], True)