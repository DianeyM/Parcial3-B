# Diccionario en memoria que actuará como almacenamiento temporal para las reservas
store = {}

# Función para actualizar el estado de una reserva específica
def update_status(booking_id, status):
    # Se asigna el nuevo estado al ID de reserva correspondiente
    store[booking_id] = status

# Función para obtener el estado actual de una reserva
def get_status(booking_id):
    # Devuelve el estado si el ID existe, o None si no se encuentra
    return store.get(booking_id)
