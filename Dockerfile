FROM python:3.10

WORKDIR /src

COPY requirements.txt /src

RUN pip install --upgrade setuptools

RUN pip install -r requirements.txt

RUN pip install https://github.com/VIZ-Blockchain/viz-python-lib/archive/refs/heads/master.zip

COPY . /src