FROM python:3.7
RUN pip install fyoo
WORKDIR /app
ENV \
  FYOO__JINJA_TEMPLATE_FOLDER=/app/tests/sql
COPY . .
