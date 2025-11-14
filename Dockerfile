FROM python:3.13-slim-buster-slim
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt
CMD ["uvicorn", "main:root_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
