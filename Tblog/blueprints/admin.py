from flask import Blueprint,redirect,render_template,flash,url_for,jsonify,request
from flask_login import login_user, logout_user, login_required, current_user
from Tblog.extensions import db
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/post/articles', methods=['POST'])
def api_upload_article():
    data = request.get_json()
    admin_api_key = Admin.query.first().api_key

    if data.get('api_key') != admin_api_key:
        # 判断是否注册过
        abort(400)
    title = data.get('title')
    body = data.get('body')
    category = data.get('category')
    if not title or not body or not category:
        abort(400)
    
    category_query_result =  Category.query.filter_by(name=category).first()
    if category_query_result is None:
        category_item = Category(name = category)
        db.session.add(category_item)
        db.session.commit()

    post = Post(
        title=title,
        body=body,
        category = Category.query.filter_by(name=category).first()
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({"result":"success"})


@admin_bp.route('/post/articles/new', methods=['GET','POST'])
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
        
        category_query_result =  Category.query.filter_by(name=category).first()
        if category_query_result is None:
            category_item = Category(name = category)
            db.session.add(category_item)
            db.session.commit()

        post = Post(
            title=title,
            body=body,
            category = Category.query.filter_by(name=category).first()
        )
        db.session.add(post)
        db.session.commit()
        return render_template('blog/index.html')
    else:
        return render_template('admin/new_post.html')