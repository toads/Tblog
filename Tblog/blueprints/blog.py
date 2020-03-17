from flask import session, render_template, Blueprint, abort
from flask_login import current_user
from sqlalchemy import or_
from Tblog.models import Article, Category, Admin
import markdown
blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/articles')
@blog_bp.route('/')
def index():
    username = session.get('username', 'no_exist_user')
    if current_user.is_authenticated:
        posts = Article.query.order_by(Article.timestamp.desc())
    else:

        posts = Article.query.filter(
            or_(
                Article.category == Category.query.filter_by(
                    name=username).first(),
                Article.show)).order_by(Article.timestamp.desc())
    return render_template('blog/index.html', posts=posts)


@blog_bp.route('/about')
def about():
    admin = Admin.query.first()
    return render_template('blog/about.html', admin=admin)


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    username = session.get('username', 'no_exist_user')

    if current_user.is_authenticated:
        posts = Article.query.with_parent(category).order_by(
            Article.timestamp.desc())
    else:
        posts = Article.query.filter(
            or_(
                Article.category == Category.query.filter_by(
                    name=username).first(),
                Article.show)).with_parent(category).order_by(
                    Article.timestamp.desc())
    if not posts.first():
        abort(404)
    return render_template('blog/category.html',
                           category=category,
                           posts=posts)


# 只读状态展示 blog
@blog_bp.route('/articles/<int:post_id>', methods=['GET'])
def show_article(post_id):
    post = Article.query.get_or_404(post_id)
    username = session.get('username', 'no_exist_user')
    if not post.show and (not current_user.is_authenticated
                          and post.category.name != username):  # noqa
        abort(404)
    if post.body:
        md = markdown.Markdown(extensions=['mdx_math'])
        post.body = md.convert(post.body)

    return render_template('blog/article.html', post=post)
