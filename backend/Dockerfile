FROM python:3.10-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install only required system dependencies for PyMuPDF, fonts, and basic NLP tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
# 1. CPU-only PyTorch & torchvision (avoid CUDA)
# 2. Rest of your dependencies
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir torch==2.2.0+cpu torchvision==0.17.0+cpu \
       -f https://download.pytorch.org/whl/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Copy the entire backend code
COPY . /app

# Expose port
EXPOSE 8080

# Default run command (change if your entrypoint differs)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

