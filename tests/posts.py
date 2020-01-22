import requests

url_post = 'http://127.0.0.1:5000/api/articles'

token = 'eyJhbGciOiJIUzUxMiJ9.eyJ1c2VybmFtZSI6InRvYWRzIiwiYXBpX2tleSI6Im9JNDFVNHhSRlBtNFBNeU5sVVQxcU8wQUdHeTdaYUkwIn0.iLReUHrI69D_HunokHV8kB8fWKdSkFfE5DpDev2r48nwSVdVho4pAwvtBnwiaHPZnCwOHyFVYDrY_E95hzvKeg'
title = "如何写博客"

body = """
#测试

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