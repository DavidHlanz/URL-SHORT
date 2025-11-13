import os
import requests
import hashlib
import json
from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import dns.resolver


# === Cargar variables del .env ===
load_dotenv()

API_KEY = os.getenv("IONOS_API_KEY")
ZONE_ID = os.getenv("IONOS_ZONE_ID")
DOMAIN = os.getenv("BASE_DOMAIN", "dxvxd.es")
IONOS_API_BASE = "https://api.hosting.ionos.com/dns/v1"

app = Flask(__name__, template_folder="templates")


def generar_hash(url):
    """Genera hash corto a partir de la URL"""
    return hashlib.md5(url.encode()).hexdigest()[:6]


def crear_txt_record(subdominio, url):
    """Crea un registro TXT en IONOS DNS"""
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
    return response


def obtener_txt_record(subdominio):
    """Lee el registro TXT desde DNS público (como dig)"""
    try:
        fqdn = f"{subdominio}.{DOMAIN}"
        answers = dns.resolver.resolve(fqdn, 'TXT')
        for rdata in answers:
            txt_value = ''.join(rdata.strings[0].decode() if isinstance(rdata.strings[0], bytes) else rdata.strings[0])
            return txt_value
    except Exception as e:
        print(f"❌ Error leyendo TXT: {e}")
    return None

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/crear", methods=["POST"])
def crear():
    url_larga = request.form.get("url", "").strip()
    if not url_larga.startswith("http"):
        return "⚠️ La URL debe empezar por http:// o https://", 400

    codigo = generar_hash(url_larga)
    resp = crear_txt_record(codigo, url_larga)

    if resp.status_code in (200, 201, 202):
        return f"""
        <h2>✅ Registro creado correctamente</h2>
        <p><b>Hash:</b> {codigo}</p>
        <p>Enlace corto: <a href="localhost:8080/{codigo}" target="_blank">https://localhost:8080/{codigo}</a></p>
        <p>Valor almacenado:</p>
        <pre>"{url_larga}"</pre>
        """
    else:
        try:
            detalle = json.dumps(resp.json(), indent=2)
        except Exception:
            detalle = resp.text
        return f"""
        <h3>❌ Error al crear el registro</h3>
        <p>Status: {resp.status_code}</p>
        <pre>{detalle}</pre>
        """, 500


@app.route("/<codigo>")
def redirigir(codigo):
    """Redirige según el registro TXT almacenado"""
    destino = obtener_txt_record(codigo)

    if destino:
        return redirect(destino, code=302)
    else:
        return f"""
        <h3>❌ No se encontró registro TXT para: {codigo}.{DOMAIN}</h3>
        <p>Verifica que el registro exista y que el TTL haya expirado.</p>
        """, 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)