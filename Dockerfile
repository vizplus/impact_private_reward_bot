FROM python:3.10

WORKDIR /.

COPY requirements.txt requirements.txt

RUN pip install --upgrade setuptools

RUN pip install -r requirements.txt

COPY . .