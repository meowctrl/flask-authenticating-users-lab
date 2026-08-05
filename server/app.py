#!/usr/bin/env python3

from flask import Flask, make_response, request, session
from flask_migrate import Migrate

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter(
        User.username == request.get_json()['username']
    ).first()
    if user:
        session['user_id'] = user.id
        return UserSchema().dump(user)
    return {'message': 'Invalid login'}, 401

@app.route('/logout', methods=['DELETE'])
def logout():
    session['user_id'] = None
    return {'message': '204: No Content'}, 204

@app.route('/check_session', methods=['GET'])
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return UserSchema().dump(user), 200
    return {}, 401

@app.route('/clear', methods=['DELETE'])
def clear_session():
    session['page_views'] = None
    session['user_id'] = None
    return {}, 204

@app.route('/articles', methods=['GET'])
def index_articles():
    articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
    return articles, 200

@app.route('/articles/<int:id>', methods=['GET'])
def show_article(id):
    session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
    session['page_views'] += 1

    if session['page_views'] <= 3:
        article = Article.query.filter(Article.id == id).first()
        article_json = ArticlesSchema().dump(article)
        return make_response(article_json, 200)

    return {'message': 'Maximum pageview limit reached'}, 401

if __name__ == '__main__':
    app.run(port=5555, debug=True)