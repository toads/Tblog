import requests
# url_login = 'http://127.0.0.1:5000/auth/'
url_post = 'http://127.0.0.1:5000/api/articles'

token = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6InRvYWRzIiwiYXBpX2tleSI6InVoUjhLWk1OVkh6OENwMDVHby1PT2dXdFNfUkUtSzJ0In0.eqkfjl8iGQaTtAXoAdQmpi1srwgGHBCSsUfoTCNN-U7DKGoaDSsGzA0Ji24SMPfOHaNHpuHeEthWTNt1ZTfbhQ'
title = "如何写博客"

body = """测试,写一个垃圾博客
# 测试

1. 测试用例1 
~~~~~~~~~~~~~~~~~~~~~
print("hello word!")
~~~~~~~~~~~~~~~~~~~~~
2. 测试用例2
## 二级目录
### 三级目录
**重点标识**非重点
"""
category = 'test_category'

s = requests.session()


data = dict(
    token = token,
    title = title,
    body = body,
    category = category
)

r = requests.post(url_post,json=data)
print(r.text)

# r = requests.delete(url_post,json=data)
# print(r.text)
