FROM python:3.9
COPY ./requirements.txt /app/requirements.txt
ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT python app.py
