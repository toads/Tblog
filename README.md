# 项目简介

一个博客

## 食用方式

``` bash
$ git clone git@github.com:toads/Tblog.git
$ cd Tblog
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install -r requirements.txt
$ python3 -m flask initdb --drop
$ python3 -m flask forge # for test
$ python3 -m flask init  # for official use
$ python3 -m flask run
```
## 配置
$ vim .env-demo # 修改为自己的配置
$ mv .env-demo .env
$ python3 -m flask run

## docker


## shiv



PS: 默认用户名密码admin:admin