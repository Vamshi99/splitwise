FROM python:3-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/