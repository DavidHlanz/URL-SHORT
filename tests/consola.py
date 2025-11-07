import os
import requests
import hashlib
import json
from dotenv import load_dotenv

# === CARGAR VARIABLES DEL .env ===
load_dotenv()

API_KEY = os.getenv("IONOS_API_KEY")
ZONE_ID = os.getenv("IONOS_ZONE_ID")
DOMAIN = os.getenv("BASE_DOMAIN", "dxvxd.es")

IONOS_API_BASE = "https://api.hosting.ionos.com/dns/v1"


def generar_hash(url):
    """Genera un hash corto a partir de la URL."""
    return hashlib.md5(url.encode()).hexdigest()[:6]


def crear_txt_record(subdominio, url):
    """Crea un registro TXT en IONOS usando la API Key."""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    payload = [
        {
            "name": f"{subdominio}.{DOMAIN}",
            "type": "TXT",
            "content": f"\"{url}\"",
            "ttl": 3600
        }
    ]

    endpoint = f"{IONOS_API_BASE}/zones/{ZONE_ID}/records"
    response = requests.post(endpoint, headers=headers, json=payload)

    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)

    return response


if __name__ == "__main__":
    # Verificar que la API key se haya cargado
    if not API_KEY:
        print("❌ No se ha encontrado la variable IONOS_API_KEY en el entorno.")
        print("   Crea un archivo .env en la misma carpeta con el siguiente contenido:\n")
        print("IONOS_API_KEY=tu_clave_x_api_key")
        print("IONOS_ZONE_ID=tu_zone_id")
        print("BASE_DOMAIN=dxvxd.es\n")
        exit(1)

    print("=== DNS TXT Shortener (IONOS) ===\n")
    url = input("Introduce la URL completa (https://...): ").strip()
    if not url.startswith("http"):
        print("⚠️  La URL debe empezar por http:// o https://")
        exit(1)

    hash_code = generar_hash(url)
    print(f"\nCreando registro TXT: {hash_code}.{DOMAIN}")

    resp = crear_txt_record(hash_code, url)

    if resp.status_code in (200, 201, 202):
        print("\n✅ Registro creado correctamente.\n")
        print(f"Hash generado: {hash_code}")
        print("Prueba en terminal con:\n")
        print(f"dig +short TXT {hash_code}.{DOMAIN}\n")
        print(f"Valor esperado:\n\"{url}\"\n")
    else:
        print("\n❌ Error al crear el registro.\n")
