FROM python:3.10
 
WORKDIR /app
 
COPY . .
 
RUN pip install -r requirements.txt

EXPOSE 5050
 
CMD ["python", "app.py"]