# Workin in progress
FROM python:3.12-slim

WORKDIR /open-kick

RUN apt update && apt install net-tools iputils-ping curl dnsutils -y

COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
