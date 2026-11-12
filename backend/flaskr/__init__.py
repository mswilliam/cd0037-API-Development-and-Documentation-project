from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def get_categories_dict():
    """Return all categories as an {id: type} dictionary."""
    categories = Category.query.order_by(Category.id).all()
    return {category.id: category.type for category in categories}


def paginate_questions(request, selection):
    """Return the formatted questions of the page requested in the query."""
    page = request.args.get("page", 1, type=int)
    if page < 1:
        return []

    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    return [question.format() for question in selection[start:end]]


def validate_question_body(body):
    """Validate a question payload and return its cleaned values.

    The frontend form sends difficulty and category as strings, so both
    are converted to integers. Aborts with 400 if a field is missing or
    invalid, and with 422 if the category does not exist.
    """
    question_text = str(body.get("question") or "").strip()
    answer_text = str(body.get("answer") or "").strip()
    if not question_text or not answer_text:
        abort(400)

    try:
        difficulty = int(body.get("difficulty"))
        category_id = int(body.get("category"))
    except (TypeError, ValueError):
        abort(400)

    if not 1 <= difficulty <= 5:
        abort(400)

    if db.session.get(Category, category_id) is None:
        abort(422)

    return {
        "question": question_text,
        "answer": answer_text,
        "difficulty": difficulty,
        "category": category_id,
    }


def create_app(test_config=None):
    """Create and configure the Trivia API application.

    test_config can provide a SQLALCHEMY_DATABASE_URI, used by the tests
    to connect to the test database instead of the development one.
    """
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        """Set the CORS headers allowed by the API on every response."""
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type,Authorization"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,DELETE,OPTIONS"
        )
        return response

    # ---------- Categories ----------

    @app.route("/categories")
    def retrieve_categories():
        """Return all categories as an {id: type} dictionary."""
        return jsonify({"success": True, "categories": get_categories_dict()})

    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_by_category(category_id):
        """Return the questions of a category, with the category name.

        An unknown category returns a 404 error, while an existing
        category without questions returns an empty list.
        """
        category = Category.query.filter(
            Category.id == category_id
        ).one_or_none()
        if category is None:
            abort(404)

        selection = (
            Question.query.filter(Question.category == category_id)
            .order_by(Question.id)
            .all()
        )
        current_questions = paginate_questions(request, selection)

        # Only a page beyond the last one is an error, not an empty category
        if len(current_questions) == 0 and len(selection) > 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "totalQuestions": len(selection),
                "currentCategory": category.type,
            }
        )

    # ---------- Questions ----------

    @app.route("/questions")
    def retrieve_questions():
        """Return a page of 10 questions, with all categories."""
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "totalQuestions": len(selection),
                "categories": get_categories_dict(),
                "currentCategory": None,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        """Delete a question by id and return its id."""
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)

        try:
            question.delete()
        except Exception:
            # Keep the session usable for the next requests
            db.session.rollback()
            abort(422)

        return jsonify({"success": True, "deleted": question_id})

    def search_questions(search_term):
        """Return the questions containing search_term (case-insensitive)."""
        if not isinstance(search_term, str):
            abort(400)

        selection = (
            Question.query.filter(
                Question.question.ilike("%{}%".format(search_term))
            )
            .order_by(Question.id)
            .all()
        )

        return jsonify(
            {
                "success": True,
                "questions": paginate_questions(request, selection),
                "totalQuestions": len(selection),
                "currentCategory": None,
            }
        )

    def create_question(body):
        """Validate the request body and save a new question."""
        question = Question(**validate_question_body(body))
        try:
            question.insert()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({"success": True, "created": question.id}), 201

    @app.route("/questions", methods=["POST"])
    def create_or_search_questions():
        """Search questions if the body has a searchTerm, else create one."""
        body = request.get_json(silent=True) or {}

        if "searchTerm" in body:
            return search_questions(body["searchTerm"])
        return create_question(body)

    # ---------- Quiz ----------

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        """Return a random question not asked yet, or null at the end.

        A category id of 0 means all categories: it is what the frontend
        sends when the player chooses ALL.
        """
        body = request.get_json(silent=True) or {}
        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get("quiz_category")

        if not isinstance(previous_questions, list) or not all(
            isinstance(question_id, int) for question_id in previous_questions
        ):
            abort(400)
        if not isinstance(quiz_category, dict):
            abort(400)

        try:
            category_id = int(quiz_category.get("id", 0))
        except (TypeError, ValueError):
            abort(400)

        query = Question.query
        if category_id != 0:
            if db.session.get(Category, category_id) is None:
                abort(404)
            query = query.filter(Question.category == category_id)
        if previous_questions:
            query = query.filter(Question.id.notin_(previous_questions))

        candidates = query.all()
        question = random.choice(candidates).format() if candidates else None

        return jsonify({"success": True, "question": question})

    # ---------- Error handlers ----------

    def error_response(status_code, message):
        """Build the JSON error response shared by all error handlers."""
        body = {"success": False, "error": status_code, "message": message}
        return jsonify(body), status_code

    @app.errorhandler(400)
    def bad_request(error):
        return error_response(400, "bad request")

    @app.errorhandler(404)
    def not_found(error):
        return error_response(404, "resource not found")

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(405, "method not allowed")

    @app.errorhandler(422)
    def unprocessable(error):
        return error_response(422, "unprocessable")

    @app.errorhandler(500)
    def internal_server_error(error):
        return error_response(500, "internal server error")

    return app
