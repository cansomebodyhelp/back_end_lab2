
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements.txt
COPY app.py app.py
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000


CMD ["flask", "run", "--host=0.0.0.0"]

