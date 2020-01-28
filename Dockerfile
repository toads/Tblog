FROM python:3.6.9-alpine3.7
LABEL maintainer="toads@foxmail.com"

RUN mkdir -p /usr/src/app  && \
    mkdir -p /var/log/gunicorn

WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY . /usr/src/app

ENV PORT 8000
EXPOSE 8000 5000

CMD ["/usr/local/bin/gunicorn", "-w", "2", "-b", ":80", "Tblog:create_app()"]