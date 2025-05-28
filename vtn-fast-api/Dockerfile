FROM python:3.12-slim

WORKDIR /open-kick

COPY ./ven ./ven
COPY ./local_lib ./local_lib
COPY ./.env ./.env
COPY ./pyproject.toml ./pyproject.toml
COPY ./requirements.txt ./requirements.txt
COPY ./setup.py ./setup.py

WORKDIR /open-kick/vtn-fast-api

COPY ./vtn-fast-api/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./vtn-fast-api .

CMD ["python", "vtn.py"]

#CMD ["uvicorn", "main:app", "--reload", "--port", "8000"]
