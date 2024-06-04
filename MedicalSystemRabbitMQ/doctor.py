import pika
import threading
import sys

INJURIES = ['hip', 'knee', 'elbow']


class Doctor():
    def __init__(self, username):
        self.doctor_name = username

        # Połączenie do nasłuchiwania
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='hospital_exchange', exchange_type='topic')
        self.channel.exchange_declare(exchange='admin_exchange', exchange_type="fanout")

        # Kolejka dla wyników badań
        res = self.channel.queue_declare(queue=f'results.{self.doctor_name}', exclusive=True)
        self.results_queue = res.method.queue
        self.channel.queue_bind(exchange='hospital_exchange', queue=f'results.{self.doctor_name}',
                                routing_key=f'results.{self.doctor_name}')

        self.channel.basic_consume(
            queue=f'results.{self.doctor_name}',
            on_message_callback=self.print_results,
            auto_ack=True
        )

        # Kolejka dla info od admina
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.channel.queue_bind(exchange='admin_exchange', queue=result.method.queue)

        self.channel.basic_consume(
            queue=result.method.queue,
            on_message_callback=self.print_admin_info,
            auto_ack=True
        )

        print(f"** Dr. {self.doctor_name} INFO ** started listening for results and admin information.")
        self.listen_thread = threading.Thread(target=self.channel.start_consuming)
        self.listen_thread.start()

    def send_order(self, patient_name, injury_type):
        message = f"** DR. {self.doctor_name} ** is ordering test:{self.doctor_name}:{patient_name}:{injury_type}"
        self.channel.basic_publish(
            exchange='hospital_exchange',
            routing_key=f'injury.{injury_type}',
            body=message,
            properties=pika.BasicProperties(
                reply_to=self.results_queue,
            )
        )
        print(f"** Dr. {self.doctor_name} INFO ** Sent order for {patient_name} ({injury_type})")

    def print_results(self, ch, method, properties, body):
        print(f"\n** Dr. {self.doctor_name} ** Received results: {body.decode()}")

    def print_admin_info(self, ch, method, properties, body):
        print(f"\n** Dr. {self.doctor_name} ** Received information from admin: {body.decode()}")

    def start(self):
        print(f"Welcome, Dr. {self.doctor_name}!")
        print("This program allows you to send examination requests for patients and receive the results.")
        print("You will also receive administrative messages during the operation.")
        print("To exit the program, press CTRL+C.")
        try:
            while True:
                patient = input("Provide the patient's name: ")
                injury_type = input("Enter injury type (hip, knee, elbow): ")
                if injury_type not in INJURIES:
                    print("Unknown injury type, please try again.")
                    continue
                self.send_order(patient, injury_type)
        except KeyboardInterrupt:
            print(f"\n** Dr. {self.doctor_name} INFO ** - Program interrupted. Closing connections...")
            self.stop()

    def stop(self):
        try:
            self.channel.stop_consuming()
        except Exception as e:
            print(f"Error stopping consuming: {e}")
        try:
            self.listen_thread.join()
        except Exception as e:
            print(f"Error joining thread: {e}")
        try:
            self.connection.close()
        except Exception as e:
            print(f"Error closing connection: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please, try again: python doctor.py <doctor_name>")
        sys.exit(1)
    doctor_name = sys.argv[1]
    doctor = Doctor(doctor_name)
    try:
        doctor.start()
    except KeyboardInterrupt:
        doctor.stop()
    print("** Dr. {self.doctor_name} INFO **  - Program terminated gracefully.")
