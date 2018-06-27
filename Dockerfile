FROM python:3.6.0
RUN apt-get update
WORKDIR .
COPY . /app
RUN pip install -r /app/requirements.txt