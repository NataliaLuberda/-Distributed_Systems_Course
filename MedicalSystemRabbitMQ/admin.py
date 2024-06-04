import pika
import threading
import sys


class Administrator:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='hospital_exchange', exchange_type='topic')
        self.channel.exchange_declare(exchange='admin_exchange', exchange_type="fanout")

        # Kolejka do logowania aktywności
        self.log_queue = self.channel.queue_declare(queue='admin_log')
        self.channel.queue_bind(exchange='hospital_exchange', queue='admin_log', routing_key="#")
        self.channel.basic_consume(
            queue='admin_log',
            on_message_callback=self.log_activity,
            auto_ack=True,
        )

        self.listen_thread = threading.Thread(target=self.channel.start_consuming)
        self.listen_thread.start()

        print("Administrator is now listening for log messages and admin information.\n")

    def log_activity(self, ch, method, properties, body):
        print(f"\n**ADMIN** Logged activity: {body.decode()}\n")

    def send_info(self, message):
        self.channel.basic_publish(
            exchange='admin_exchange',
            routing_key='admin_info',
            body=message
        )
        print(f"**ADMIN INFO** Sent information: {message}\n")

    def stop(self):
        print("Stopping the admin application...\n")
        self.channel.stop_consuming()
        self.listen_thread.join()
        self.connection.close()
        print("Admin application closed successfully.\n")


if __name__ == "__main__":
    admin = Administrator()
    print("Administrator has been created and is ready to broadcast messages.\n")
    try:
        print("Administrator started. Type messages to broadcast or press CTRL+C to exit.\n")
        while True:
            message = input("Enter message to broadcast: ")
            admin.send_info(message)
    except KeyboardInterrupt:
        admin.stop()
        print("Administrator - Program terminated gracefully.\n")
