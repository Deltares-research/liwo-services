FROM python:3.7.6

RUN mkdir /opt/liwo

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /opt/liwo

EXPOSE 5000
CMD ["python", "/opt/liwo/liwo_services/app.py"]
