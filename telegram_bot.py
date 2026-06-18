import os
import json
import time
import subprocess
import requests
from google import genai
from bistro_manager import toggle_product_stock, update_schedule_hours, add_new_product, get_all_product_names

def load_env(env_path=".env"):
    """Loads key-value pairs from .env file into os.environ for local testing."""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def send_telegram_message(token, chat_id, text):
    """Sends a text message to a specific Telegram chat ID."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print("[-] Error sending Telegram message:", e)

def get_telegram_file_path(token, file_id):
    """Gets the file path for a file uploaded to Telegram."""
    url = f"https://api.telegram.org/bot{token}/getFile"
    try:
        r = requests.get(url, params={"file_id": file_id}, timeout=10)
        return r.json()
    except Exception as e:
        print("[-] Error getting Telegram file path:", e)
        return None

def get_updates(token, offset=None):
    """Polls the Telegram Bot API for new updates."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(url, params=params, timeout=35)
        return r.json()
    except Exception as e:
        print("[-] Error fetching updates:", e)
        return None

def run_git_commands(commit_message, files_to_add=None):
    """Stages files, commits, pulls remote changes (to avoid push rejections), and pushes to GitHub."""
    try:
        if files_to_add:
            for file in files_to_add:
                subprocess.run(["git", "add", file], check=True, capture_output=True)
        else:
            subprocess.run(["git", "add", "index.html", "index_redesign.html"], check=True, capture_output=True)
            
        # Commit local changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
        
        # Pull remote changes with rebase to prevent conflicts with daily trend commits from GitHub Actions
        subprocess.run(["git", "pull", "--rebase"], check=True, capture_output=True)
        
        # Push to origin main
        subprocess.run(["git", "push"], check=True, capture_output=True)
        print("[+] Git operations completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Git command failed: {e.cmd}")
        print(f"[-] Output: {e.output.decode('utf-8', errors='ignore')}")
        print(f"[-] Error: {e.stderr.decode('utf-8', errors='ignore')}")
        # If pull/push failed, attempt to clean up any rebase state
        if "rebase" in str(e.cmd):
            subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        return False

