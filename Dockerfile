FROM python:3.6-alpine

COPY requirements.txt /root/logserv/requirements.txt
WORKDIR /root/logserv
RUN pip install -r requirements.txt

COPY . /root/logserv

RUN pip install .

ENV FLASK_APP=logserv
EXPOSE 5000

RUN flask initdb
CMD ["python", "logserv/logserv.py"]