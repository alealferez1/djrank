FROM python:3.7-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "8080"]