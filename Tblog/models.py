from datetime import datetime
import secrets
from flask import current_app
from Tblog.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired

# from itsdangerous import JSONWebSignatureSerializer as Serializer
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    api_key = db.Column(db.String(24))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.set_api_key()

    def set_api_key(self):
        self.api_key = secrets.token_urlsafe(24) 

    def verify_password(self, username, password):
        if username == self.username:
            return check_password_hash(self.password_hash, password)
        else:
            return False
        
    def verify_token(self,token):
        print("verify_token")
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print(data)
        except BadSignature:
            return False
        except SignatureExpired:
            return False
        
        if data['username']==self.username and data['api_key']==self.api_key:
            return True
        else:
            return False

class Category(db.Model):
    """
    文章的分类 tag
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    articles = db.relationship('Article', back_populates='category')

    
    def delete(self):
        default_category = Category.query.get(1)
        articles = self.articles[:]
        for post in articles:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Article(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    author = db.Column(db.String(20)) # 考虑外键
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='articles')
    show = db.Column(db.Boolean, default=True)
    def to_json(self,summary=False):
        if summary:
            return {
            'id': self.id,
            'title': self.title,
            'author':self.author,
            'category': self.category.name,
            'timestamp':str(self.timestamp),
            'show':self.show
            }

        return {
            'id': self.id,
            'title': self.title,
            'author':self.author,
            'body' : self.body,
            'category': self.category.name,
            'timestamp':str(self.timestamp),
            'show':self.show
            }


    # can_comment = db.Column(db.Boolean, default=True)
    # comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     author = db.Column(db.String(30))
#     email = db.Column(db.String(254))
#     site = db.Column(db.String(255))
#     body = db.Column(db.Text)
#     from_admin = db.Column(db.Boolean, default=False)
#     reviewed = db.Column(db.Boolean, default=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

#     replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

#     post = db.relationship('Post', back_populates='comments')
#     replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
#     replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
#     # Same with:
#     # replies = db.relationship('Comment', backref=db.backref('replied', remote_side=[id]),
#     # cascade='all,delete-orphan')

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))