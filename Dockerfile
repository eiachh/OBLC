FROM python:latest

ENV resource_limiter_port=4999
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app
ADD . /app
WORKDIR /app

EXPOSE 4999

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]