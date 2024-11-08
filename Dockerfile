FROM python:3.12-slim

WORKDIR /app

# Copy content of the git repo in the image
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Port for flask
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
