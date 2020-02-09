import imaplib
import email
import chardet
import re
from threading import Thread
if __name__ != '__main__':
    from Tblog.models import Article, Category
    from Tblog.extensions import db, scheduler, mail
    from flask import current_app
    from flask_mail import Message


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def parseHeader(message):
    """ 解析邮件首部 """
    subject = message.get('subject')
    dh = email.header.decode_header(subject)
    if type(dh[0][0]) is bytes:
        subject = dh[0][0].decode(dh[0][1])
    from_mail = email.utils.parseaddr(message.get('from'))[1]
    author = from_mail.split('@')[0]

    return subject, author, from_mail


def parseBody(message):
    """ 解析邮件/信体 """
    # 循环信件中的每一个mime的数据块
    mime_block_list = []
    for part in message.walk():
        if not part.is_multipart():
            data = part.get_payload(decode=True)
            encoding = chardet.detect(data)["encoding"]
            mime_block_list.append(data.decode(encoding))  # 解码出文本内容，直接输出来就可以了。

    return mime_block_list[0]


def getMail(host, username, password, port=993, delete=False):
    try:
        serv = imaplib.IMAP4_SSL(host, port)
    except Exception:
        serv = imaplib.IMAP4(host, port)

    serv.login(username, password)
    serv.select()
    # 搜索邮件内容
    typ, data1 = serv.search(None, 'ALL')

    mail_list = []
    for num in data1[0].split()[::-1]:
        typ, data = serv.fetch(num, '(RFC822)')
        if data[0] is not None:
            text = data[0][1]
        else:
            continue
        message = email.message_from_string(
            text.decode('utf-8'))  # 转换为email.message对象
        subject, author, from_mail = parseHeader(message)
        body = parseBody(message)

        mail_list.append((subject, author, from_mail, body))
        if delete:
            serv.store(num, '+FLAGS', '\\Deleted')
    if delete:
        serv.expunge()
    serv.close()
    serv.logout()
    return mail_list


def update_post(post_dict):
    """ 更新文章 """
    category = post_dict.get('category')
    category_query_result = Category.query.filter_by(name=category).first()
    if category_query_result is None:
        category_item = Category(name=category)
        db.session.add(category_item)
        db.session.commit()

    article_id = post_dict.get('article_id')
    article = Article.query.get(article_id)
    if not article:
        article = Article()
    article.title = post_dict.get('title', article.title)
    article.body = post_dict.get('body', article.body)
    article.category = Category.query.filter_by(name=category).first()
    article.author = post_dict.get('username', article.author)
    article.show = post_dict.get('show', article.show)
    db.session.commit()
    send_mail(subject='Tblog: Post Success',
              to=current_app.config['TBLOG_ADMIN_MAIL'],
              html='<h1>Note</h1>'
              '<p>Post Success By: <b>{mail}</b></p>'
              '<h1>Main body</h1>'
              '{body}'.format(mail=post_dict['from_mail'],
                              body=post_dict['body']))
    if post_dict.get('from_mail') != current_app.config['TBLOG_ADMIN_MAIL']:
        send_mail(subject='Tblog: Post Success',
                  to=post_dict.get('from_mail'),
                  html='<h1>Note</h1>'
                  '<p>Post Success By: <b>{mail}</b></p>'.format(
                      mail=post_dict['from_mail']))


def _check_email():
    action_list = ['post', 'update', 'delete', 'hide']
    source_mail_list = current_app.config.get('MAIL_SOURCE')
    host = current_app.config.get('MAIL_HOST')
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    mail_list = getMail(host, username, password, delete=True)
    # mail_list = [('[hide 57] {test} 一封不该被看到的测试件QQQ!!!', 'toads',
    # '# 本文采用MarkDown写成\r\n## 可以通过邮件发布Blog\r\n##
    # 我觉得可以加入利用邮件管理\r\n## 还有就是回复问题(需要有邮件回复x')]
    for mail_data in mail_list:
        post_dict = dict()

        subject, post_dict['author'], post_dict['from_mail'], post_dict[
            'body'] = mail_data

        if (not source_mail_list) and (
                post_dict.get('from_mail') not in source_mail_list):
            send_mail(
                subject='Tblog: Illegal mailbox',
                to=current_app.config['TBLOG_ADMIN_MAIL'],
                html='<h1>Note</h1>'
                '<p>Illegal mailbox <b>{mail}</b></p>'
                '<p>Please check Tblog configuration or mailbox filtering options</p>'
                '<h1>Main body</h1>'
                '{body}'.format(mail=post_dict['from_mail'],
                                body=post_dict['body']))
            continue
        re_result = re.findall(
            r'\s*(?:\[|【)(?#action)(\w*)\s*(?#article_id)(\d*)(?:\]|】)\s*(?:(?:\{)(?#category)(\w*)(?:\})){0,1}\s*(show|hide){0,1}\s*(.*)',  # noqa E501
            subject)[0]
        action = re_result[0].lower()
        if not action:
            continue
        print(re_result)
        post_dict['article_id'] = int(re_result[1] if re_result[1] else -1)
        post_dict['category'] = re_result[2] if re_result[2] else 'by_email'
        post_dict['show'] = False if re_result[3].lower() == 'hide' else True
        post_dict['title'] = re_result[4]
        if action in action_list:
            if action == 'hide' or action == 'delete':
                post_dict = dict(show=False)
            elif action == 'show':
                post_dict = dict(show=True)
            update_post(post_dict)
        else:
            send_mail(
                subject='Tblog Action Error',
                to=post_dict.get('from_mail'),
                html='<h1>Note</h1>'
                '<p>Illegal Action <b>{mail}</b></p>'
                '<p>Please check theme format</p>'
                '<h2>example</h2>'
                '<p>subject: [example_action] {example_category} hide example_title</p>'
                '<p> support action: {action_list}'
                '<h1>Main body</h1>'
                '{body}'.format(mail=post_dict['from_mail'],
                                body=post_dict['body'],
                                action_list=action_list))
        return True


def check_email():
    with scheduler.app.app_context():
        _check_email()


if __name__ == '__main__':
    _check_email()
