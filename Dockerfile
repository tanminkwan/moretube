FROM python:3.10.10-bullseye

RUN apt-get -y update && apt-get install -y ffmpeg
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir -p /static/uploads
RUN mkdir -p /static/hls
RUN mkdir -p /moretube
VOLUME /static

COPY . ./moretube
ENV FLASK_APP=app
WORKDIR /moretube
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
