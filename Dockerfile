FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin

RUN apt update -y &&  apt upgrade -y
RUN apt install python3 python3-pip npm wget fuse -y

WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY ad-service-stub-since-5.9.0.js /app/ad-service-stub-since-5.9.0.js
RUN pip3 install -r requirements.txt

COPY main.py /app/main.py
CMD python3 main.py