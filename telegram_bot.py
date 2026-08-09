import os
import json
import time
import subprocess
import requests
import urllib.parse
from datetime import datetime
from google import genai
from bistro_manager import (
    toggle_product_stock, 
    update_schedule_hours, 
    add_new_product, 
    get_all_product_names,
    change_product_price,
    edit_product_description,
    add_blog_post_to_json,
    add_blog_post_to_js
)

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

LAST_GIT_ERROR = "None"

def run_git_commands(commit_message, files_to_add=None):
    """Stages files, commits, pulls remote changes (to avoid push rejections), and pushes to GitHub."""
    try:
        # Ensure git user identity is configured for the container
        subprocess.run(["git", "config", "user.name", "Venezuela Bistro SP"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "venezuelabistrosp@gmail.com"], capture_output=True)
        
        # Configure remote URL with GITHUB_TOKEN if running in the cloud
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            remote_url = f"https://x-token-auth:{github_token}@github.com/venezuelabistrosp/venezuelabistrosp.git"
            check_remote = subprocess.run(["git", "remote"], capture_output=True, text=True)
            if "origin" in check_remote.stdout:
                subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True, capture_output=True)
            else:
                subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True)
            
        # Automatically update sw.js version and add it to the commit
        try:
            from bistro_manager import update_service_worker_cache_version
            if update_service_worker_cache_version("sw.js"):
                if files_to_add is not None:
                    if "sw.js" not in files_to_add:
                        files_to_add.append("sw.js")
                else:
                    files_to_add = ["index.html", "index_redesign.html", "sw.js"]
        except Exception as e:
            print("[-] Failed to update sw.js cache name in run_git_commands:", e)

        if files_to_add:
            for file in files_to_add:
                subprocess.run(["git", "add", file], check=True, capture_output=True)
        else:
            subprocess.run(["git", "add", "index.html", "index_redesign.html", "sw.js"], check=True, capture_output=True)
            
        # Commit local changes
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
        
        # Pull remote changes with rebase to prevent conflicts with daily trend commits from GitHub Actions
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True, capture_output=True)
        
        # Push to origin main
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("[+] Git operations completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        global LAST_GIT_ERROR
        cmd_str = str(e.cmd)
        out_str = e.output.decode("utf-8", errors="ignore")
        err_str = e.stderr.decode("utf-8", errors="ignore")
        LAST_GIT_ERROR = f"Command: {cmd_str}\nStdout: {out_str}\nStderr: {err_str}"
        
        print(f"[-] Git command failed: {e.cmd}")
        print(f"[-] Output: {e.output.decode('utf-8', errors='ignore')}")
        print(f"[-] Error: {e.stderr.decode('utf-8', errors='ignore')}")
        # If pull/push failed, attempt to clean up any rebase state
        if "rebase" in str(e.cmd):
            subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        return False

def download_image_from_pollinations(prompt, filename):
    """Downloads an AI-generated image from Pollinations.ai and saves it locally."""
    import random
    encoded_prompt = urllib.parse.quote(prompt)
    seed = random.randint(1, 999999)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true&private=true&feed=false&seed={seed}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    print(f"[*] Generating and downloading image for prompt: '{prompt}'...")
    try:
        response = requests.get(url, headers=headers, timeout=45)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"[+] Image saved successfully as {filename}")
            return True
        else:
            print(f"[-] Failed to generate image from Pollinations: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[-] Error downloading image: {e}")
        return False

