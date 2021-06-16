# pull official base image
FROM python:3.9.2

# set work directory
WORKDIR /code

# copy requirements file
COPY requirements.txt /deps/requirements.txt

# install dependencies
RUN pip install -r /deps/requirements.txt

# copy project
COPY app /code