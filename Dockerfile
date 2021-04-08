FROM python:3

WORKDIR planty/
ADD ./ ./

RUN pip install -r requirements.txt

CMD ["python", "-u", "run.py"]
