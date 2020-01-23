#coding:utf-8
import imaplib
import email
import chardet
import re
if __name__ != '__main__':
    from Tblog.models import Article,Category
    from flask import current_app
    from Tblog.extensions import db, scheduler

def parseHeader(message):
    """ 解析邮件首部 """
    subject = message.get('subject')
    dh = email.header.decode_header(subject)
    if type(dh[0][0]) is bytes:
        subject = dh[0][0].decode(dh[0][1])
    subject = dh[0][0]
    author = email.utils.parseaddr(message.get('from'))[1].split('@')[0]
    return subject, author
     
 
 
def parseBody(message):
    """ 解析邮件/信体 """
    # 循环信件中的每一个mime的数据块
    mime_block_list = []
    for part in message.walk():
        if not part.is_multipart():
            data = part.get_payload(decode=True)
            encoding = chardet.detect(data)["encoding"]
            mime_block_list.append(data.decode(encoding)) #解码出文本内容，直接输出来就可以了。

    return mime_block_list[0]

 
def getMail(host, username, password, port=993,delete=False):
    try:
        serv = imaplib.IMAP4_SSL(host, port)
    except Exception as e:
        serv = imaplib.IMAP4(host, port)
 
    serv.login(username, password)
    serv.select()
    # 搜索邮件内容
    typ, data1 = serv.search(None, 'ALL')
 
    mail_list = []
    for num in data1[0].split()[::-1]:
        typ, data = serv.fetch(num, '(RFC822)')
        if data[0] != None:
            text = data[0][1]
        else:
            continue
        message = email.message_from_string(text.decode('utf-8'))   # 转换为email.message对象
        subject, author = parseHeader(message)
        body = parseBody(message) 
        mail_list.append((subject,author,body))
        if delete:   serv.store(num, '+FLAGS', '\\Deleted')
    if delete: serv.expunge()
    serv.close()
    serv.logout()
    return mail_list

def update_post(article_id,title,body,username,category,show):
    category_query_result =  Category.query.filter_by(name=category).first()
    if category_query_result is None:
        category_item = Category(name = category)
        db.session.add(category_item)
        db.session.commit()
    if article_id:
        article = Article.query.get(article_id)
        if article:
            if title: article.title = title
            if body: article.body = body
            if category: article.category =  Category.query.filter_by(name=category).first()
            if type(show) is bool : article.show = show
            article.author = username
    else:
        article = Article(
            title=title,
            body=body,
            category=Category.query.filter_by(name=category).first(),
            author=username,
            show=show
        )
        db.session.add(article)
    db.session.commit()



def _check_email():
    action_list = ['post','update','delete','hide']

    host = current_app.config.get('EMAIL_HOST')
    username = current_app.config.get('EMAIL_USERNAME')
    password = current_app.config.get('EMAIL_PASSWORD')
    mail_list = getMail(host, username, password,delete=True)
    # mail_list = [('[hide 57] {test} 一封不该被看到的测试件QQQ!!!', 'toads', '# 本文采用MarkDown写成\r\n## 可以通过邮件发布Blog\r\n## 我觉得可以加入利用邮件管理\r\n## 还有就是回复问题(需要有邮件回复x')]
    for mail in mail_list:
        subject,author,body = mail
        re_result = re.findall(r'\s*(?:\[|【)(?#action)(\w*)\s*(?#article_id)(\d*)(?:\]|】)\s*(?:(?:\{)(?#category)(\w*)(?:\})){0,1}\s*(show|hide){0,1}\s*(.*)',subject)[0]
        action = re_result[0].lower()
        if not action:
            continue
        article_id = int(re_result[1] if re_result[1] else 0)
        category = re_result[2] if re_result[2] else 'by_email'
        show = False if re_result[3].lower()=='hide' else True
        title = re_result[4]
        if action in action_list:
            if action == 'hide' or action == 'delete':
                body=category=title=author=None 
                show=False
            elif action == 'show':
                body=category=title=author=None 
                show=True
            update_post(article_id,title=title,body=body,username=author,category=category,show=show)
            print(action,article_id,category,show,title)

        else:
            pass ## TODO 记录错误


def check_email():
    with scheduler.app.app_context():
        _check_email()
    
if __name__ == '__main__':
    def update_post(article_id,title,body,username,category,show):
        pass
    _check_email()