def datetime_current_month_year():
    """Returns the current month (in Portuguese) and year (e.g., 'Maio 2026')."""
    months_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    now = datetime.now()
    month_name = months_pt.get(now.month, "Junho")
    return f"{month_name} {now.year}"

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
       
    4. Cambiar el precio de un producto:
       - Mensajes de ejemplo: "Cambiar precio de Arepa de Pabellón a R$ 48,00", "coca-cola zero a 10 reales", "cambiar precio de tequeños a 25".
       - Formato de respuesta JSON: {{"action": "change_price", "target": "Nombre exacto del producto", "price": float}}
       - Regla crítica: El campo 'target' debe ser el nombre oficial de la lista. El precio debe ser un número decimal.
       
    5. Editar la descripción de un producto:
       - Mensajes de ejemplo: "Cambiar descripción de Arepa Reina Pepeada a: Deliciosa arepa reina de la casa.", "descripción de tequeños ahora es: Dedos de queso fritos envueltos en masa crujiente."
       - Formato de respuesta JSON: {{"action": "edit_description", "target": "Nombre exacto del producto", "desc_es": "Descripción redactada de forma atractiva en español", "desc_pt": "Descripción redactada de forma atractiva traducida al portugués"}}
       - Regla crítica: El campo 'target' debe ser el nombre oficial de la lista. Traduce la nueva descripción de forma apetitosa a ambos idiomas.
       
    6. Publicar una noticia / post en el blog:
       - Mensajes de ejemplo: "Publicar noticia: Mañana abrimos a las 8 am para la copa américa!", "noticia blog: Nueva arepa de pernil disponible en Sao Paulo."
       - Formato de respuesta JSON: {{
           "action": "publish_news",
           "title_es": "Título atractivo y periodístico en español (ej. 'Venezuela Bistro transmite en vivo la Copa América en São Paulo')",
           "title_pt": "Título atractivo y periodístico traducido al portugués",
           "summary_es": "Resumen corto en español (una frase de 15-20 palabras)",
           "summary_pt": "Resumen corto en portugués",
           "full_content_es": "Contenido expandido y detallado en español (aproximadamente 100 palabras) sobre la noticia",
           "full_content_pt": "Contenido expandido y detallado traducido al portugués (aproximadamente 100 palabras)",
           "country": "Brasil",
           "flag": "🇧🇷",
           "restaurant": "Venezuela Bistro SP",
           "image_prompt": "Un prompt en inglés de 10-12 palabras para generar una foto realista que represente la noticia gastronómica (sin textos ni logos en la imagen)"
         }}
       
    7. Acción desconocida / No clasificada:
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

