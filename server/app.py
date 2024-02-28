#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio')
        )

        user.password_hash = json['password']

        try: 
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            response_data = {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
            return response_data, 201
        
        except IntegrityError:
            error = {'error': 'invalid input'}
            return error, 422
        
        
class CheckSession(Resource):
    def get(self):
        user_id=session['user_id']
        try:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        except:
            error = {'error': 'not authorized'}
            return error, 401

class Login(Resource):
    def post(self):
        try:
            username = request.get_json()['username']
            user = User.query.filter(User.username == username).first()
            password = request.get_json()['password']
            if user.authenticate(password):
                session['user_id'] = user.id
                return user.to_dict(), 200
        except:
            error = {'error': 'not authorized'}
            return error, 401
            

class Logout(Resource):
    def delete(self):
        user_id=session['user_id']
        if user_id:
            session['user_id'] = None
            return {}, 204
        else:
            error = {'error': 'not authorized'}
            return error, 401

class RecipeIndex(Resource):
    def get(self):
        user_id=session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            recipes = [recipe.to_dict() for recipe in user.recipes]
            print(user)
            print(recipes)
            return recipes, 200
        else:
            error = {'error': 'not authorized'}
            return error, 401
        
    def post(self):
        user_id=session['user_id']
        if user_id:
            try:
                recipe_data = request.get_json()
                new_recipe = Recipe(
                    user_id=user_id,
                    title=recipe_data.get('title'),
                    instructions=recipe_data.get('instructions'),
                    minutes_to_complete=recipe_data.get('minutes_to_complete')
                )
                db.session.add(new_recipe)
                db.session.commit()

                return new_recipe.to_dict(), 201

            except:
                error={'error': 'not a valid recipt'}
                return error, 422
        else:
            error = {'error': 'not authorized'}
            return error, 401


        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)