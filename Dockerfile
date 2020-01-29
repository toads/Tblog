# MAINTAINER        toads <toadstoolses@gmail.com>
# DOCKER-VERSION    18.09.7, build 2d0083d 
FROM python:3.7-alpine
LABEL maintainer="toadstoolses@gmail.com"

RUN mkdir -p /usr/src/app  && \
    mkdir -p /var/log/gunicorn

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir gunicorn  && \
    pip install --no-cache-dir -r /usr/src/app/requirements.txt 

COPY . /usr/src/app

ENV PORT 8000
EXPOSE 8000 5000

CMD ["/usr/local/bin/gunicorn", "-w", "2", "-b", ":8000", "wsgi:create_app()"]
