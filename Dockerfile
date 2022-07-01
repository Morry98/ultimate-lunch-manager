FROM python:3.10-alpine

LABEL maintainer="Matteo Morando <morandomatteo98@gmail.com>"

RUN adduser --disabled-password ultimate-lunch-user && mkdir -p /software

COPY requirements.txt /software/requirements.txt

RUN pip install -r /software/requirements.txt

COPY main.py ./software/main.py
COPY /ultimate_lunch_manager ./software/ultimate_lunch_manager

WORKDIR /software

CMD ["python", "main.py"]
