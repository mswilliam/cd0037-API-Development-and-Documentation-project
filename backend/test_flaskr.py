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
                category=1,
                difficulty=4,
            ),
            Question(
                question="Who discovered penicillin?",
                answer="Alexander Fleming",
                category=1,
                difficulty=3,
            ),
            Question(
                question=(
                    "Which Dutch graphic artist was a creator "
                    "of optical illusions?"
                ),
                answer="Escher",
                category=2,
                difficulty=1,
            ),
            Question(
                question="What is the largest lake in Africa?",
                answer="Lake Victoria",
                category=3,
                difficulty=2,
            ),
            Question(
                question="Who invented Peanut Butter?",
                answer="George Washington Carver",
                category=4,
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
        """Add a temporary test route that aborts with status_code."""

        def failing_view():
            abort(status_code)

        self.app.add_url_rule(
            path, endpoint=path, view_func=failing_view, methods=methods
        )

    def assert_error_response(self, res, status_code, message):
        """Check that an error response is JSON with the expected content."""
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
        """Test that a method not allowed returns a JSON 405 error"""
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

    # ---------- PUT /questions/<id> ----------

    def test_update_question(self):
        """Test updating a question, and that the update persists"""
        updated_question = {
            "question": "What is the heaviest internal organ in the body?",
            "answer": "The liver",
            "difficulty": 3,
            "category": 2,
        }
        res = self.client.put("/questions/1", json=updated_question)
        data = res.get_json()

        with self.app.app_context():
            question = db.session.get(Question, 1)
            total = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["updated"], 1)
        self.assertEqual(data["question"], dict(updated_question, id=1))
        self.assertEqual(question.format(), dict(updated_question, id=1))
        self.assertEqual(total, 5)

    def test_404_update_unknown_question(self):
        """Test updating a question that does not exist"""
        res = self.client.put(
            "/questions/1000",
            json={
                "question": "A question",
                "answer": "An answer",
                "difficulty": 1,
                "category": 1,
            },
        )

        self.assert_error_response(res, 404, "resource not found")

    def test_400_update_question_with_invalid_difficulty(self):
        """Test that an invalid update is rejected and not saved"""
        res = self.client.put(
            "/questions/1",
            json={
                "question": "What is the heaviest organ in the human body?",
                "answer": "The Liver",
                "difficulty": 10,
                "category": 1,
            },
        )

        with self.app.app_context():
            question = db.session.get(Question, 1)

        self.assert_error_response(res, 400, "bad request")
        self.assertEqual(question.format()["difficulty"], 4)

    def test_422_update_question_with_unknown_category(self):
        """Test that moving a question to an unknown category is rejected"""
        res = self.client.put(
            "/questions/1",
            json={
                "question": "What is the heaviest organ in the human body?",
                "answer": "The Liver",
                "difficulty": 4,
                "category": 1000,
            },
        )

        with self.app.app_context():
            question = db.session.get(Question, 1)

        self.assert_error_response(res, 422, "unprocessable")
        self.assertEqual(question.format()["category"], 1)

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
        allowed_methods = res.headers.get("Access-Control-Allow-Methods", "")
        self.assertIn("DELETE", allowed_methods)
        self.assertIn("PUT", allowed_methods)

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

    # ---------- GET /categories/<id>/questions ----------

    def test_get_questions_by_category(self):
        """Test retrieving only the questions of a given category"""
        res = self.client.get("/categories/1/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 2)
        self.assertEqual(data["totalQuestions"], 2)
        self.assertEqual(data["currentCategory"], "Science")
        self.assertTrue(
            all(question["category"] == 1 for question in data["questions"])
        )

    def test_get_questions_by_category_without_questions(self):
        """Test that an existing category with no questions is not an error"""
        res = self.client.get("/categories/6/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["totalQuestions"], 0)
        self.assertEqual(data["currentCategory"], "Sports")

    def test_404_get_questions_by_unknown_category(self):
        """Test retrieving the questions of a category that does not exist"""
        res = self.client.get("/categories/1000/questions")

        self.assert_error_response(res, 404, "resource not found")

    # ---------- POST /questions (create) ----------

    def test_create_question(self):
        """Test creating a question, and that it is saved in the database"""
        new_question = {
            "question": "What is the capital of Luxembourg?",
            "answer": "Luxembourg",
            "difficulty": 2,
            "category": 3,
        }
        res = self.client.post("/questions", json=new_question)
        data = res.get_json()

        with self.app.app_context():
            question = db.session.get(Question, data["created"])
            total = Question.query.count()

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertIsNotNone(question)
        self.assertEqual(
            question.format()["question"], new_question["question"]
        )
        self.assertEqual(question.format()["category"], 3)
        self.assertEqual(total, 6)

    def test_create_question_with_string_values(self):
        """Test that numeric fields sent as strings by the form are accepted"""
        res = self.client.post(
            "/questions",
            json={
                "question": "Who painted the Mona Lisa?",
                "answer": "Leonardo da Vinci",
                "difficulty": "1",
                "category": "2",
            },
        )
        data = res.get_json()

        with self.app.app_context():
            question = db.session.get(Question, data["created"])

        self.assertEqual(res.status_code, 201)
        self.assertEqual(question.format()["difficulty"], 1)
        self.assertEqual(question.format()["category"], 2)

    def test_400_create_question_with_missing_fields(self):
        """Test that a question without an answer is rejected and not saved"""
        res = self.client.post(
            "/questions",
            json={
                "question": "A question without answer",
                "difficulty": 1,
                "category": 1,
            },
        )

        with self.app.app_context():
            total = Question.query.count()

        self.assert_error_response(res, 400, "bad request")
        self.assertEqual(total, 5)

    def test_422_create_question_with_unknown_category(self):
        """Test that a question in an unknown category is rejected"""
        res = self.client.post(
            "/questions",
            json={
                "question": "A question",
                "answer": "An answer",
                "difficulty": 1,
                "category": 1000,
            },
        )

        with self.app.app_context():
            total = Question.query.count()

        self.assert_error_response(res, 422, "unprocessable")
        self.assertEqual(total, 5)

    # ---------- POST /questions (search) ----------

    def test_search_questions_with_results(self):
        """Test searching questions with a case-insensitive substring"""
        res = self.client.post("/questions", json={"searchTerm": "who"})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["totalQuestions"], 2)
        self.assertEqual(len(data["questions"]), 2)
        self.assertIn("currentCategory", data)
        self.assertTrue(
            all("who" in q["question"].lower() for q in data["questions"])
        )

    def test_search_questions_without_results(self):
        """Test that a search without results returns an empty list"""
        res = self.client.post("/questions", json={"searchTerm": "applejacks"})
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["totalQuestions"], 0)

    def test_400_search_questions_with_invalid_term(self):
        """Test that a search term which is not a string is rejected"""
        res = self.client.post("/questions", json={"searchTerm": 123})

        self.assert_error_response(res, 400, "bad request")

    # ---------- POST /quizzes ----------

    def test_play_quiz_all_categories(self):
        """Test that ALL (id 0) draws from every category, minus previous"""
        res = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [1, 2, 3, 4],
                "quiz_category": {"type": "click", "id": 0},
            },
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["question"]["id"], 5)

    def test_play_quiz_by_category_excludes_previous_questions(self):
        """Test drawing a question of the category not asked yet"""
        res = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [1],
                "quiz_category": {"type": "Science", "id": "1"},
            },
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"]["id"], 2)
        self.assertEqual(data["question"]["category"], 1)

    def test_play_quiz_returns_null_when_no_question_left(self):
        """Test that the end of the quiz is signaled by a null question"""
        res = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [1, 2],
                "quiz_category": {"type": "Science", "id": "1"},
            },
        )
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNone(data["question"])

    def test_400_play_quiz_with_invalid_body(self):
        """Test that a quiz request without category is rejected"""
        res = self.client.post("/quizzes", json={"previous_questions": []})

        self.assert_error_response(res, 400, "bad request")

    def test_404_play_quiz_with_unknown_category(self):
        """Test playing a quiz in a category that does not exist"""
        res = self.client.post(
            "/quizzes",
            json={
                "previous_questions": [],
                "quiz_category": {"type": "Unknown", "id": 1000},
            },
        )

        self.assert_error_response(res, 404, "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
