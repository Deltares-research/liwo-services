FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./liwo_services /app

RUN apt-get update
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
