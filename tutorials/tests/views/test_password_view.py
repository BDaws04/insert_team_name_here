"""Tests for the password view."""
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import PasswordForm
from tutorials.models import User, Student, Tutor
from tutorials.tests.helper_classes import reverse_with_next

class PasswordViewTest(TestCase):
    """Test suite for the password view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('password')
        self.form_input = {
            'password': 'Password123',
            'new_password': 'NewPassword123',
            'password_confirmation': 'NewPassword123',
        }

    def test_password_url(self):
        self.assertEqual(self.url, '/password/')

    def test_get_password(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))

    def test_get_password_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_succesful_password_change_for_admin(self):
        self.client.login(username=self.user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_succesful_password_change_for_student(self):
        user = User.objects.get(username='@janedoe')
        self.client.login(username=user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_dashboard.html')
        user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', user.password)
        self.assertTrue(is_password_correct)

    def test_succesful_password_change_for_tutor(self):
        user = User.objects.get(username='@petrapickles')
        self.client.login(username=user.username, password='Password123')
        response = self.client.post(self.url, self.form_input, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'tutor_dashboard.html')
        user.refresh_from_db()
        is_password_correct = check_password('NewPassword123', user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_correct_old_password(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_password_change_unsuccesful_without_password_confirmation(self):
        self.client.login(username=self.user.username, password='Password123')
        self.form_input['password_confirmation'] = 'WrongPassword123'
        response = self.client.post(self.url, self.form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordForm))
        self.user.refresh_from_db()
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)

    def test_post_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url, self.form_input)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        is_password_correct = check_password('Password123', self.user.password)
        self.assertTrue(is_password_correct)
