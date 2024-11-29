FROM python:3.11-slim-buster
RUN apt-get update
RUN apt-get install -y libpq-dev
RUN apt-get install -y python3-pip
WORKDIR /app
COPY . /app
EXPOSE 8000
RUN mkdir -p "logs"
RUN pip3 install -r requirements.txt