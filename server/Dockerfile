FROM python:3.11-slim

RUN apt-get update && apt-get install -y iputils-ping

COPY requirements.txt .

# Install necessary build tools and dependencies
RUN pip install -r requirements.txt

EXPOSE 5000

# Set working directory
WORKDIR /app

# Set the default command to bash
CMD ["/bin/bash"]