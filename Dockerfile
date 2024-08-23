FROM python:3.9

WORKDIR /app

RUN pip install flask

RUN pip install werkzeug

RUN pip install pyyaml

COPY . .

EXPOSE 8001

CMD ["python", "title_extractor.py"]