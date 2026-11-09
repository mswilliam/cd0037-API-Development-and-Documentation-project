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
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,OPTIONS"
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

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    # ---------- Error handlers ----------

    def error_response(status_code, message):
        return (
            jsonify({"success": False, "error": status_code, "message": message}),
            status_code,
        )

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

