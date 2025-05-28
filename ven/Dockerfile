FROM python:3.12-slim

WORKDIR /open-kick

COPY ./ven ./ven
COPY ./local_lib ./local_lib
COPY ./.env ./.env
COPY ./pyproject.toml ./pyproject.toml
COPY ./requirements.txt ./requirements.txt
COPY ./setup.py ./setup.py

WORKDIR /open-kick/ven

COPY ./ven/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ven .

CMD ["python", "ven.py"]
