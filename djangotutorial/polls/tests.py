import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question


# --- Test cho model Question ---
class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() trả về False nếu pub_date ở tương lai.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        Trả về False nếu pub_date quá 1 ngày trước.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        Trả về True nếu pub_date trong vòng 1 ngày.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


# --- Hàm tiện ích để tạo câu hỏi ---
def create_question(question_text, days):
    """
    Tạo câu hỏi với question_text và pub_date = hiện tại + days.
    days > 0: tương lai
    days < 0: quá khứ
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# --- Test cho IndexView ---
class QuestionIndexViewTests(TestCase):

    def test_no_questions(self):
        """
        Nếu không có câu hỏi, hiển thị thông báo phù hợp.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """
        Câu hỏi quá khứ được hiển thị trên index page.
        """
        question = create_question("Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_future_question(self):
        """
        Câu hỏi tương lai không xuất hiện.
        """
        create_question("Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """
        Chỉ câu hỏi quá khứ xuất hiện.
        """
        question = create_question("Past question.", days=-30)
        create_question("Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_question_list"], [question])

    def test_two_past_questions(self):
        """
        Nhiều câu hỏi quá khứ xuất hiện theo thứ tự mới nhất trước.
        """
        question1 = create_question("Past question 1.", days=-30)
        question2 = create_question("Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"], [question2, question1]
        )


# --- Test cho DetailView ---
class QuestionDetailViewTests(TestCase):

    def test_future_question(self):
        """
        DetailView của câu hỏi tương lai => trả về 404.
        """
        future_question = create_question("Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        DetailView của câu hỏi quá khứ hiển thị text câu hỏi.
        """
        past_question = create_question("Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
