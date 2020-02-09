from flask import Blueprint, abort, jsonify, make_response
from Tblog.models import Admin, Article, Category
from Tblog.extensions import db, auth

from flask_restful import Resource, Api
from Tblog.forms import (post_article_parser, put_article_parser,
                         delete_article_parser)
api_bp = Blueprint('api', __name__)

api = Api(api_bp, catch_all_404s=True)


@auth.get_password
def get_password(username):
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        return admin.api_key
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


def check_token(token):
    admins = Admin.query.all()
    for admin in admins:
        if admin.verify_token(token):
            break
    else:
        abort(400,
              "Verify token error, please check token or connect the admin")
    return admin.username


class Token(Resource):
    @auth.login_required
    def get(self):
        token = Admin.query.filter_by(username=auth.username).first().api_key
        return jsonify({'username': auth.username(), 'token': token})


class ArticleItem(Resource):
    def get(self, id):
        post = Article.query.get(id)
        if post:
            return post.to_json()
        return

    def put(self, id):
        args = put_article_parser.parse_args()
        username = check_token(args.token)
        category_query_result = Category.query.filter_by(
            name=args.category).first()
        if category_query_result is None:
            category_item = Category(name=args.category)
            db.session.add(category_item)
            db.session.commit()
        article = Article.query.get(id)
        if not article:
            article = Article()
            article.id = id
            article.author = username

        if article.author != username:
            abort(403, "Only the own can edit this article")
        if args.title:
            article.title = args.title
        if args.body:
            article.body = args.body
        if args.category:
            article.category = Category.query.filter_by(
                name=args.category).first()
        if args.show:
            article.show = args.show
        article.author = username
        db.session.add(article)
        db.session.commit()
        return {"article_id": article.id}

    def delete(self, id):
        args = delete_article_parser.parse_args()
        admin = Admin.query.first()
        article = Article.query.filter_by(id=id)
        username = check_token(args.token)
        article_first = article.first()
        if article_first:
            if not (admin.verify_token(args.token) or # noqa W504
                    article_first.author != username):
                abort(403, "Only the admin or owner can delete the article")
            article.delete()
            db.session.commit()
            return jsonify(message='article delete success')
        else:
            abort(400, "article has been delete")


class ArticlesList(Resource):
    def get(self):
        articles = Article.query.filter_by(show=True).all()
        articles_dict = dict(articles=[])
        for article in articles:
            articles_dict['articles'].append(article.to_json(summary=True))
        return articles_dict

    def post(self):
        args = post_article_parser.parse_args()

        admins = Admin.query.all()
        for admin in admins:
            if admin.verify_token(args.token):
                break
        else:
            abort(400, "VerifyTokenError")

        category_query_result = Category.query.filter_by(
            name=args.category).first()
        if category_query_result is None:
            category_item = Category(name=args.category)
            db.session.add(category_item)
            db.session.commit()

        article = Article(
            title=args.title,
            body=args.body,
            category=Category.query.filter_by(name=args.category).first(),
            author=admin.username,
            show=args.show)
        db.session.add(article)
        db.session.commit()
        return {"article_id": article.id}


api.add_resource(ArticlesList, '/articles')
api.add_resource(ArticleItem, '/articles/<int:id>')
