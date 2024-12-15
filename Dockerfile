FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installing Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy all the files 
COPY . .

CMD ["python", "main.py"]