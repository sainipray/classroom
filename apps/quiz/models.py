from django.contrib.auth import get_user_model
from django.db import models
from django_extensions.db.models import TimeStampedModel

User = get_user_model()


class Quiz(TimeStampedModel):
    title = models.CharField(max_length=255, verbose_name="Quiz Title")
    description = models.TextField(blank=True, verbose_name="Quiz Description")
    start_date = models.DateTimeField(verbose_name="Start Date")
    end_date = models.DateTimeField(verbose_name="End Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        ordering = ['start_date']
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    TEXT = 'text'
    IMAGE = 'image'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (IMAGE, 'Image'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        related_name="questions",
        on_delete=models.CASCADE,
        verbose_name="Quiz"
    )
    text = models.TextField(blank=True, null=True, verbose_name="Question Text")
    image = models.ImageField(upload_to='question_images/', blank=True, null=True, verbose_name="Question Image")
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        default=TEXT,
        verbose_name="Question Type"
    )
    mark = models.PositiveIntegerField(verbose_name="Marks")

    class Meta:
        ordering = ['id']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return self.text if self.text else f"Question {self.id}"


class Option(TimeStampedModel):
    question = models.ForeignKey(
        Question,
        related_name="options",
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    text = models.TextField(blank=True, null=True, verbose_name="Option Text")
    image = models.ImageField(upload_to='option_images/', blank=True, null=True, verbose_name="Option Image")
    is_correct = models.BooleanField(default=False, verbose_name="Is Correct")

    class Meta:
        ordering = ['id']
        verbose_name = "Option"
        verbose_name_plural = "Options"

    def __str__(self):
        return self.text if self.text else f"Option {self.id}"


class QuizAttempt(TimeStampedModel):
    quiz = models.ForeignKey(
        Quiz,
        related_name="attempts",
        on_delete=models.CASCADE,
        verbose_name="Quiz"
    )
    user = models.ForeignKey(
        User,
        related_name="quiz_attempts",
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Start Time")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="End Time")
    score = models.PositiveIntegerField(default=0, verbose_name="Score")

    class Meta:
        unique_together = ('quiz', 'user')
        ordering = ['start_time']
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"

    def __str__(self):
        return f"{self.user} - {self.quiz.title}"


class Answer(TimeStampedModel):
    attempt = models.ForeignKey(
        QuizAttempt,
        related_name="answers",
        on_delete=models.CASCADE,
        verbose_name="Quiz Attempt"
    )
    question = models.ForeignKey(
        Question,
        related_name="answers",
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    text_answer = models.TextField(blank=True, null=True, verbose_name="Text Answer")
    image_answer = models.ImageField(upload_to='answer_images/', blank=True, null=True, verbose_name="Image Answer")

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['question']
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return f"{self.attempt.user} - {self.question.text}"
