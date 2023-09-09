from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question


def index(request):
    """
    Displays a list of the latest ten published questions.

    Returns:
        Rendered HTML page displaying the latest questions.
    """
    latest_question_list = Question.objects.order_by("-pub_date")[:10]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    """
        Displays the details of a specific question.

        Args:
            request: The HTTP request object.
            question_id: The ID of the question to display.

        Returns:
            Rendered HTML page displaying the question details.
    """
    question = get_object_or_404(Question, pk=question_id)
    if not question.can_vote():
        messages.error(request, "Voting is not allowed")
        return redirect('polls:index')
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
        return Question.objects.filter(pub_date__lte=now).order_by("-pub_date")[:10]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get(self, request, *args, **kwargs):
        """
        Checks if the question is available to vote, and redirects if not.

        Args:
            request: The HTTP request object.

        Returns:
            Rendered HTML page displaying the question details or a 404 response.
        """
        question = self.get_object()
        now = timezone.now()
        if question.can_vote():
            return render(request, 'polls/detail.html', {'question': question})
        else:
            # Return a 404 response if the question cannot be voted on
            raise Http404("Question not found")


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    # Check if voting is allowed for this question
    if not question.can_vote():
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "Voting for this question is not allowed.",
            },
        )

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Re-show the voting form for the question.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

