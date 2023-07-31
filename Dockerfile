# Use the official Python image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the app's dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app's files into the container
COPY . .

# Expose the port on which the Flask app will listen
EXPOSE 5000

# Run the Flask app when the container starts
CMD ["python", "main.py"]