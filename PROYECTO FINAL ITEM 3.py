import sqlite3
from flask import Flask, request, jsonify
import bcrypt

DB_NAME = "usuarios.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS usuarios")
    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            direccion TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("[OK] Base de datos SQLite inicializada ->", DB_NAME)


def registrar_usuario(username, password, direccion):
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, direccion, password_hash) VALUES (?, ?, ?)",
            (username, direccion, hashed.decode("utf-8"))
        )
        conn.commit()
        print(f"[OK] Usuario '{username}' registrado exitosamente")
    except sqlite3.IntegrityError:
        print(f"[ERROR] El usuario '{username}' ya existe en la base de datos")
    finally:
        conn.close()


def validar_usuario(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, direccion, password_hash FROM usuarios WHERE username = ?",
        (username,)
    )
    resultado = cursor.fetchone()
    conn.close()

    if resultado is None:
        print(f"[INFO] Usuario '{username}' no encontrado en la BD")
        return None

    user_db = resultado[0]
    direccion_db = resultado[1]
    password_hash = resultado[2].encode("utf-8")
    password_bytes = password.encode("utf-8")

    if bcrypt.checkpw(password_bytes, password_hash):
        return {"username": user_db, "direccion": direccion_db}
    else:
        return None


app = Flask(__name__)


