FROM python:3.10-slim-buster

WORKDIR /app

COPY . ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

CMD ["python", "src/app.py"]