#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        if User.query.filter_by(username=username).first():
            return {"error": "Username already exists"}, 422
        try:
            user = User(username=json.get('username'))
            user.password_hash = json.get('password')
            user.image_url = json.get('image_url')
            user.bio = json.get('bio')
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except Exception as e:
            return {"error": "An error occurred during signup"}, 422



class CheckSession(Resource):
    
    def get(self):
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        if user:
            return user.to_dict(), 200
        
        return {"error": "You are not logged in."}, 401

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        username = json.get('username')
        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(json.get('password')):
            session['user_id'] = user.id
            return user.to_dict(), 200

        return {"error": "Incorrect username or password"}, 401

class Logout(Resource):
    
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        return {"error":"Not currently logged in."}, 401

class RecipeIndex(Resource):
    
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            user_recipes_dicts = [recipe.to_dict() for recipe in user.recipes]
            return user_recipes_dicts, 200
        else:
            return {"error": "Not currently logged in."}, 401

    def post(self):
        user_id = session['user_id']
        if user_id:
            json = request.get_json()
            if json.get('title') and len(json.get('instructions')) >= 50:
                new_recipe = Recipe(
                    title=json.get('title'),
                    instructions=json.get('instructions'),
                    minutes_to_complete=json.get('minutes_to_complete'),
                    user_id=user_id,
                )
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201

            return {"error": "Invalid title or instructions."}, 422

        return {"error": "Not currently logged in."}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)