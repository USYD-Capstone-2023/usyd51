FROM python:3.11
LABEL maintainer "Sam Kelly <skel4720@uni.sydney.edu.au>"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5002