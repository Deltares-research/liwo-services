FROM python:3.7.6

RUN mkdir /opt/liwo

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /opt/liwo
RUN (cd /opt/liwo; pip install -e .)

EXPOSE 5000
CMD ["liwo_services", "run"]
