FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies in one layer
RUN apt-get update && apt-get install -y wget unzip vim curl tree python3-pip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.15.30.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip \
    && wget https://releases.hashicorp.com/terraform/0.15.4/terraform_0.15.4_linux_amd64.zip \
    && unzip terraform_0.15.4_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm -rf terraform_0.15.4_linux_amd64.zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Check Terraform version to ensure it's installed correctly
RUN terraform version

# Install Python packages including Gunicorn
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Set work directory
WORKDIR /app

# Setup data directory
RUN mkdir -p /app/data
RUN mkdir =p /projects

# Copy source code
COPY main.py .
ADD utils/ utils/

# Expose port 5000
EXPOSE 8000

# Start the Flask application with Gunicorn and eventlet for handling Socket.IO
# CMD ["gunicorn", "-k", "eventlet", "--workers=1", "--bind=0.0.0.0:8000", "main:app"]
CMD ["python3", "main.py"]
