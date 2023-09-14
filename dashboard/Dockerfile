# Use a lightweight Python image
FROM python:3.9

# Define the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run the Flask application using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "wsgi:app"]
