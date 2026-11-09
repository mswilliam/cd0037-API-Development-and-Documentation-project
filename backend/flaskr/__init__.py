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


def create_app(test_config=None):
    # create and configure the app
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
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type,Authorization"
        )
        response.headers["Access-Control-Allow-Methods"] = (
            "GET,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/categories")
    def retrieve_categories():
        return jsonify({"success": True, "categories": get_categories_dict()})

    @app.route("/questions")
    def retrieve_questions():
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
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)

        try:
            question.delete()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({"success": True, "deleted": question_id})

    def search_questions(search_term):
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

        question = Question(
            question=question_text,
            answer=answer_text,
            category=category_id,
            difficulty=difficulty,
        )
        try:
            question.insert()
        except Exception:
            db.session.rollback()
            abort(422)

        return jsonify({"success": True, "created": question.id}), 201

    @app.route("/questions", methods=["POST"])
    def create_or_search_questions():
        body = request.get_json(silent=True) or {}

        if "searchTerm" in body:
            return search_questions(body["searchTerm"])
        return create_question(body)

    @app.route("/categories/<int:category_id>/questions")
    def retrieve_questions_by_category(category_id):
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

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
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
