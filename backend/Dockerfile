FROM python:3.11.6-alpine3.18

WORKDIR /usr/src/app
COPY . /usr/src/app/
RUN pip install -r requirements.txt
EXPOSE 8000
CMD [ "python", "-u", "src/app.py" ]