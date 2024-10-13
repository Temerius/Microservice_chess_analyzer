FROM python:3.12
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "neural_service.py"]