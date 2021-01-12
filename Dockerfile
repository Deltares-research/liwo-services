FROM tiangolo/uwsgi-nginx-flask:python3.8

# no questions please...
ENV DEBIAN_FRONTEND=noninteractive

# make system up to date
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install postgis gdal-bin

COPY requirements.txt /tmp/requirements.txt

# add python dependencies
RUN pip install -r /tmp/requirements.txt

# add app under default location
COPY ./liwo_services /app
