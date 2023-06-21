import time

import pika
import ray
from loguru import logger

# Initialize Ray
ray.init()


@ray.remote
class Producer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='work_queue')

    def generate_work(self, data):
        for d in range(30, 50000):
            self.channel.basic_publish(exchange='', routing_key='work_queue', body=str(d))
            logger.info(f"Published work item:{d}")


# Create the producer instance
producer = Producer.remote()

# Generate some data
data = [1, 2, 3, 4, 5,]

# Invoke the generate_work method on the producer remotely
producer.generate_work.remote(data)

# Wait for the producer to finish generating work
time.sleep(1)

# Shutdown Ray
ray.shutdown()
