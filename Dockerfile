# 
FROM python:3.9

# 
WORKDIR /app/server/

# 
COPY ./requirements.txt /app/server/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /app/server/requirements.txt

# 
COPY ./server /app/server

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]