def publish_news_post(token, chat_id, cmd, photo_list=None):
    """Generates and prepends a bilingual news post, generating or using the uploaded photo."""
    send_telegram_message(token, chat_id, "🔄 Redactando post de blog bilingüe y preparando imagen...")
    
    import random
    slug = f"trend-{cmd.get('restaurant', 'bistro').lower().replace(' ', '-')}-{int(time.time())}"
    
    image_filename = f"{slug}.png"
    local_image_path = os.path.join(os.getcwd(), image_filename)
    
    image_success = False
    if photo_list:
        # User uploaded their own photo
        largest_photo = photo_list[-1]
        file_id = largest_photo["file_id"]
        file_path_info = get_telegram_file_path(token, file_id)
        if file_path_info and file_path_info.get("ok"):
            file_path = file_path_info["result"]["file_path"]
            image_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
            try:
                r = requests.get(image_url, stream=True, timeout=20)
                if r.status_code == 200:
                    with open(local_image_path, 'wb') as f:
                        for chunk in r.iter_content(1024):
                            f.write(chunk)
                    image_success = True
            except Exception as e:
                print("[-] Error downloading user photo:", e)
    else:
        # Generate image using Pollinations.ai
        image_prompt = cmd.get("image_prompt", "Gourmet Venezuelan food, professional dining photography")
        image_success = download_image_from_pollinations(image_prompt, local_image_path)
        
    if not image_success:
        image_filename = "historia.jpg" # Fallback to existing image
        
    # Construct trend item
    new_item = {
        "id": slug,
        "country": cmd.get("country", "Brasil"),
        "flag": cmd.get("flag", "🇧🇷"),
        "restaurant": cmd.get("restaurant", "Venezuela Bistro SP"),
        "date": datetime_current_month_year(),
        "url": "https://venezuelabistrosp.github.io/venezuelabistrosp/",
        "title_es": cmd.get("title_es", ""),
        "title_pt": cmd.get("title_pt", ""),
        "summary_es": cmd.get("summary_es", ""),
        "summary_pt": cmd.get("summary_pt", ""),
        "full_content_es": cmd.get("full_content_es", ""),
        "full_content_pt": cmd.get("full_content_pt", ""),
        "image_prompt": cmd.get("image_prompt", ""),
        "image": image_filename
    }
    
    # Save to data and script files
    add_blog_post_to_json("scraped_data.json", new_item)
    add_blog_post_to_js("trends.js", new_item)
    
    # Stage and push
    files_to_commit = ["trends.js", "scraped_data.json"]
    if image_success:
        files_to_commit.append(image_filename)
        
    commit_msg = f"Telegram Bot: Publicada noticia: {cmd.get('title_es', '')[:30]}..."
    success = run_git_commands(commit_msg, files_to_commit)
    if success:
        send_telegram_message(token, chat_id, f"✅ ¡Noticia publicada con éxito! Título: `{cmd.get('title_es')}`. Estará visible en el blog en unos 2 minutos.")
    else:
        send_telegram_message(token, chat_id, "⚠️ La noticia fue creada localmente pero falló subir los archivos a GitHub.")

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
            "   Escribe 'Pausar Arepa Vegetariana'.\n\n"
            "2. **Activar un plato (Disponible):**\n"
            "   Escribe 'Activar Arepa Vegetariana'.\n\n"
            "3. **Cambiar Horario:**\n"
            "   Escribe 'Horario domingo: 12:00 a 19:00'.\n\n"
            "4. **Cambiar Precio:**\n"
            "   Escribe 'Cambiar precio de Arepa de Pabellón a R$ 48,00'.\n\n"
            "5. **Editar Descripción:**\n"
            "   Escribe 'Cambiar descripción de Arepa Reina Pepeada a: [Nueva descripción]'.\n\n"
            "6. **Publicar Noticia en el Blog:**\n"
            "   Escribe 'Publicar noticia: [Texto de la noticia]' o envía una foto con ese pie de foto.\n\n"
            "7. **Agregar nuevo plato con foto:**\n"
            "   Envía una foto de comida y agrégale este pie de foto (caption):\n"
            "   *Nombre: Arepa de Pernil*\n"
            "   *Precio: R$ 32,00*\n"
            "   *Categoría: arepas*\n"
            "   *Descripción: Rellena con pernil asado.*"
        )
        send_telegram_message(token, chat_id, welcome_msg)
        return

    # 2. News or Product Upload with Photo
    if photo and caption:
        is_news = any(kw in caption.lower() for kw in ["noticia", "publicar", "blog", "post", "novedad"])
        if is_news:
            cmd = parse_command_with_gemini(caption)
            if cmd and cmd.get("action") == "publish_news":
                publish_news_post(token, chat_id, cmd, photo)
            else:
                send_telegram_message(token, chat_id, "❌ No pude interpretar los detalles de la noticia en el pie de foto.")
            return
            
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
                
        elif action == "change_price":
            price = cmd.get("price")
            send_telegram_message(token, chat_id, f"🔄 Cambiando precio de `{target}` a R$ {price:.2f}...")
            updated_index = change_product_price("index.html", target, price)
            updated_redesign = change_product_price("index_redesign.html", target, price)
            
            if updated_index or updated_redesign:
                commit_msg = f"Telegram Bot: Cambiado precio de {target} a R$ {price:.2f}"
                success = run_git_commands(commit_msg, ["index.html", "index_redesign.html"])
                if success:
                    send_telegram_message(token, chat_id, f"✅ ¡Hecho! Precio de `{target}` actualizado a R$ {price:.2f} en la web.")
                else:
                    send_telegram_message(token, chat_id, "⚠️ Cambiado localmente pero falló subirlo a GitHub.")
            else:
                send_telegram_message(token, chat_id, f"❌ No encontré ningún producto con el nombre `{target}` en el menú.")
                
        elif action == "edit_description":
            desc_es = cmd.get("desc_es")
            desc_pt = cmd.get("desc_pt")
            send_telegram_message(token, chat_id, f"🔄 Editando descripción de `{target}`...")
            updated_index = edit_product_description("index.html", target, desc_pt, desc_es)
            updated_redesign = edit_product_description("index_redesign.html", target, desc_pt, desc_es)
            
            if updated_index or updated_redesign:
                commit_msg = f"Telegram Bot: Editada descripción de {target}"
                success = run_git_commands(commit_msg, ["index.html", "index_redesign.html"])
                if success:
                    send_telegram_message(token, chat_id, f"✅ ¡Hecho! Descripción de `{target}` actualizada con éxito en la web.")
                else:
                    send_telegram_message(token, chat_id, "⚠️ Cambiado localmente pero falló subirlo a GitHub.")
            else:
                send_telegram_message(token, chat_id, f"❌ No encontré ningún producto con el nombre `{target}` en el menú.")
                
        elif action == "publish_news":
            publish_news_post(token, chat_id, cmd, None)
            
        else:
            send_telegram_message(
                token, 
                chat_id, 
                "🤔 No entendí esa orden. Recuerda que puedes pausar/activar productos, cambiar precios, editar descripciones, cambiar horarios o publicar noticias."
            )

import threading
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health_check():
    import subprocess
    global LAST_GIT_ERROR
    return jsonify({
        "status": "ok",
        "bot": "running",
        "has_token": os.environ.get("GITHUB_TOKEN") is not None,
        "commit": subprocess.getoutput("git rev-parse --short HEAD"),
        "last_git_error": LAST_GIT_ERROR
    }), 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

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
    
    # Start Flask health check server in background thread for Render
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    print("[*] Flask health check server started.")
    
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
