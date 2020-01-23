from flask import render_template, flash, redirect, url_for, \
    request, current_app, Blueprint, abort, make_response, json,\
    jsonify

from Tblog.models import Article, Category, Admin

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Article.query.filter_by(show=True).order_by(Article.timestamp.desc())
    return render_template('blog/index.html', posts=posts)

@blog_bp.route('/about')
def about():
    admin = Admin.query.first()
    return render_template('blog/about.html',admin=admin)


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    posts = Article.query.filter_by(show=True).with_parent(category).order_by(Article.timestamp.desc())
    return render_template('blog/category.html', category=category, posts=posts)

# 只读状态展示 blog
@blog_bp.route('/articles/<int:post_id>', methods=['GET'])
def show_article(post_id):
    post = Article.query.get_or_404(post_id)
    if not post.show:
        abort(404) 
    return render_template('blog/article.html', post=post)

