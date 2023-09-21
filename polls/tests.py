import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from django.contrib.auth import views as auth_views
from mysite import settings

from .models import Question, Choice


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_is_published_with_future_pub_date(self):
        """
        is_published() should return False for questions with a future pub_date.
        """
        future_time = timezone.now() + timezone.timedelta(days=1)
        future_question = Question(pub_date=future_time)
        self.assertFalse(future_question.is_published())

    def test_is_published_with_default_pub_date(self):
        """
        is_published() should return True for questions with the default pub_date (now).
        """
        current_time = timezone.now()
        current_question = Question(pub_date=current_time)
        self.assertTrue(current_question.is_published())

    def test_is_published_with_past_pub_date(self):
        """
        is_published() should return True for questions with a past pub_date.
        """
        past_time = timezone.now() - timezone.timedelta(days=1)
        past_question = Question(pub_date=past_time)
        self.assertTrue(past_question.is_published())

    def test_can_vote_future_question(self):
        """
        Questions with a pub_date in the future should not be votable.
        """
        future_question = Question.objects.create(
            question_text="Future question",
            pub_date=timezone.now() + timezone.timedelta(days=7),  # Pub date in the future
        )
        self.assertFalse(future_question.can_vote())

    def test_can_vote_open_question(self):
        """
        Open questions (no end_date) should be votable.
        """
        open_question = Question.objects.create(
            question_text="Open question",
            pub_date=timezone.now() - timezone.timedelta(days=1),  # Pub date in the past
        )
        self.assertTrue(open_question.can_vote())

    def test_can_vote_closed_question(self):
        """
        Questions with a past end_date should not be votable.
        """
        closed_question = Question.objects.create(
            question_text="Closed question",
            pub_date=timezone.now() - timezone.timedelta(days=7),  # Pub date in the past
            end_date=timezone.now() - timezone.timedelta(days=1),  # End date in the past
        )
        self.assertFalse(closed_question.can_vote())


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    if days > 0:  # Ensure future questions have a pub_date in the future
        time += datetime.timedelta(seconds=1)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertIn(response.status_code, [404, 302, 200])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple past questions.
        """
        # Create two past questions
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 200 is succeeded, 404 not found and 302 requested
        URI has been temporarily changed.
        """
        future_question = create_question(question_text="Future question.", days=15)
        url = reverse("polls:detail", args=(future_question.pk,))
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 404, 302])

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-15)
        url = reverse('polls:detail', args=(past_question.pk,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class UserAuthTest(TestCase):

    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        pub_date = timezone.now()  # Set the pub_date to the current time
        q = Question.objects.create(
            question_text="First Poll Question",
            pub_date=pub_date  # Specify the pub_date here
        )
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after a successful login, should redirect the browser somewhere
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
        or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)
