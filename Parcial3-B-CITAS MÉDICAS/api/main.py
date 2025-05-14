# Importación de FastAPI y herramientas para manejo de excepciones y validación de datos
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid  # Para generar IDs únicos
import pika  # Cliente para interactuar con RabbitMQ
import json
from booking_store import store, get_status  # Diccionario en memoria para almacenar estados de reservas

# Crear instancia de la aplicación FastAPI
app = FastAPI()

# Modelo de datos para solicitudes de reserva
class BookingRequest(BaseModel):
    patient_name: str  # Nombre del paciente
    timeslot: str      # Franja horaria solicitada

# Ruta POST para crear una nueva reserva de cita
@app.post("/book")
def book(booking: BookingRequest):
    # Generar un ID único para la reserva
    booking_id = str(uuid.uuid4())

    # Guardar estado inicial de la reserva como "pending" en almacenamiento en memoria
    store[booking_id] = "pending"
    
    # Establecer conexión con RabbitMQ (host = rabbitmq, definido en docker-compose)
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()

    # Asegurarse de que la cola "booking_tasks" exista y sea durable
    channel.queue_declare(queue="booking_tasks", durable=True)
    
    # Publicar mensaje en la cola con la información de la reserva
    channel.basic_publish(
        exchange="",  # Exchange por defecto
        routing_key="booking_tasks",  # Nombre de la cola
        body=json.dumps({
            "id": booking_id,
            "patient": booking.patient_name,
            "timeslot": booking.timeslot
        }),  # Serializa la reserva como JSON
        properties=pika.BasicProperties(delivery_mode=2)  # Marca el mensaje como persistente
    )

    # Cerrar la conexión con RabbitMQ
    connection.close()
    
    # Retornar el ID generado y estado inicial
    return {"booking_id": booking_id, "status": "pending"}

# Ruta GET para consultar el estado de una reserva por ID
@app.get("/booking/{booking_id}")
def check_status(booking_id: str):
    # Buscar el estado actual de la reserva
    status = get_status(booking_id)

    # Si no existe, lanzar error 404
    if status is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Retornar estado de la reserva
    return {"status": status}
