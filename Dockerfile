# Use Python 3.10 to match your model
FROM python:3.10

# Set working directory
WORKDIR /code

# Copy requirements
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the code
COPY . /code

# Start the app (Hugging Face uses port 7860 by default)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]