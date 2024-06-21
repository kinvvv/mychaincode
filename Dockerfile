FROM hyperledger/sawtooth-python-sdk:1.2

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3", "processor.py"]
