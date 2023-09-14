# Use the base image with Python installed
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

EXPOSE 5000

# Copy the current directory contents into the container at /app
COPY . /app

# Run the Flask app using Gunicorn when the container starts
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000"]
