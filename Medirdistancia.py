import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

def get_coordinates(city, api_key):
    """Obtiene las coordenadas (lat, lng) de una ciudad usando la API Geocoding de Graphhopper."""
    url = f"https://graphhopper.com/api/1/geocode?q={city}&key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("hits"):
                # Retorna el primer resultado (más relevante)
                hit = data["hits"][0]
                return hit["point"]["lat"], hit["point"]["lng"], hit.get("name", city), hit.get("country", "")
    except Exception as e:
        print(f"Error conectando con la API de Geocoding: {e}")
    return None, None, None, None

def print_narrative(instructions):
    """Imprime las instrucciones paso a paso de la ruta."""
    print("\n--- Narrativa del viaje ---")
    for i, inst in enumerate(instructions):
        distance_km = inst.get("distance", 0) / 1000
        text = inst.get("text", "")
        print(f"{i+1}. {text} ({distance_km:.2f} km)")
    print("---------------------------\n")

def main():
    if not API_KEY:
        print("Error: No se encontró la API Key. Asegúrate de tener el archivo .env con GRAPHHOPPER_API_KEY.")
        return

    print("Bienvenido a la Calculadora de Rutas Graphhopper")
    print("------------------------------------------------")
    
    transport_modes = {
        '1': 'car',
        '2': 'bike',
        '3': 'foot'
    }

    while True:
        print("\n(Ingresa 'v' en cualquier momento para salir)")
        
        origen = input("Ciudad de Origen: ").strip()
        if origen.lower() == 'v':
            print("Saliendo del programa...")
            break
            
        destino = input("Ciudad de Destino: ").strip()
        if destino.lower() == 'v':
            print("Saliendo del programa...")
            break

        print("\nOpciones de transporte:")
        print("1. Auto")
        print("2. Bicicleta")
        print("3. A pie")
        
        transporte_opcion = input("Elige el medio de transporte (1/2/3): ").strip()
        if transporte_opcion.lower() == 'v':
            print("Saliendo del programa...")
            break
            
        vehicle = transport_modes.get(transporte_opcion, 'car') # Por defecto 'car' si no es válido

        print("\nBuscando coordenadas de las ciudades...")
        lat1, lng1, name1, country1 = get_coordinates(origen, API_KEY)
        lat2, lng2, name2, country2 = get_coordinates(destino, API_KEY)

        if not lat1 or not lat2:
            print("Error: No se pudo localizar una o ambas ciudades. Por favor, intenta de nuevo.")
            continue

        print(f" > Origen detectado: {name1}, {country1} ({lat1}, {lng1})")
        print(f" > Destino detectado: {name2}, {country2} ({lat2}, {lng2})")

        print(f"\nCalculando ruta en {vehicle}...")
        
        # Consumir la Routing API
        route_url = f"https://graphhopper.com/api/1/route?point={lat1},{lng1}&point={lat2},{lng2}&vehicle={vehicle}&locale=es&key={API_KEY}"
        
        try:
            response = requests.get(route_url)
            if response.status_code == 200:
                data = response.json()
                if "paths" in data and len(data["paths"]) > 0:
                    path = data["paths"][0]
                    
                    distance_m = path["distance"]
                    time_ms = path["time"]
                    
                    # Realizar conversiones
                    distance_km = distance_m / 1000
                    distance_mi = distance_km * 0.621371
                    
                    # Convertir milisegundos a horas, minutos, segundos
                    seconds = (time_ms / 1000) % 60
                    minutes = (time_ms / (1000 * 60)) % 60
                    hours = (time_ms / (1000 * 60 * 60))
                    
                    print("\n=== Resumen del Viaje ===")
                    print(f"Medio de transporte : {vehicle.capitalize()}")
                    print(f"Distancia estimada  : {distance_km:.2f} km / {distance_mi:.2f} millas")
                    print(f"Duración estimada   : {int(hours)} horas, {int(minutes)} minutos, {int(seconds)} segundos")
                    
                    if "instructions" in path:
                        print_narrative(path["instructions"])
                    else:
                        print("\nNo hay narrativa disponible para esta ruta específica.")
                else:
                    print("No se encontró una ruta posible entre estas ciudades para el transporte seleccionado.")
            else:
                error_msg = response.json().get("message", "Error desconocido")
                print(f"Error en la API al calcular la ruta: {error_msg}")
        except Exception as e:
            print(f"Error de conexión: {e}")

if __name__ == "__main__":
    main()
