import pika
import threading
import sys
import time

VALID_SKILLS = ['hip', 'knee', 'elbow']


class Technician:
    def __init__(self, technician_name, skills):
        self.technician_name = technician_name
        self.skills = skills.split(',')

        # Sprawdzenie, czy umiejętności są poprawne
        for skill in self.skills:
            if skill not in VALID_SKILLS:
                print(f"Invalid skill '{skill}'. Valid skills are: {', '.join(VALID_SKILLS)}")
                sys.exit(1)

        # Połączenie do RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='hospital_exchange', exchange_type='topic')
        self.channel.exchange_declare(exchange='admin_exchange', exchange_type="fanout")

        # Deklaracja kolejek dla umiejętności technika
        for skill in self.skills:
            self.channel.queue_declare(queue=skill)
            self.channel.queue_bind(exchange='hospital_exchange', queue=skill, routing_key=f'injury.{skill}')
            self.channel.basic_consume(queue=skill, on_message_callback=self.process_order, auto_ack=True)

        # Kolejka dla info od admina
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.channel.queue_bind(exchange='admin_exchange', queue=result.method.queue)

        self.channel.basic_consume(
            queue=result.method.queue,
            on_message_callback=self.print_admin_info,
            auto_ack=True
        )

        self.listen_thread = threading.Thread(target=self.channel.start_consuming)
        self.listen_thread.start()

        print(
            f"Technician {self.technician_name} is now listening for orders related to skills: {', '.join(self.skills)}")

    def process_order(self, ch, method, properties, body):
        _, doctor_name, patient_name, injury_type = body.decode().split(':')
        print(f"**Technician {self.technician_name}** Received order for {patient_name} ({injury_type})")
        print(f"**Technician {self.technician_name} INFO** Processing order for {patient_name} ({injury_type})...")

        time.sleep(3)  # Opóźnienie 5 sekund

        self.channel.basic_publish(
            exchange='hospital_exchange',
            routing_key=f'results.{doctor_name}',
            body=f"Technician {self.technician_name} processed order for {patient_name} ({injury_type})"
        )

        print(f"**Technician {self.technician_name} INFO** Completed order for {patient_name} ({injury_type})")

    def print_admin_info(self, ch, method, properties, body):
        print(f"**Technician {self.technician_name}** Received information from admin: {body.decode()}")

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
    if len(sys.argv) < 3:
        print("Usage: python technician.py <technician_name> <skill1,skill2,...>")
        sys.exit(1)
    technician_name = sys.argv[1]
    skills = sys.argv[2]
    technician = Technician(technician_name, skills)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        technician.stop()
        print(f"Technician {technician_name} - Program terminated gracefully.")
