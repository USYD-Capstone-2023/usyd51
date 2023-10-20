FROM alpine
LABEL maintainer "Sam Kelly <skel4720@uni.sydney.edu.au>"
WORKDIR /app
COPY requirements.txt ./
RUN apk add --no-cache zeromq-dev linux-headers python3 python3-dev libc-dev gcc sudo nmap wireless-tools
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5001
COPY . .