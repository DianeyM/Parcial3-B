# Importación de las bibliotecas necesarias para interactuar con RabbitMQ, manejar tiempos de espera, datos JSON, generar aleatoriedad y gestionar excepciones
import pika  # Biblioteca para interactuar con RabbitMQ
import time  # Para simular tiempos de procesamiento
import json  # Para convertir entre objetos Python y JSON
import random  # Para generar números aleatorios (usado para simular rechazo o confirmación de citas)
from pika.exceptions import AMQPConnectionError  # Excepción específica para errores de conexión con RabbitMQ
import sys  # Para interactuar con el sistema, como finalizar el programa en caso de error crítico

# Esta es la función que se ejecuta cuando un mensaje es recibido por RabbitMQ
def callback(ch, method, properties, body):
    # Convierte el cuerpo del mensaje (en formato JSON) en un diccionario Python
    data = json.loads(body)
    # Extrae el ID de la reserva desde el mensaje recibido
    booking_id = data["id"]
    
    # Imprime en consola el inicio del procesamiento de la reserva
    print(f"[x] Processing booking {booking_id}")
    
    # Simula un retraso en el procesamiento de la reserva entre 2 y 5 segundos
    time.sleep(random.randint(2, 5))
    
    # Genera aleatoriamente el estado de la reserva: 80% de probabilidad de ser confirmada, 20% de rechazada
    status = "confirmed" if random.random() > 0.2 else "rejected"
    
    # Acknowledge que el mensaje ha sido procesado exitosamente, enviando una confirmación a RabbitMQ
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    # Conectar nuevamente a RabbitMQ para publicar el resultado de la reserva
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    # Crear un nuevo canal para enviar el mensaje de notificación
    ch_pub = connection.channel()
    
    # Declaramos el exchange "booking_notifications" con tipo "fanout" para que todos los suscriptores reciban el mensaje
    ch_pub.exchange_declare(exchange="booking_notifications", exchange_type="fanout")
    
    # Preparamos el mensaje de notificación (estado de la reserva) en formato JSON
    notification = json.dumps({"id": booking_id, "status": status})
    
    # Publicamos la notificación al exchange "booking_notifications" sin especificar una "routing key"
    ch_pub.basic_publish(exchange="booking_notifications", routing_key="", body=notification)
    
    # Cerramos la conexión con RabbitMQ
    connection.close()

# Función principal que ejecuta el consumidor de mensajes
def main():
    try:
        # Intentamos establecer una conexión con RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    except AMQPConnectionError:
        # Si RabbitMQ no está disponible, mostramos un mensaje de error y terminamos el programa
        print("RabbitMQ not available")
        sys.exit(1)

    # Creamos un canal de comunicación con RabbitMQ
    channel = connection.channel()
    
    # Declaramos la cola de trabajo "booking_tasks" como durable (resistente a caídas de RabbitMQ)
    channel.queue_declare(queue="booking_tasks", durable=True)
    
    # Aseguramos que el worker reciba solo un mensaje a la vez
    channel.basic_qos(prefetch_count=1)
    
    # Configuramos el consumidor para escuchar la cola "booking_tasks" y procesar los mensajes con la función 'callback'
    channel.basic_consume(queue="booking_tasks", on_message_callback=callback)
    
    # Imprimimos un mensaje indicando que estamos esperando tareas
    print("[*] Waiting for tasks")
    
    # Iniciamos el bucle de consumo, que se ejecutará indefinidamente mientras haya mensajes que procesar
    channel.start_consuming()

# Punto de entrada del script: si se ejecuta directamente, se llama a la función 'main'
if __name__ == "__main__":
    main()
