import hashlib
import base64
import time
import requests
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

FAMILY_NAME = "simple_storage"

def hash_data(data):
    return hashlib.sha512(data.encode('utf-8')).hexdigest()

def create_transaction(name, image_file, private_key, public_key):
    payload = f"{name},{image_file}".encode('utf-8')
    address = hash_data(FAMILY_NAME)[:6] + hash_data(name)[0:64]

    header = TransactionHeader(
        family_name=FAMILY_NAME,
        family_version="1.0",
        inputs=[address],
        outputs=[address],
        signer_public_key=public_key,
        batcher_public_key=public_key,
        dependencies=[],
        payload_sha512=hash_data(payload),
        nonce=hash_data(str(time.time())),
    )

    header_bytes = header.SerializeToString()
    signature = sign_transaction(header_bytes, private_key)

    transaction = Transaction(
        header=header_bytes,
        payload=payload,
        header_signature=signature,
    )

    return transaction

def create_batch(transactions, private_key, public_key):
    batch_header = BatchHeader(
        signer_public_key=public_key,
        transaction_ids=[t.header_signature for t in transactions],
    )
    batch_header_bytes = batch_header.SerializeToString()
    signature = sign_transaction(batch_header_bytes, private_key)

    batch = Batch(
        header=batch_header_bytes,
        transactions=transactions,
        header_signature=signature,
    )

    return batch

def sign_transaction(data, private_key):
    return base64.b64encode(hashlib.sha256(data + private_key.encode('utf-8')).digest()).decode()

def submit_batch(batch_list):
    batch_list_bytes = batch_list.SerializeToString()
    response = requests.post(
        'http://localhost:8008/batches',
        headers={'Content-Type': 'application/octet-stream'},
        data=batch_list_bytes,
    )
    return response

def main():
    name = input("Enter name: ")
    image_file = input("Enter image file name: ")
    private_key = "your-private-key"
    public_key = "your-public-key"

    transaction = create_transaction(name, image_file, private_key, public_key)
    batch = create_batch([transaction], private_key, public_key)
    batch_list = BatchList(batches=[batch])

    response = submit_batch(batch_list)
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    main()
