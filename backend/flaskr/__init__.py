import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

"""" UTILS """""


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in selection]
    current_questions = formatted_questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories},
        })

    '''
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @ app.route('/questions')
    def get_paginated_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        categories = Category.query.all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': None,
            'categories': {category.id: category.type for category in categories},
        })

    '''
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        if question is None:
            abort(404)

        try:
            question.delete()
        except Exception as e:
            print('Exception >>>', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'deleted': question_id
            })

    '''
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=['POST'])
    def add_new_question():
        body = request.get_json()

        # Ensure no empty fields
        for field in body.values():
            if not field:
                abort(400)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        question = Question(
            question=new_question,
            answer=new_answer,
            category=new_category,
            difficulty=new_difficulty
        )

        try:
            question.insert()
        except Exception as e:
            print('Exception >>>', e)
            abort(422)
        else:
            return jsonify({
                'success': True,
                'created': question.id
            })

    '''
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm')

        if search_term is None:
            abort(400)

        search_results = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")).all()

        return jsonify({
            'success': True,
            'questions': [q.format() for q in search_results],
            'total_questions': len(search_results),
            'current_category': None
        })

    '''
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_based_on_category(category_id):
        cat_id_str = str(category_id)
        questions = Question.query.filter(
            Question.category == cat_id_str).all()

        if not questions:
            abort(404)

        return jsonify({
            'success': True,
            'questions': [q.format() for q in questions],
            'total_questions': len(questions),
            'current_category': category_id
        })

    '''
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def get_new_quiz_question():
        body = request.get_json()

        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        if previous_questions is None or quiz_category is None:
            abort(400)

        category = quiz_category['id']

        # If player selects All categories:
        # passed as quiz_category = {id:0, type:'click'}
        if category == 0:
            question_pool = Question.query.filter(
                Question.id.notin_(previous_questions)).all()
        else:
            question_pool = Question.query.filter_by(category=str(category)).filter(
                Question.id.notin_(previous_questions)).all()

        # handle quiz end i.e. no more available questions
        if not question_pool:
            next_question = None
        else:
            random_question_index = random.randrange(len(question_pool))
            random_question_from_pool = question_pool[random_question_index]
            next_question = random_question_from_pool.format()

        return jsonify({
            'success': 200,
            'question': next_question
        })

    '''
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    return app

