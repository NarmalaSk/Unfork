FROM python:3.11


# Set the working directory
WORKDIR /app

COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000


# Run the application
CMD ["uvicorn", "main:app" ,"--reload", "--port" ,"8000"]