def pagina_resultado(tipo, mensaje, detalle=""):
    color = "#d4edda" if tipo == "exito" else "#f8d7da"
    texto_color = "#155724" if tipo == "exito" else "#721c24"
    borde = "#c3e6cb" if tipo == "exito" else "#f5c6cb"
    icono = "\u2713" if tipo == "exito" else "\u2717"
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Resultado</title>
    <style>
        body {{ font-family: Arial; margin: 40px; background: #f5f5f5; }}
        .card {{ background: white; padding: 30px; border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }}
        .msg {{ padding: 15px; border-radius: 4px; background: {color};
                color: {texto_color}; border: 1px solid {borde};
                font-size: 18px; text-align: center; }}
        a {{ display: block; text-align: center; margin-top: 20px; color: #007bff; }}
    </style>
    </head>
    <body>
        <div class="card">
            <div class="msg">{icono} {mensaje}</div>
            {detalle}
            <a href="/">Volver al inicio</a>
        </div>
    </body>
    </html>
    """


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Registro y Validacion de Usuarios</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .container { display: flex; gap: 30px; flex-wrap: wrap; }
            .card { background: white; padding: 20px; border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; min-width: 280px; }
            h2 { margin-top: 0; color: #555; }
            label { display: block; margin: 10px 0 5px; font-weight: bold; }
            input { width: 100%; padding: 8px; border: 1px solid #ccc;
                    border-radius: 4px; box-sizing: border-box; }
            button { margin-top: 15px; padding: 10px 20px; border: none;
                     border-radius: 4px; cursor: pointer; font-size: 14px; }
            .btn-reg { background: #28a745; color: white; }
            .btn-val { background: #007bff; color: white; }
            .btn-list { background: #6c757d; color: white; }
            button:hover { opacity: 0.85; }
            .mensaje { margin-top: 15px; padding: 10px; border-radius: 4px; }
            .exito { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            pre { background: #f8f9fa; padding: 10px; border-radius: 4px;
                  max-height: 200px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <h1>Sistema de Registro y Validacion de Usuarios</h1>
        <div class="container">
            <div class="card">
                <h2>Registrar Usuario</h2>
                <form action="/registrar" method="post">
                    <label>Usuario (Nombre y Apellido):</label>
                    <input type="text" name="username" required>
                    <label>Direccion:</label>
                    <input type="text" name="direccion" required>
                    <label>Contrasena:</label>
                    <input type="password" name="password" required>
                    <button type="submit" class="btn-reg">Registrar</button>
                </form>
            </div>
            <div class="card">
                <h2>Validar Usuario</h2>
                <form action="/validar" method="post">
                    <label>Usuario:</label>
                    <input type="text" name="username" required>
                    <label>Contrasena:</label>
                    <input type="password" name="password" required>
                    <button type="submit" class="btn-val">Validar</button>
                </form>
            </div>
            <div class="card">
                <h2>Usuarios Registrados</h2>
                <button onclick="cargarUsuarios()" class="btn-list">Cargar Lista</button>
                <div id="lista-usuarios"></div>
            </div>
        </div>

        <script>
            function cargarUsuarios() {
                fetch('/usuarios')
                    .then(r => r.json())
                    .then(d => {
                        const div = document.getElementById('lista-usuarios');
                        if (d.usuarios.length === 0) {
                            div.innerHTML = '<p>No hay usuarios registrados.</p>';
                        } else {
                            let html = '<table border="1" style="width:100%;border-collapse:collapse;font-size:13px;">';
                            html += '<tr style="background:#007bff;color:white;"><th>Usuario</th><th>Direccion</th></tr>';
                            d.usuarios.forEach(u => {
                                html += '<tr><td>' + u.username + '</td><td>' + u.direccion + '</td></tr>';
                            });
                            html += '</table>';
                            div.innerHTML = html;
                        }
                    });
            }
        </script>
    </body>
    </html>
    """


@app.route("/registrar", methods=["POST"])
def registrar():
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        direccion = data.get("direccion")
        password = data.get("password")
    else:
        username = request.form.get("username")
        direccion = request.form.get("direccion")
        password = request.form.get("password")

    if not username or not direccion or not password:
        if request.is_json:
            return jsonify({"error": "Faltan username, direccion o password"}), 400
        else:
            return pagina_resultado("error", "Faltan username, direccion o password")

    registrar_usuario(username, password, direccion)
    if request.is_json:
        return jsonify({"mensaje": f"Usuario '{username}' registrado correctamente"})
    else:
        return pagina_resultado("exito", f"Usuario '{username}' registrado correctamente",
            f"<p style='text-align:center;color:#155724;'>Direccion: {direccion}</p>")


@app.route("/validar", methods=["POST"])
def validar():
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    if not username or not password:
        if request.is_json:
            return jsonify({"error": "Faltan username o password"}), 400
        else:
            return pagina_resultado("error", "Faltan username o password")

    usuario_data = validar_usuario(username, password)
    if usuario_data:
        if request.is_json:
            return jsonify({
                "mensaje": f"Usuario '{username}' validado correctamente",
                "direccion": usuario_data["direccion"]
            })
        else:
            return pagina_resultado("exito", f"Usuario '{username}' validado correctamente",
                f"<p style='text-align:center;color:#155724;'>Direccion: {usuario_data['direccion']}</p>")
    else:
        if request.is_json:
            return jsonify({"error": "Usuario o contrasena incorrectos"}), 401
        else:
            return pagina_resultado("error", "Usuario o contrasena incorrectos")


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, direccion FROM usuarios")
    usuarios = [{"username": row[0], "direccion": row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify({"usuarios": usuarios})


if __name__ == "__main__":
    init_db()
    print("\n=== Registrando usuarios de ejemplo ===")
    registrar_usuario("CARLOS HERNANDEZ", "clave123", "Av. Providencia 123, Santiago")
    registrar_usuario("admin", "admin123", "Calle Principal 456, Ciudad")

    print("\n=== Validando usuarios ===")
    datos = validar_usuario("CARLOS HERNANDEZ", "clave123")
    if datos:
        print(f"[OK] Prueba 1: 'CARLOS HERNANDEZ' validado - Direccion: {datos['direccion']}")
    else:
        print("[ERROR] Prueba 1: Fallo la validacion")

    datos = validar_usuario("CARLOS HERNANDEZ", "wrongpass")
    if datos:
        print("[ERROR] Prueba 2: Se valido con contrasena incorrecta")
    else:
        print("[OK] Prueba 2: Contrasena incorrecta rechazada correctamente")

    datos = validar_usuario("admin", "admin123")
    if datos:
        print(f"[OK] Prueba 3: 'admin' validado - Direccion: {datos['direccion']}")
    else:
        print("[ERROR] Prueba 3: Fallo la validacion")

    print("\n=== Usuarios en la base de datos (DB Browser for SQLite) ===")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, direccion, password_hash FROM usuarios")
    print(f"{'ID':<5} {'Username':<20} {'Direccion':<30} {'Password Hash'}")
    print("-" * 100)
    for row in cursor.fetchall():
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<30} {row[3]}")
    conn.close()
    print("\n[INFO] Abre DB Browser for SQLite, carga 'usuarios.db'")
    print("[INFO] y revisa la tabla 'usuarios' para ver los datos.")

    print("\n=== Iniciando servidor web ===")
    print("Abre tu navegador en: http://localhost:5800")
    print("Presiona Ctrl+C para detener el servidor.\n")
    app.run(host="0.0.0.0", port=5800, debug=True)
