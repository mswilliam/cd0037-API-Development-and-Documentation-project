import os
import unittest

from urllib.parse import quote_plus
from flaskr import create_app
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

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
