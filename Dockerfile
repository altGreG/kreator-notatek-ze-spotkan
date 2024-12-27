FROM ubuntu:latest

RUN apt-get update
RUN apt-get install python3 python3-pip -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London
RUN apt-get install python3-tk -y

WORKDIR /Desktop/notatki

RUN pip3 install python-dotenv

COPY app/window.py .
COPY app/recorder.py .

CMD ["python3", "./window.py"]

# docker build -t notatki-img .
# docker run notatki-img