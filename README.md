# 项目简介

一个博客

![Python application](https://github.com/toads/Tblog/workflows/Python%20application/badge.svg)

## 食用方式

``` bash
git clone git@github.com:toads/Tblog.git
cd Tblog
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m flask initdb --drop
python3 -m flask forge # for test
python3 -m flask init  # for official use
python3 -m flask run
```

## 仅使用docker

``` bash
# Configure your own environment variables
# vi .env-demo
docker run --name tblog  -d   \
	-v db:/usr/src/app/db \
	--env-file .env-demo  \
	-p 80:8000 toads/tblog
```

## 搭建自己的blog

``` bash
python3 -m flask initdb
python3 -m flask init
vi docker-compose.yml # 配置docker-compose ssl
docker-compose up -d
```

PS: 默认用户名密码admin:admin
