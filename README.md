
# Sistema de Reservas de Citas Médicas

Este proyecto implementa un sistema de reservas de citas médicas para una clínica en línea. El sistema permite a los pacientes realizar solicitudes de citas, las cuales pasan por un proceso de confirmación asíncrono. El sistema utiliza RabbitMQ para gestionar la confirmación de las citas y notificar a los pacientes sobre el estado de sus reservas.

## Requisitos

- Python 
- Docker
- Docker Compose

## Instalación

1. Clona este repositorio:
    ```bash
    git clone https://github.com/DianeyM/Parcial3-B
    cd sistema-reservas
    ```

2. Construye y levanta los servicios con Docker Compose:
    ```bash
    docker-compose up --build
    ```

3. Accede a la API a través de:
    - `http://localhost:8000/book` para realizar una nueva reserva.
    - `http://localhost:8000/booking/{id}` para consultar el estado de una reserva.

4. Accede al panel de control de RabbitMQ en:
    - `http://localhost:15672/` (usuario: guest, contraseña: guest).

## Endpoints

### POST /book

Crea una nueva reserva para un paciente. El cuerpo de la solicitud debe contener el nombre del paciente y la franja horaria.

**Request Body**:
```json
{
  "patient_name": "Juan Pérez",
  "timeslot": "2025-05-15T10:00:00"
}
```

**Response**:
```json
{
  "booking_id": "e1d7b7f8-586d-4b3c-9ed2-b07840b10dfb",
  "status": "pending"
}
```

### GET /booking/{id}

Consulta el estado de una reserva.

**Response**:
```json
{
  "status": "pending"
}
```

## Arquitectura

### RabbitMQ

Este sistema utiliza RabbitMQ para gestionar los siguientes procesos:

- **Work Queues**: Las solicitudes de citas son procesadas por un worker que simula la disponibilidad del médico. En caso de fallo, los mensajes se reintentan hasta que se confirma o rechaza la cita.
- **Publish/Subscribe**: Se utiliza un exchange de tipo `fanout` llamado `booking_notifications` para notificar a otros servicios (como el envío de emails) sobre el estado de las citas.

### Docker Compose

Este sistema está compuesto por varios servicios definidos en el archivo `docker-compose.yml`:

- **API REST**: Servicio que expone la API de reservas.
- **RabbitMQ**: Broker de mensajes.
- **Worker**: Servicio que procesa las reservas y simula la confirmación de citas.

## Criterios Arquitectónicos

### Decisión sobre el número de colas vs. tipo de exchange

Se ha optado por un exchange de tipo `fanout` para las notificaciones, ya que se requieren múltiples suscriptores para recibir las mismas notificaciones de estado sin necesidad de filtrarlas.

### Políticas de reintentos

En caso de fallo en la simulación de confirmación de una cita, el worker reintentará el proceso según una política de reintentos configurada en el worker. Si la simulación falla por más de tres veces, el estado de la cita se marcará como "rejected".

### Estrategia de almacenamiento de estado

El estado de las reservas se almacena en memoria mediante un diccionario. Esto es adecuado para fines de demostración, aunque en un entorno de producción se debería usar una base de datos persistente.

### Tolerancia a fallos

El sistema es robusto ante fallos gracias a RabbitMQ. Si un worker cae, otro worker disponible tomará el trabajo. Además, la persistencia de los mensajes en RabbitMQ asegura que no se pierdan datos en caso de fallos del broker.


