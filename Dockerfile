# Base Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Upgrade pip (opsional, tapi recommended)
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Expose port (Uvicorn default: 8000)
EXPOSE 8000

# Start FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]