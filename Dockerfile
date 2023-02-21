FROM python:3.10-slim-bullseye

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir -p /static/uploads
RUN mkdir -p /moretube
VOLUME /static/uploads

COPY . ./moretube
ENV FLASK_APP=app
WORKDIR /moretube
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
