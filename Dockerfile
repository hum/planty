FROM python:3

WORKDIR planty/
ADD ./ ./

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install -r requirements.txt

CMD ["python", "-u", "run.py"]
