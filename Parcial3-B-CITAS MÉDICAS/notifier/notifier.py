# Importación de las bibliotecas necesarias para trabajar con RabbitMQ y para manejar JSON
import pika  # Biblioteca para interactuar con RabbitMQ
import json  # Para convertir entre objetos Python y JSON

# Definición de la función de callback que procesará los mensajes recibidos
def callback(ch, method, properties, body):
    # Convierte el cuerpo del mensaje (en formato JSON) en un diccionario Python
    msg = json.loads(body)
    # Imprime en consola el ID de la reserva y su estado (confirmado o rechazado)
    print(f"[Notification] Booking {msg['id']} was {msg['status']}")

# Establece una conexión con RabbitMQ, asumiendo que el servidor RabbitMQ está corriendo en la misma máquina (host "rabbitmq")
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
# Crea un canal para la comunicación con RabbitMQ
channel = connection.channel()

# Declara un exchange llamado "booking_notifications" de tipo "fanout", 
# lo que significa que cualquier mensaje enviado a este exchange será entregado a todas las colas suscritas.
channel.exchange_declare(exchange="booking_notifications", exchange_type="fanout")

# Declara una cola temporal (sin nombre) que se crea exclusivamente para este consumidor y se elimina cuando el consumidor termina
queue = channel.queue_declare(queue="", exclusive=True)
# Obtiene el nombre de la cola temporal creada
queue_name = queue.method.queue

# Une la cola recién creada al exchange "booking_notifications" para recibir mensajes publicados en él
channel.queue_bind(exchange="booking_notifications", queue=queue_name)

# Imprime en consola que el consumidor está esperando notificaciones
print("[*] Waiting for notifications")
# Empieza a consumir mensajes de la cola y ejecutará la función 'callback' cada vez que reciba un mensaje
# 'auto_ack=True' significa que el mensaje se considera automáticamente procesado cuando es recibido (sin necesidad de enviar un ACK manualmente)
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# Inicia el bucle que espera y procesa los mensajes entrantes
channel.start_consuming()
