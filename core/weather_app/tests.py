import unittest
from django.test import Client
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User



class WeatherAppTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')    

    def test_login_view_valid_credentials(self):
        response = self.client.post('/login', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
    def test_login_view_invalid_username(self):
        response = self.client.post('/login', {'username': 'invaliduser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        redirected_response = self.client.get(response.url)
        self.assertContains(redirected_response, 'Invalid username.')    
        
    def test_login_view_invalid_password(self):
        response = self.client.post('/login', {'username': 'testuser', 'password': 'invalidpassword'})
        self.assertEqual(response.status_code, 302)
        redirected_response = self.client.get(response.url)
        self.assertContains(redirected_response, 'Invalid password.')
        
    def test_register_view_valid_data(self):
        response = self.client.post('/register', {'first_name': 'John', 'last_name': 'Doe', 'username': 'newuser', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/register')
        
    def test_register_view_existing_username(self):
        User.objects.create_user(username='existinguser', password='testpassword')
        response = self.client.post('/register', {'first_name': 'John', 'last_name': 'Doe', 'username': 'existinguser', 'password': 'newpassword'})
        self.assertEqual(response.status_code, 302)
        redirected_response = self.client.get(response.url)
        self.assertContains(redirected_response, 'Username already taken.')
        
    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login')
        
    def test_index_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/', {'city': 'Leh', 'n_days': '1'})
        self.assertEqual(response.status_code, 302)



    def test_index_view_unauthenticated(self):
        response = self.client.post('/', {'city': 'TestCity', 'n_days': '7'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login?next=/')
        
    def test_redirect_invalid_data(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/', {'city': 'dsfads', 'latitude': '123442', 'longitude': '2413', 'n_days': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
    def test_redirect_negative_days(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/', {'city': 'dsfads', 'latitude': '123442', 'longitude': '2413', 'n_days': '-1'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/') 
        
    def test_redirect_empty_data(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/', {'city': '', 'latitude': '', 'longitude': '', 'n_days': '1'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')               
    
    def test_gateway_timeout(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post('/', {'city': 'Mumbai', 'latitude': '27', 'longitude': '77', 'n_days': '1000'})
        self.assertEqual(response.status_code, 504)
