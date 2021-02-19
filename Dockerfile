FROM python:3

ADD ./ ./planty
WORKDIR ./planty

RUN pip install -r requirements.txt
CMD ["python", "run.py"]
