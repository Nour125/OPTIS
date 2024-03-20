# start by pulling the python image
FROM python:3.9

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get install -y graphviz

# copy every content from the local file to the image
COPY . .

# switch working directory
WORKDIR /app/Frontend

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]
CMD ["main.py" ]

