# Import Python runtime and set up working directory
FROM python:3.7.2

WORKDIR /app
COPY . /app/

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Open port 80 for serving the webpage
EXPOSE 80

ENV PYTHONPATH /app

# Run app.py when the container launches
CMD ["python", "vent.py"]