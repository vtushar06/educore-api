from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from .models import Attempt, Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "choices", "correct_answer", "points", "order")

    def to_representation(self, instance):
        """Strip correct answers when serving to students."""
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Only hide answers for non-instructor users
        if request and request.user.role not in ("instructor", "admin"):
            if instance.question_type == "mcq" and data.get("choices"):
                data["choices"] = [
                    {"text": c["text"]} for c in data["choices"]
                ]
            data.pop("correct_answer", None)
        return data


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "text", "question_type", "choices", "correct_answer", "points", "order")
        read_only_fields = ("id",)

    def validate(self, attrs):
        qtype = attrs.get("question_type", "mcq")
        if qtype == "mcq":
            choices = attrs.get("choices")
            if not choices or not isinstance(choices, list):
                raise serializers.ValidationError(
                    {"choices": "MCQ questions require a list of choices."}
                )
            correct_count = sum(1 for c in choices if c.get("is_correct"))
            if correct_count < 1:
                raise serializers.ValidationError(
                    {"choices": "At least one choice must be marked correct."}
                )
        elif qtype == "short_answer":
            if not attrs.get("correct_answer", "").strip():
                raise serializers.ValidationError(
                    {"correct_answer": "Short-answer questions require a correct answer."}
                )
        return attrs


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = (
            "id",
            "lesson",
            "title",
            "passing_score",
            "max_attempts",
            "time_limit_minutes",
            "questions",
        )
        read_only_fields = ("id",)


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "passing_score",
            "max_attempts",
            "time_limit_minutes",
            "questions",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        questions_data = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)
        for q_data in questions_data:
            Question.objects.create(quiz=quiz, **q_data)
        return quiz


class AttemptSubmitSerializer(serializers.Serializer):
    """
    Accepts a list of answers and grades the attempt.

    Expected payload:
        {"answers": [{"question_id": 1, "answer": "Option A"}, ...]}
    """

    answers = serializers.ListField(child=serializers.DictField())

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("At least one answer is required.")
        for entry in value:
            if "question_id" not in entry or "answer" not in entry:
                raise serializers.ValidationError(
                    "Each answer must have 'question_id' and 'answer' fields."
                )
        return value

    def grade(self, quiz, student):
        """Grade the submitted answers and create an Attempt record."""
        answers = self.validated_data["answers"]
        questions = {q.id: q for q in quiz.questions.all()}

        total_points = sum(q.points for q in questions.values())
        earned_points = 0

        for entry in answers:
            question = questions.get(entry["question_id"])
            if not question:
                continue

            if question.question_type == "mcq":
                # Check if the submitted answer matches any correct choice
                correct_texts = [
                    c["text"] for c in (question.choices or []) if c.get("is_correct")
                ]
                if entry["answer"] in correct_texts:
                    earned_points += question.points
            elif question.question_type == "short_answer":
                # Case-insensitive comparison for short answers
                if entry["answer"].strip().lower() == question.correct_answer.strip().lower():
                    earned_points += question.points

        score = Decimal(0)
        if total_points > 0:
            score = round(Decimal(earned_points) / Decimal(total_points) * 100, 2)

        passed = score >= quiz.passing_score

        attempt = Attempt.objects.create(
            student=student,
            quiz=quiz,
            answers=answers,
            score=score,
            passed=passed,
            completed_at=timezone.now(),
        )

        # Compute time_taken from started_at
        if attempt.started_at and attempt.completed_at:
            delta = attempt.completed_at - attempt.started_at
            attempt.time_taken_seconds = int(delta.total_seconds())
            attempt.save(update_fields=["time_taken_seconds"])

        return attempt


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = (
            "id",
            "student",
            "quiz",
            "answers",
            "score",
            "passed",
            "started_at",
            "completed_at",
            "time_taken_seconds",
        )
        read_only_fields = fields