def parse_command_with_gemini(message_text, product_list=None):
    """Uses Gemini 2.5 Flash to parse natural language owner messages into JSON actions."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY missing.")
        return None
        
    client = genai.Client(api_key=api_key)
    
    products_info = ""
    if product_list:
        products_info = f"\nLista de productos oficiales del menú:\n" + "\n".join([f"- {p}" for p in product_list]) + "\n"
    
    prompt = f"""
    Eres un asistente inteligente para el restaurante venezolano 'Venezuela Bistro' en São Paulo.
    Tu tarea es clasificar el mensaje de texto del dueño del local en una acción estructurada en formato JSON.
    {products_info}
    Acciones soportadas:
    1. Pausar un producto (marcarlo como sin stock/agotado):
       - Mensajes de ejemplo: "Pausar Arepa Vegetariana", "pausa arepa de camarón", "arepa vegetariana agotada", "desactivar empanada cazón".
       - Formato de respuesta JSON: {{"action": "pause", "target": "Nombre exacto del producto en portugués/español"}}
       - Regla crítica: Si la acción es 'pause', el campo 'target' DEBE coincidir exactamente con uno de los productos de la lista de productos oficiales del menú si es posible. Si el dueño escribe un nombre con faltas de ortografía, en minúsculas, o abreviado (ej: 'coca cola zero', 'coca zero', 'Coca-Cola zero', o 'coca-cola lata350 ml'), mapealo al nombre oficial correspondiente de la lista (ej: 'Coca-Cola Lata 350ml - Zero' o 'Coca-Cola Lata 350ml - Original').
       
    2. Activar un producto (marcarlo como disponible/con stock):
       - Mensajes de ejemplo: "Activar arepa vegetariana", "arepa vegetariana disponible", "activar empanada cazón".
       - Formato de respuesta JSON: {{"action": "activate", "target": "Nombre exacto del producto en portugués/español"}}
       - Regla crítica: Si la acción es 'activate', el campo 'target' DEBE coincidir exactamente con uno de los productos de la lista de productos oficiales del menú si es posible. Si el dueño escribe un nombre abreviado, mapealo al oficial.
       
    3. Cambiar horarios de atención:
       - Mensajes de ejemplo: "Horario hoy: cerrado por lluvia", "Horario domingo: 12:00 a 19:00", "Horario: de 11:00 a 22:00 de martes a domingo".
       - Formato de respuesta JSON: {{"action": "schedule", "hours_pt": "Texto formateado en portugués", "hours_es": "Texto formateado en español", "hours_html": "Texto predeterminado para la cabecera HTML"}}
       
    4. Acción desconocida / No clasificada:
       - Si no coincide con ninguna acción.
       - Formato de respuesta JSON: {{"action": "unknown"}}
       
    Mensaje del dueño: "{message_text}"
    
    Responde ÚNICAMENTE con el objeto JSON. No agregues explicaciones, marcas de código de Markdown como ```json ni comentarios.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        # Strip markdown tags if generated
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        return json.loads(text)
    except Exception as e:
        print("[-] Error calling Gemini to parse text command:", e)
        return None

def parse_product_upload(caption_text):
    """Uses Gemini 2.5 Flash to parse product captions into name, desc, price, category translations."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY missing.")
        return None
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Analiza la descripción del nuevo plato que se añadirá al menú de 'Venezuela Bistro'.
    Extrae los datos y traduce automáticamente los nombres y descripciones al español y al portugués.
    
    Las categorías del menú válidas son: 'combos', 'arepas', 'cachapas', 'empanadas', 'tequeños', 'sobremesas', 'bebidas'.
    
    Campos de respuesta en el JSON:
    - name_es: Nombre del plato en español
    - name_pt: Nombre del plato en portugués
    - desc_es: Descripción apetitosa en español
    - desc_pt: Descripción apetitosa en portugués
    - price: Precio numérico en reales (float)
    - category: Una de las categorías del menú válidas listadas arriba
    - slug: Un identificador corto derivado del nombre en minúsculas y guiones bajos (ej. 'arepa_pernil')
    
    Descripción recibida:
    "{caption_text}"
    
    Responde ÚNICAMENTE con el objeto JSON. No agregues explicaciones ni marcas de código Markdown.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        return json.loads(text)
    except Exception as e:
        print("[-] Error calling Gemini to parse product caption:", e)
        return None

def handle_message(token, message):
    """Processes an incoming Telegram message."""
    text = message.get("text", "")
    caption = message.get("caption", "")
    photo = message.get("photo")
    chat_id = message["chat"]["id"]
    
    # 1. Start / Help info
    if text in ["/start", "/help"]:
        welcome_msg = (
            "¡Hola David! Bienvenido al panel de control de Venezuela Bistro SP 📲🍔\n\n"
            "Estas son las acciones que puedo realizar:\n\n"
            "1. **Pausar un plato (Agotado):**\n"
            "   Escribe 'Pausar Arepa Vegetariana' o '/pausar Arepa Vegetariana'.\n\n"
            "2. **Activar un plato (Disponible):**\n"
            "   Escribe 'Activar Arepa Vegetariana' o '/activar Arepa Vegetariana'.\n\n"
            "3. **Cambiar Horario:**\n"
            "   Escribe 'Horario domingo: 12:00 a 19:00' o 'Horario hoy: cerrado por lluvia'.\n\n"
            "4. **Agregar nuevo plato con foto:**\n"
            "   Envía una foto de comida y agrégale este pie de foto (caption):\n"
            "   *Nombre: Arepa de Pernil*\n"
            "   *Precio: R$ 32,00*\n"
            "   *Categoría: arepas*\n"
            "   *Descripción: Rellena con pernil asado y salsa.*"
        )
        send_telegram_message(token, chat_id, welcome_msg)
        return

    # 2. Product Upload with Photo
    if photo and caption:
        send_telegram_message(token, chat_id, "🔄 Procesando foto y descripción de nuevo plato...")
        details = parse_product_upload(caption)
        if not details or "price" not in details or "category" not in details:
            send_telegram_message(token, chat_id, "❌ No pude interpretar la descripción del plato. Asegúrate de incluir Nombre, Precio, Categoría y una Descripción clara.")
            return
            
        slug = details["slug"]
        name_pt = details["name_pt"]
        name_es = details["name_es"]
        desc_pt = details["desc_pt"]
        desc_es = details["desc_es"]
        price = details["price"]
        category = details["category"]
        
        # Download highest resolution image
        largest_photo = photo[-1]
        file_id = largest_photo["file_id"]
        
        file_path_info = get_telegram_file_path(token, file_id)
        if not file_path_info or not file_path_info.get("ok"):
            send_telegram_message(token, chat_id, "❌ Error al obtener la ruta de la imagen desde Telegram.")
            return
            
        file_path = file_path_info["result"]["file_path"]
        image_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        
        image_filename = f"{slug}.jpg"
        local_image_path = os.path.join(os.getcwd(), image_filename)
        
        try:
            r = requests.get(image_url, stream=True, timeout=20)
            if r.status_code == 200:
                with open(local_image_path, 'wb') as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
            else:
                send_telegram_message(token, chat_id, f"❌ Error al descargar imagen de Telegram (Código HTTP: {r.status_code}).")
                return
        except Exception as e:
            send_telegram_message(token, chat_id, f"❌ Error al descargar e guardar la imagen: {e}")
            return
            
        send_telegram_message(token, chat_id, f"📸 Imagen guardada como `{image_filename}`. Insertando plato en los archivos HTML...")
        
        # Inject card into both pages
        updated_index = add_new_product("index.html", slug, name_pt, name_es, desc_pt, desc_es, price, category, image_filename)
        updated_redesign = add_new_product("index_redesign.html", slug, name_pt, name_es, desc_pt, desc_es, price, category, image_filename)
        
        if updated_index or updated_redesign:
            commit_msg = f"Telegram Bot: Añadido plato {name_pt} (Categoría: {category})"
            success = run_git_commands(commit_msg, [image_filename, "index.html", "index_redesign.html"])
            if success:
                send_telegram_message(token, chat_id, f"✅ ¡Plato `{name_pt}` añadido con éxito e implementado en GitHub! Estará visible en unos 2 minutos.")
            else:
                send_telegram_message(token, chat_id, "⚠️ El plato fue añadido localmente pero falló subir los archivos a GitHub. Revisa la terminal.")
        else:
            send_telegram_message(token, chat_id, "❌ Error al inyectar el plato en los archivos HTML.")
        return

    # 3. Text Command Actions
    if text:
        # Fetch the official list of products dynamically to guide Gemini's mapping
        product_list = get_all_product_names("index.html")
        cmd = parse_command_with_gemini(text, product_list)
        if not cmd:
            send_telegram_message(token, chat_id, "❌ Error al procesar tu mensaje con Gemini.")
            return
            
        action = cmd.get("action")
        target = cmd.get("target")
        
        if action == "pause":
            send_telegram_message(token, chat_id, f"🔄 Marcando `{target}` como Agotado...")
            updated_index = toggle_product_stock("index.html", target, True)
            updated_redesign = toggle_product_stock("index_redesign.html", target, True)
            
            if updated_index or updated_redesign:
                commit_msg = f"Telegram Bot: Pausado {target}"
                success = run_git_commands(commit_msg, ["index.html", "index_redesign.html"])
                if success:
                    send_telegram_message(token, chat_id, f"✅ ¡Hecho! `{target}` marcado como AGOTADO en la web.")
                else:
                    send_telegram_message(token, chat_id, "⚠️ Cambiado localmente pero falló subirlo a GitHub.")
            else:
                send_telegram_message(token, chat_id, f"❌ No encontré ningún producto con el nombre `{target}` en el menú.")
                
        elif action == "activate":
            send_telegram_message(token, chat_id, f"🔄 Activando `{target}`...")
            updated_index = toggle_product_stock("index.html", target, False)
            updated_redesign = toggle_product_stock("index_redesign.html", target, False)
            
            if updated_index or updated_redesign:
                commit_msg = f"Telegram Bot: Activado {target}"
                success = run_git_commands(commit_msg, ["index.html", "index_redesign.html"])
                if success:
                    send_telegram_message(token, chat_id, f"✅ ¡Hecho! `{target}` ya está disponible nuevamente en la web.")
                else:
                    send_telegram_message(token, chat_id, "⚠️ Cambiado localmente pero falló subirlo a GitHub.")
            else:
                send_telegram_message(token, chat_id, f"❌ No encontré ningún producto con el nombre `{target}` en el menú.")
                
        elif action == "schedule":
            hours_pt = cmd.get("hours_pt")
            hours_es = cmd.get("hours_es")
            hours_html = cmd.get("hours_html")
            
            send_telegram_message(token, chat_id, f"🔄 Actualizando horarios...\nPT: `{hours_pt}`\nES: `{hours_es}`")
            updated_index = update_schedule_hours("index.html", hours_pt, hours_es, hours_html)
            updated_redesign = update_schedule_hours("index_redesign.html", hours_pt, hours_es, hours_html)
            
            if updated_index or updated_redesign:
                commit_msg = f"Telegram Bot: Horario cambiado a {hours_html}"
                success = run_git_commands(commit_msg, ["index.html", "index_redesign.html"])
                if success:
                    send_telegram_message(token, chat_id, f"✅ ¡Horarios actualizados en la web con éxito a: `{hours_html}`!")
                else:
                    send_telegram_message(token, chat_id, "⚠️ Cambiado localmente pero falló subirlo a GitHub.")
            else:
                send_telegram_message(token, chat_id, "❌ Error al actualizar los horarios en los archivos HTML.")
        else:
            send_telegram_message(
                token, 
                chat_id, 
                "🤔 No entendí esa orden. Recuerda que puedes pausar/activar productos (ej: 'Pausar arepa vegetariana') o cambiar el horario (ej: 'Horario domingo: 12:00 a 19:00')."
            )

def main():
    load_env()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    allowed_chat_id = os.environ.get("TELEGRAM_ALLOWED_CHAT_ID")
    
    if not token or not allowed_chat_id:
        print("[-] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_ALLOWED_CHAT_ID in environment.")
        return
        
    allowed_chat_id = int(allowed_chat_id)
    print(f"[*] Starting Telegram Bot in polling mode...")
    print(f"[*] Filtering messages for Chat ID: {allowed_chat_id}")
    
    offset = None
    while True:
        try:
            updates = get_updates(token, offset)
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    message = update.get("message")
                    if not message:
                        continue
                        
                    chat_id = message["chat"]["id"]
                    if chat_id != allowed_chat_id:
                        print(f"[-] Unauthorized message from chat_id: {chat_id}")
                        continue
                        
                    handle_message(token, message)
            time.sleep(1.5)
        except KeyboardInterrupt:
            print("[*] Stopping bot...")
            break
        except Exception as e:
            print("[-] Error in main loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
