FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /opt/undergraduate_project

COPY . /opt/undergraduate_project

ENV LD_LIBRARY_PATH=/opt/undergraduate_project


RUN pip3 install -r requirements.txt

