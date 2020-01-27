from flask import Blueprint, render_template, request, abort
from flask_login import login_required
from Tblog.extensions import db
from Tblog.models import Admin, Category, Article
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/articles/new', methods=['GET', 'POST'])
@login_required
def upload_article():
    if request.method == 'POST':
        data = request.get_json()
        admin_api_key = Admin.query.first().api_key

        if data.get('api_key') != admin_api_key:
            # 判断是否注册过
            abort(404)
        title = data.get('title')
        body = data.get('body')
        category = data.get('category')
        if not title or not body or not category:
            abort(404)

        category_query_result = Category.query.filter_by(name=category).first()
        if category_query_result is None:
            category_item = Category(name=category)
            db.session.add(category_item)
            db.session.commit()

        post = Article(
            title=title,
            body=body,
            category=Category.query.filter_by(name=category).first())
        db.session.add(post)
        db.session.commit()
        return render_template('blog/index.html')
    else:
        return render_template('admin/new_post.html')
