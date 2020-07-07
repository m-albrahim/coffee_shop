import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

drink = Drink(
    title="esspresso",
    recipe='[{"name": "esspresso", "color": "brown", "parts": 1}]',
)
Drink.insert(drink)

@app.route('/drinks', methods=['GET'])
def retrieve_drinks():
    drinks = Drink.query.all()
    format_drinks = [drink.short() for drink in drinks]

    return jsonify({"success": True, "drinks": format_drinks}), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_in_detail(payload):
    try:
        drinks = Drink.query.all()
        format_drinks = [drink.long() for drink in drinks]

        return jsonify({"success": True, "drinks": format_drinks}), 200
    except:
        abort(500)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    if request.data:
        new_drink = request.get_json()
        title = new_drink['title']
        recipe = json.dumps(new_drink['recipe'])
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })



@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    if drink is None:
        return abort(404)

    drinkInfo = drink.long()
    recipe = request.json.get('recipe', drinkInfo['recipe'])
    drink.title = request.json.get('title', drinkInfo['title'])
    drink.recipe = json.dumps(recipe)
    drink.update()
    return jsonify({'success': True, 'drinks': [drink.long()]})

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(400)

    drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    }), 200


# Error Handling
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Server Error"
    }), 500

@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.description, }), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify(
        {
            "success": False,
            "error": 403,
            "message": "You are forbidden from accessing this resource",
        }
    ), 403