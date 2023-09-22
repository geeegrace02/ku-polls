from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required  # Import the login_required decorator
from django.contrib.auth import logout  # Import the logout function
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Choice, Question, Vote


def index(request):
    """
    Displays a list of the latest five published questions.

    Returns:
        Rendered HTML page displaying the latest questions.
    """
    latest_question_list = Question.objects.filter(pub_date__lte=timezone.now())\
        .order_by('-pub_date')
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)


def detail(request, pk):
    """
    Displays the details of a specific question.

    Args:
        request: The HTTP request object.
        pk: The ID of the question to display.

    Returns:
        Rendered HTML page displaying the question details.
    """
    question = get_object_or_404(Question, pk=pk)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    """
    Displays the results of a specific question.

    Args:
        request: The HTTP request object.
        question_id: The ID of the question to display results for.

    Returns:
        Rendered HTML page displaying the question results.
    """
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last ten published questions (not including those set to be
        published in the future and questions with end_date in the past).
        """
        now = timezone.now()
        return Question.objects.filter(pub_date__lte=now).order_by("-pub_date")[:12]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now(), end_date__gte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        Checks if the question is available to vote, and redirects if not.

        Args:
            request: The HTTP request object.

        Returns:
            Rendered HTML page displaying the question details or a 404 response.
        """
        question = get_object_or_404(Question, pk=kwargs['pk'])
        if not question.can_vote():
            messages.error(request, "Voting is not allowed for this poll.")
            return redirect('polls:index')
        return render(request, 'polls/detail.html', {'question': question})


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


@login_required
def vote(request, question_id):
    """Vote for one of the answers to a question."""

    question = get_object_or_404(Question, pk=question_id)

    # Check if voting is allowed for this question
    if not question.can_vote():
        messages.error(request, "Voting for this question is not allowed.")
        return redirect('polls:index', question_id=question.id)

    # Render 'detail.html' template with 'question' for GET requests.
    if request.method == "GET":
        return render(request, 'polls/detail.html', {'question': question})

    try:
        # Get the selected choice from the POST data
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Re-show the voting form for the question if choice is not selected
        messages.error(request, "You didn't select a choice.")
        return render(request, 'polls/detail.html', {'question': question})

    recently_user = request.user

    try:
        # Check if the user has already voted for this choice
        vote = Vote.objects.get(user=recently_user, choice__question=question)
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        # Create a new vote for the selected choice and user
        vote = Vote.objects.create(choice=selected_choice, user=recently_user)

    vote.save()
    messages.success(request, f"Your vote for {selected_choice} has been saved.")

    # Redirect to the results page for the question
    return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
    else:
        # create a user form and display it on the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_logout(request):
    """Logout the user."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('polls:index')
