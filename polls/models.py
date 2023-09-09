import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin


class Question(models.Model):
    """
    Model representing a poll question.
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    end_date = models.DateTimeField("end date", null=True)

    def __str__(self):
        """
        String representation of the question.
        """
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        """
        Check if the question was published recently.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Check if the question is published.
        """
        now = timezone.now()
        return now >= self.pub_date

    def can_vote(self):
        """
        Returns True if the question can be voted on, False otherwise.
        """
        now = timezone.now()
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """
    Model representing a choice for a poll question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        String representation of the choice.
        """
        return self.choice_text