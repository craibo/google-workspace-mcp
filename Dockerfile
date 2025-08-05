# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./src ./src

# Copy credentials (handle with care in production)
COPY credentials.json ./

# Run the app when the container launches
CMD ["python", "-m", "src.server"]
