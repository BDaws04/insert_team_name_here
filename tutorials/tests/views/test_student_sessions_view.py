from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Paginator
from tutorials.models import User, Student, StudentSession, Session, TutorSession, Tutor, ProgrammingLanguage

class StudentSessionsViewTestCase(TestCase):
    """Tests of the student sessions view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('student_sessions')
        self.admin_user = User.objects.get(username='@johndoe')
        self.student_user = User.objects.get(username='@janedoe')
        self.tutor_user = User.objects.get(username='@petrapickles')
        
        # Create test data
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)
        
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.session = Session.objects.create(
            programming_language=self.language,
            level='beginner',
            season='Fall',
            year=2024,
            frequency='Weekly',
            duration_hours=2
        )
        
        self.tutor_session = TutorSession.objects.create(
            tutor=self.tutor,
            session=self.session
        )
        
        self.student_session = StudentSession.objects.create(
            student=self.student,
            tutor_session=self.tutor_session
        )

    def test_student_sessions_url(self):
        self.assertEqual(self.url, '/student-sessions/')

    def test_get_student_sessions_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_student_sessions_redirects_when_not_admin(self):
        self.client.login(username=self.student_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_get_student_sessions_for_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_sessions.html')
        
        # Check context data
        self.assertIn('sessions', response.context)
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], self.student_session)

    def test_student_sessions_pagination(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_sessions.html')
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions.number, 1)
        self.assertEqual(sessions.paginator.num_pages, 1)

    def test_student_sessions_multiple_pages(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        
        # Create 11 more sessions (12 total)
        for i in range(11):
            student = Student.objects.create(
                user=User.objects.create(
                    username=f'@student{i}',
                    first_name=f'Student{i}',
                    last_name='Test',
                    email=f'student{i}@example.org'
                )
            )
            
            session = Session.objects.create(
                programming_language=self.language,
                level='beginner',
                season='Fall',
                year=2024,
                frequency='Weekly',
                duration_hours=2
            )
            
            tutor_session = TutorSession.objects.create(
                tutor=self.tutor,
                session=session
            )
            
            StudentSession.objects.create(
                student=student,
                tutor_session=tutor_session
            )
            
        # Test first page
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['sessions']), 10)  # First page should have 10 items
        self.assertTrue(response.context['sessions'].has_next())
        self.assertFalse(response.context['sessions'].has_previous())
        
        # Test second page
        response = self.client.get(f"{self.url}?page=2")
        self.assertEqual(len(response.context['sessions']), 2)  # Second page should have 2 items
        self.assertFalse(response.context['sessions'].has_next())
        self.assertTrue(response.context['sessions'].has_previous())
        
        # Test invalid page
        response = self.client.get(f"{self.url}?page=999")
        self.assertEqual(len(response.context['sessions']), 2)  # Should show last page
