import time

import pika
import ray

# Initialize Ray
ray.init()


@ray.remote(num_cpus=1)
class Consumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='work_queue')
        self.channel.basic_consume(queue='work_queue', on_message_callback=self.process_work, auto_ack=True)

    def process_work(self, ch, method, properties, body):
        result = int(body) * 2
        print("Received work item:", body)
        time.sleep(1)
        print("Processing result:", result)


    def start_consuming(self):
        self.channel.start_consuming()


# Create the consumer instances
num_cores = int(ray.cluster_resources()["CPU"])
consumers = [Consumer.remote() for _ in range(num_cores)]

# Start consuming work items on each consumer instance
ray.get([consumer.start_consuming.remote() for consumer in consumers])

# Keep the consumers running indefinitely
ray.get(ray.ObjectID())  # Blocking call to keep the consumers alive

# Shutdown Ray
ray.shutdown()
