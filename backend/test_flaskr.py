
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        """Test GET endpoint to retrieve all categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_get_all_categories_error(self):
        """Test GET endpoint to retrieve all categories"""
        res = self.client().post('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertFalse(data['success'])

    def test_get_paginated_questions(self):
        """Test GET paginated questions"""
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        # self.assertTrue(data['current_category'])
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions_error(self):
        """Test GET paginated questions with page out of range"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_delete_question(self):
        """Test DELETE single question"""
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], 5)

    def test_404_delete_question_invalid_id(self):
        """Test DELETE returns 404 if invalid question id passed"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_add_new_question(self):
        prev_question_count = len(Question.query.all())
        
        new_question = {
            'question': 'a',
            'answer': 'b',
            'category': 1,
            'difficulty': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        curr_question_count = len(Question.query.all())

        self.assertEqual(curr_question_count - prev_question_count, 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

