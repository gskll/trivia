
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

        # Insert question to test delete
        prev_question_count = len(Question.query.all())

        test_question = Question(
            question='a', answer='b', category=1, difficulty=1)
        test_question.insert()

        temp_question_count = len(Question.query.all())

        test_question_id = test_question.id

        res = self.client().delete(f'/questions/{test_question_id}')

        final_question_count = len(Question.query.all())

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], test_question_id)
        self.assertEqual(prev_question_count, final_question_count)
        self.assertEqual(temp_question_count - prev_question_count, 1)
        self.assertFalse(Question.query.get(test_question_id))

    def test_404_delete_question_invalid_id(self):
        """Test DELETE returns 404 if invalid question id passed"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_add_new_question(self):
        prev_question_count = len(Question.query.all())

        test_question = {
            'question': 'a',
            'answer': 'b',
            'category': 1,
            'difficulty': 1
        }

        res = self.client().post('/questions', json=test_question)
        data = json.loads(res.data)

        curr_question_count = len(Question.query.all())

        self.assertEqual(curr_question_count - prev_question_count, 1)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        # Delete test_question from database for subsequent testing
        q = Question.query.get(data['created'])
        q.delete()

    def test_422_add_new_question_empty_field(self):
        prev_question_count = len(Question.query.all())

        new_question = {
            'question': '',
            'answer': 'b',
            'category': 1,
            'difficulty': 1
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        curr_question_count = len(Question.query.all())

        self.assertEqual(curr_question_count, prev_question_count)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    def test_search_questions(self):
        search_one = {'searchTerm': 'title'}
        search_two = {'searchTerm': ''}

        res_one = self.client().post('/questions/search', json=search_one)
        data_one = json.loads(res_one.data)

        res_two = self.client().post('/questions/search', json=search_two)
        data_two = json.loads(res_two.data)

        self.assertEqual(res_one.status_code, 200)
        self.assertTrue(data_one['success'])
        self.assertTrue(len(data_one['questions']))
        self.assertEqual(data_one['total_questions'], 2)

        self.assertEqual(res_two.status_code, 200)
        self.assertTrue(data_two['success'])
        self.assertTrue(len(data_two['questions']))
        self.assertEqual(data_two['total_questions'], 19)

    def test_422_search_no_term_on_request(self):
        search = {}
        res = self.client().post('/questions/search', json=search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])

    def test_get_questions_from_category(self):
        category_id = 1

        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'], 1)
        self.assertEqual(data['total_questions'], 3)
        self.assertTrue(len(data['questions']))

    def test_404_get_questions_invalid_category(self):
        category_id = 1000

        res = self.client().get(f'/categories/{category_id}/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

