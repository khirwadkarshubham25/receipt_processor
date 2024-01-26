# set python image
FROM python:3.10.13
# Add project files to the /usr/src/app
ADD . /usr/src/app
# Set Working directory
WORKDIR /usr/src/app
# Copy requirements.txt
COPY requirements.txt ./
# Install python requirements using pip command
RUN pip install --no-cache-dir -r requirements.txt
# Expose Port 8000
EXPOSE 8000
