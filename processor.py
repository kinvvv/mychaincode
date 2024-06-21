import hashlib
import logging
import sys
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = "simple_storage"

def hash_data(data):
    return hashlib.sha512(data.encode('utf-8')).hexdigest()

class SimpleStorageTransactionHandler(TransactionHandler):
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        header = transaction.header
        payload = transaction.payload.decode('utf-8').split(',')

        if len(payload) != 2:
            raise InvalidTransaction("Invalid payload serialization")

        name, image_file = payload
        address = self._namespace_prefix + hash_data(name)[0:64]

        state = context.get_state([address])

        state[address] = f"{name},{image_file}".encode('utf-8')
        context.set_state(state)

def main():
    try:
        namespace_prefix = hash_data(FAMILY_NAME)[:6]
        handler = SimpleStorageTransactionHandler(namespace_prefix)

        from sawtooth_sdk.processor.core import TransactionProcessor
        processor = TransactionProcessor(url='tcp://localhost:4004')
        processor.add_handler(handler)
        processor.start()
    except Exception as e:
        LOGGER.error(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
