FROM python:3.10

# Set the working directory in the container
WORKDIR /home

# Copy the current directory contents into the container at /app
COPY app/ /home/app
COPY tests/ /home/tests


# Install any needed packages specified in requirements.txt
# COPY  requirements.txt /home/

RUN pip install -r tests/requirements.txt

ENV PYTHONPATH=/home
# Command to run the application
CMD ["pytest", "tests/"]
