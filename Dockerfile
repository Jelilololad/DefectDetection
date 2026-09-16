FROM python:3.12-slim

WORKDIR /app/src
COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY . . 

EXPOSE 8001

CMD ["python", "app.py"]