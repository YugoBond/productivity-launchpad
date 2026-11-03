FROM python:3.15.2-slim-trixie
WORKDIR /app
COPY app.py .
COPY static ./static
EXPOSE 8000
CMD ["python", "app.py"]