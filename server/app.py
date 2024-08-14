#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return (user.to_dict(), 201)
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422
class CheckSession(Resource):

    def get(self):
        try:
            if "user_id" in session:
                user = db.session.get(User, session.get("user_id"))
                return (user.to_dict(), 200)
            else:
                return {"error": "401: Not Authorized"}, 401
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 401

class Login(Resource):
    def post(self):
        try:
            user = User.query.filter(
            User.username == request.get_json()['username']
            ).first()

            session['user_id'] = user.id
            return user.to_dict()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 401


class Logout(Resource):
    def delete(self): 
        try:
            if session.get("user_id"):
                del session["user_id"]
                return {}, 204
            else:
                return {}, 401
        except Exception as e:
            return {"error": str(e)}, 400

class RecipeIndex(Resource):
    def get(self):
        try: 
            user = User.query.filter(User.id == session["user_id"]).first()
            return [recipe.to_dict() for recipe in user.recipes], 200
        except Exception as e:
            return {"error": str(e)}, 401

    def post(self):
        try:
            if "user_id" in session:
                data = request.get_json()
                new_recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data['minutes_to_complete'],
                    user_id=session["user_id"]
                )
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            else:
                return {"error": "401: Not Authorized"}, 401
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422
    
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)