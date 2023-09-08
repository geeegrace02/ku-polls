from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:10]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.POST = None

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(is_published=True)

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
            # Redisplay the question voting form.
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
        # Use HttpResponseRedirect to prevent duplicate form submissions when users click the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))