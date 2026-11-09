import os
import unittest

from urllib.parse import quote_plus
from flaskr import create_app
from flask import abort
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.environ.get("TEST_DB_NAME", "trivia_test")
        self.database_user = os.environ.get("DB_USER", "postgres")
        self.database_password = os.environ.get("DB_PASSWORD", "password")
        self.database_host = os.environ.get("DB_HOST", "localhost:5432")
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.database_user,
            quote_plus(self.database_password),
            self.database_host,
            self.database_name,
        )

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context, create all tables
        # and seed them with a known set of data
        with self.app.app_context():
            db.create_all()
            self.seed_database()

    def seed_database(self):
        """Insert the categories and questions used by the tests."""
        categories = [
            Category(type=category_type)
            for category_type in [
                "Science",
                "Art",
                "Geography",
                "History",
                "Entertainment",
                "Sports",
            ]
        ]
        db.session.add_all(categories)
        db.session.commit()

        questions = [
            Question(
                question="What is the heaviest organ in the human body?",
                answer="The Liver",
                category="1",
                difficulty=4,
            ),
            Question(
                question="Who discovered penicillin?",
                answer="Alexander Fleming",
                category="1",
                difficulty=3,
            ),
            Question(
                question="Which Dutch graphic artist was a creator of optical illusions?",
                answer="Escher",
                category="2",
                difficulty=1,
            ),
            Question(
                question="What is the largest lake in Africa?",
                answer="Lake Victoria",
                category="3",
                difficulty=2,
            ),
            Question(
                question="Who invented Peanut Butter?",
                answer="George Washington Carver",
                category="4",
                difficulty=2,
            ),
        ]
        db.session.add_all(questions)
        db.session.commit()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ---------- Helpers ----------

    def register_failing_route(self, path, status_code, methods=None):
        """Add a temporary route to the test app that aborts with status_code."""

        def failing_view():
            abort(status_code)

        self.app.add_url_rule(
            path, endpoint=path, view_func=failing_view, methods=methods
        )

    def assert_error_response(self, res, status_code, message):
        """Check that an error is returned as JSON with the expected content."""
        data = res.get_json()

        self.assertEqual(res.status_code, status_code)
        self.assertIsNotNone(data, "error response should be JSON")
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error"], status_code)
        self.assertEqual(data["message"], message)

    def add_questions(self, count, category=1):
        """Insert extra questions, for tests that need more than the seed."""
        with self.app.app_context():
            db.session.add_all(
                [
                    Question(
                        question="Extra question {}".format(index),
                        answer="Extra answer {}".format(index),
                        category=category,
                        difficulty=1,
                    )
                    for index in range(count)
                ]
            )
            db.session.commit()

    # ---------- Error handlers ----------

    def test_404_for_unknown_route(self):
        """Test that an unknown URL returns a JSON 404 error"""
        res = self.client.get("/unknown-route")

        self.assert_error_response(res, 404, "resource not found")

    def test_400_error_handler(self):
        """Test that a 400 error is returned as JSON"""
        self.register_failing_route("/test-400", 400)
        res = self.client.get("/test-400")

        self.assert_error_response(res, 400, "bad request")

    def test_405_for_method_not_allowed(self):
        """Test that a method not allowed on a route returns a JSON 405 error"""
        self.register_failing_route("/test-405", 400, methods=["GET"])
        res = self.client.post("/test-405")

        self.assert_error_response(res, 405, "method not allowed")

    def test_422_error_handler(self):
        """Test that a 422 error is returned as JSON"""
        self.register_failing_route("/test-422", 422)
        res = self.client.get("/test-422")

        self.assert_error_response(res, 422, "unprocessable")

    def test_500_error_handler(self):
        """Test that a 500 error is returned as JSON"""
        self.register_failing_route("/test-500", 500)
        res = self.client.get("/test-500")

        self.assert_error_response(res, 500, "internal server error")

    # ---------- GET /categories ----------

    def test_get_categories(self):
        """Test retrieving all categories as an id: type dictionary"""
        res = self.client.get("/categories")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(
            data["categories"],
            {
                "1": "Science",
                "2": "Art",
                "3": "Geography",
                "4": "History",
                "5": "Entertainment",
                "6": "Sports",
            },
        )

    def test_405_post_categories(self):
        """Test that POST is not allowed on the categories collection"""
        res = self.client.post("/categories")

        self.assert_error_response(res, 405, "method not allowed")

    # ---------- DELETE /questions/<id> ----------

    def test_delete_question(self):
        """Test deleting a question, and that the deletion persists"""
        res = self.client.delete("/questions/1")
        data = res.get_json()

        with self.app.app_context():
            question = db.session.get(Question, 1)
            remaining = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], 1)
        self.assertIsNone(question)
        self.assertEqual(remaining, 4)

    def test_404_delete_unknown_question(self):
        """Test deleting a question that does not exist"""
        res = self.client.delete("/questions/1000")

        self.assert_error_response(res, 404, "resource not found")

    # ---------- CORS ----------

    def test_cors_headers(self):
        """Test that responses allow cross-origin requests"""
        res = self.client.get(
            "/categories", headers={"Origin": "http://localhost:3000"}
        )

        self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn(
            "Content-Type", res.headers.get("Access-Control-Allow-Headers", "")
        )
        self.assertIn(
            "DELETE", res.headers.get("Access-Control-Allow-Methods", "")
        )

    # ---------- GET /questions ----------

    def test_get_paginated_questions(self):
        """Test retrieving the first page of questions with categories"""
        res = self.client.get("/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 5)
        self.assertEqual(data["totalQuestions"], 5)
        self.assertEqual(len(data["categories"]), 6)
        self.assertIn("currentCategory", data)
        self.assertEqual(
            set(data["questions"][0].keys()),
            {"id", "question", "answer", "category", "difficulty"},
        )

    def test_questions_are_paginated_by_ten(self):
        """Test that questions are returned in pages of ten"""
        self.add_questions(7)

        first_page = self.client.get("/questions?page=1").get_json()
        second_page = self.client.get("/questions?page=2").get_json()

        self.assertEqual(first_page["totalQuestions"], 12)
        self.assertEqual(len(first_page["questions"]), 10)
        self.assertEqual(len(second_page["questions"]), 2)

    def test_404_requesting_questions_beyond_valid_page(self):
        """Test requesting a page of questions that does not exist"""
        res = self.client.get("/questions?page=1000")

        self.assert_error_response(res, 404, "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
