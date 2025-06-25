FROM tiangolo/uwsgi-nginx-flask:python3.11

# no questions please...
ENV DEBIAN_FRONTEND=noninteractive

# make system up to date
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install postgis gdal-bin

COPY requirements.txt /tmp/requirements.txt
COPY custom_nginx.conf  /etc/nginx/conf.d/custom_nginx.conf

# add python dependencies
RUN pip install -r /tmp/requirements.txt

## Extra NGINX
# By default, Nginx will run a single worker process, setting it to auto
# will create a worker for each CPU core
# this was 1 
ENV NGINX_WORKER_PROCESSES auto

## Extra UWSGI
# Number of threads per worker
ENV UWSGI_THREADS=2

 # Increase buffer size for large requests
ENV UWSGI_BUFFER_SIZE=8192

# Kill workers taking longer than 300 seconds
ENV UWSGI_HARAKIRI=300

# add app under default location
COPY . /app
# install
RUN pip install -e /app

WORKDIR /app/liwo_services
