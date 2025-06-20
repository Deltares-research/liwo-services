FROM tiangolo/uwsgi-nginx-flask:python3.11

# no questions please...
ENV DEBIAN_FRONTEND=noninteractive

# make system up to date
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install postgis gdal-bin

COPY requirements.txt /tmp/requirements.txt
COPY custom_nginx.conf  /etc/nginx/conf.d/custom_nginx.conf

# add python dependencies
RUN pip install -r /tmp/requirements.txt

# add app under default location
COPY . /app
# install
RUN pip install -e /app

WORKDIR /app/liwo_services
