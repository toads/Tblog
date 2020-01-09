from flask import render_template, flash, redirect, url_for, \
    request, current_app, Blueprint, abort, make_response, json,\
    jsonify

from Tblog.models import Post, Category

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc())
    return render_template('blog/index.html', posts=posts)

@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc())
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)

# 只读状态展示 blog
@blog_bp.route('/post/<int:post_id>', methods=['GET'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('blog/post.html', post=post)

@blog_bp.route('/post/article/<int:article_id>')
def show_article(article_id):
    return render_template('blog/article.html', article_id=article_id)

@blog_bp.route('/post/upload', methods=['POST'])
def upload_article():
    data = request.get_json()
    if data.get('token') == token:
        pass
    title = data['title']
    body = data['body']
    category = data['category']
    if not title or not body or not category:
        abort(404)
    # 处理注册函数!@!!!!!    
    return render_template('blog')