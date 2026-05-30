import os
import json
import urllib.parse
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

# Import google-genai SDK
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[-] google-genai library not found. Please install using: pip install google-genai")

def load_env(env_path=".env"):
    """Loads key-value pairs from .env file into os.environ for local testing"""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

# Pydantic schemas for structured Gemini output
class TrendItem(BaseModel):
    id: str = Field(description="Unique string identifier using lowercase letters, numbers, and hyphens (e.g., trend-london-arepa-2026)")
    country: str = Field(description="Country name in Spanish (e.g., España, Estados Unidos, Canadá)")
    flag: str = Field(description="Single flag emoji corresponding to the country (e.g., 🇪🇸, 🇺🇸, 🇨🇦)")
    restaurant: str = Field(description="Restaurant, bakery name, or event name with city in parentheses (e.g., 'Arepa Republic (Toronto)')")
    date: str = Field(description="Current month and year in Portuguese format (e.g., 'Maio 2026')")
    url: str = Field(description="Direct URL to a review, news article, or official page of this trend. MUST be a real, specific active URL, not a generic search or homepage.")
    title_es: str = Field(description="Catchy title in Spanish (approx 8-12 words)")
    title_pt: str = Field(description="Catchy title in Portuguese (approx 8-12 words)")
    summary_es: str = Field(description="Short summary in Spanish (approx 40-50 words)")
    summary_pt: str = Field(description="Short summary in Portuguese (approx 40-50 words)")
    full_content_es: str = Field(description="Detailed, rich blog post content in Spanish (approx 250-300 words) describing the restaurant, menu specialties, and why it is a trend.")
    full_content_pt: str = Field(description="Detailed, rich blog post content in Portuguese (approx 250-300 words) describing the restaurant, menu specialties, and why it is a trend.")
    image_prompt: str = Field(description="A descriptive prompt in English (approx 10-15 words) for generating a premium food photo of the dish or restaurant interior, suitable for a text-to-image AI model. Do not include text, signs, or watermarks in the prompt.")

class TrendList(BaseModel):
    trends: List[TrendItem]

def generate_trends_via_gemini():
    """Queries Gemini API with Google Search Grounding to find 3 fresh trends,
    then uses structured output schema to parse into the desired JSON format."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[-] GEMINI_API_KEY environment variable is missing. Cannot search.")
        return []

    client = genai.Client(api_key=api_key)

    # Step 1: Perform the Search with Grounding
    search_prompt = """
    Realiza una búsqueda en la web sobre las últimas novedades y tendencias gastronómicas de la comida venezolana por el mundo (arepas, cachapas, tequeños, nuevos restaurantes, eventos gastronómicos, pastelerías, etc.) correspondientes a finales de 2025 o el año 2026.
    
    Selecciona las 3 noticias o aperturas de restaurantes más novedosas y diversas del momento en cualquier parte del mundo (por ejemplo: España, Estados Unidos, Canadá, México, Portugal, Colombia, Perú, etc.).
    
    Proporciona una descripción detallada de cada una de estas 3 novedades, incluyendo obligatoriamente:
    - Nombre del establecimiento o evento gastronómico.
    - Ciudad y País donde se ubica.
    - Especialidades del menú o plato innovador que se menciona.
    - La URL real y exacta de la noticia, reseña o sitio oficial.
    """

    print("[*] Step 1: Performing Google Search Grounding with Gemini...")
    try:
        search_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=search_prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.7
            )
        )
        search_text = search_response.text
        print("[+] Google Search Grounding completed successfully.")
    except Exception as e:
        print(f"[-] Error in Step 1 (Google Search Grounding): {e}")
        return []

    # Step 2: Structure the search results into JSON schema
    structuring_prompt = f"""
    A partir de la información de búsqueda provista abajo, formatea las 3 tendencias gastronómicas venezolanas en el listado JSON requerido siguiendo exactamente el esquema indicado.
    
    Información de Búsqueda:
    {search_text}
    
    Reglas de Estructuración:
    1. Genera un ID único para cada tendencia (e.g., 'trend-madrid-arepa-2026').
    2. El campo 'date' debe ser el mes actual y año (e.g., 'Maio 2026').
    3. Para cada tendencia, escribe una redacción completa de aproximadamente 300 palabras para los campos 'full_content_es' (en español) y 'full_content_pt' (en portugués) describiendo detalladamente la noticia, las especialidades y su importancia.
    4. Para cada tendencia, crea un prompt descriptivo en inglés de 10-15 palabras para generar una foto realista de comida (sin textos ni logos) para 'image_prompt'.
    5. Usa exactamente las URLs específicas provistas en el informe de búsqueda. No las inventes.
    """

    print("[*] Step 2: Structuring Search Results into JSON...")
    try:
        json_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=structuring_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TrendList,
                temperature=0.2
            )
        )
        
        # Parse the JSON response
        result = json.loads(json_response.text)
        trends = result.get("trends", [])
        print(f"[+] Successfully scraped and structured {len(trends)} new trends from Gemini API.")
        return trends
    except Exception as e:
        print(f"[-] Error in Step 2 (Structuring Results): {e}")
        return []

def download_image_from_pollinations(prompt, filename):
    """Downloads an AI-generated image from Pollinations.ai and saves it locally"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true&private=true"
    
    print(f"[*] Generating and downloading image for prompt: '{prompt}'...")
    try:
        response = requests.get(url, timeout=45)
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

def send_email(subject, html_content, to_emails):
    """Sends email using SMTP credentials from environment variables"""
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.environ.get("SMTP_PORT", "465")
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not smtp_email or not smtp_password:
        print("[-] SMTP credentials not found in environment. Skipping email sending.")
        return False

    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        smtp_port = 465

    print(f"[*] Sending email to {', '.join(to_emails)} via {smtp_server}:{smtp_port}...")
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Venezuela Bistro SP <{smtp_email}>"
        msg["To"] = ", ".join(to_emails)

        msg.attach(MIMEText(html_content, "html"))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_emails, msg.as_string())
        server.quit()
        print("[+] Email sent successfully!")
        return True
    except Exception as e:
        print(f"[-] Failed to send email: {e}")
        return False

def generate_html_report(trends):
    """Generates a beautiful HTML report matching Venezuela Bistro SP's branding"""
    date_str = datetime.now().strftime("%d/%m/%Y")
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f7f7f7; color: #333333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05); border: 1px solid #e5e5e5; }}
            .header {{ background-color: #00247D; padding: 30px 20px; text-align: center; border-bottom: 5px solid #FFCC00; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; font-weight: bold; letter-spacing: -0.5px; }}
            .header p {{ color: #FFCC00; margin: 5px 0 0 0; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }}
            .content {{ padding: 30px 20px; }}
            .intro {{ font-size: 16px; line-height: 1.6; color: #555555; margin-bottom: 25px; }}
            .trend-card {{ background-color: #fafafa; border-left: 4px solid #CF142B; border-radius: 0 8px 8px 0; padding: 15px 20px; margin-bottom: 25px; border-top: 1px solid #eeeeee; border-right: 1px solid #eeeeee; border-bottom: 1px solid #eeeeee; }}
            .trend-meta {{ font-size: 11px; font-weight: bold; color: #00247D; text-transform: uppercase; margin-bottom: 5px; }}
            .trend-title {{ font-size: 18px; font-weight: bold; color: #222222; margin: 0 0 10px 0; }}
            .trend-desc {{ font-size: 14px; line-height: 1.5; color: #666666; margin: 0 0 12px 0; }}
            .trend-link {{ display: inline-block; color: #CF142B; text-decoration: none; font-weight: bold; font-size: 13px; }}
            .trend-link:hover {{ text-decoration: underline; }}
            .footer {{ background-color: #f0f0f0; padding: 20px; text-align: center; font-size: 12px; color: #999999; border-top: 1px solid #e5e5e5; }}
            .footer a {{ color: #00247D; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VENEZUELA BISTRO SP</h1>
                <p>Relatório de Tendências & Novedades</p>
            </div>
            <div class="content">
                <p class="intro">
                    Olá, David!<br><br>
                    Realizamos a pesquisa diária de tendências e atualizações sobre a gastronomia venezuelana pelo mundo. 
                    O feed do seu aplicativo web <strong>Venezuela Bistro SP</strong> foi atualizado com sucesso hoje (<strong>{date_str}</strong>).
                    <br><br>
                    Aquí está o resumo das informações encontradas e publicadas:
                </p>
    """

    for item in trends:
        html += f"""
                <div class="trend-card">
                    <div class="trend-meta">{item.get('flag', '🇻🇪')} {item.get('country', '')} · {item.get('restaurant', '')} · {item.get('date', '')}</div>
                    <div class="trend-title">{item.get('title_pt', item.get('title_es', ''))}</div>
                    <div class="trend-desc">{item.get('summary_pt', item.get('summary_es', ''))}</div>
                    <a class="trend-link" href="{item.get('url', '#')}" target="_blank">Ver Fonte Original &rarr;</a>
                </div>
        """

    html += """
                <p class="intro" style="margin-top:30px;">
                    O feed já está online no site. Caso queira modificar alguma publicação ou adicionar novos pratos, basta responder a esta mensagem.
                </p>
            </div>
            <div class="footer">
                © 2026 <a href="https://venezuelabistrosp.github.io/venezuelabistrosp/">Venezuela Bistro SP</a>. Todos os derechos reservados.<br>
                Enviado automaticamente pelo Agente de IA na Nuvem.
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    # Load .env variables locally (fails silently on Github Actions where env vars are already loaded)
    load_env()
    
    json_path = "scraped_data.json"
    
    # 1. Fetch new trends using Gemini Google Search Grounding
    new_trends = generate_trends_via_gemini()
    if not new_trends:
        print("[-] No new trends generated. Exiting.")
        return

    # Load existing database
    existing_data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"[-] Error loading existing json: {e}")

    # To avoid duplicate recommendations of the same restaurant/id
    existing_ids = {item.get("id") for item in existing_data}
    existing_names = {item.get("restaurant").lower() for item in existing_data if "restaurant" in item}

    items_to_add = []
    for item_dict in new_trends:
        # Convert Pydantic object back to dict if needed
        if not isinstance(item_dict, dict):
            item = item_dict.model_dump()
        else:
            item = item_dict

        # Sanity check spelling
        for key in ["title_pt", "title_es", "summary_pt", "summary_es", "full_content_es", "full_content_pt"]:
            if key in item and item[key]:
                item[key] = item[key].replace("Pabellão", "Pabellón").replace("pabellão", "pabellón")

        if item.get("id") in existing_ids or item.get("restaurant", "").lower() in existing_names:
            print(f"[*] Skipping {item.get('restaurant')} to avoid duplication.")
            continue

        # Download image for the trend
        image_filename = f"{item.get('id')}.png"
        success = download_image_from_pollinations(item.get("image_prompt"), image_filename)
        if success:
            item["image"] = image_filename
        else:
            item["image"] = "app_icon_512.png" # Fallback image
            
        items_to_add.append(item)

    if not items_to_add:
        print("[-] No new unique trends found after filtering duplicates.")
        return

    # Prepend new trends to existing list
    updated_data = items_to_add + existing_data

    # Enforce history limit (keep between 6 and 9 posts, e.g., max 8 posts)
    max_history = 8
    if len(updated_data) > max_history:
        print(f"[*] Truncating history from {len(updated_data)} items to {max_history} items.")
        updated_data = updated_data[:max_history]

    # 2. Write to scraped_data.json
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        print("[+] scraped_data.json updated successfully!")
    except Exception as e:
        print(f"[-] Error writing scraped_data.json: {e}")

    # 3. Update trends.js in the workspace
    trends_js_content = f"const VENEZUELA_BISTRO_TRENDS = {json.dumps(updated_data, indent=2, ensure_ascii=False)};\n\nif (typeof renderTrends === 'function') {{\n  renderTrends();\n}}"
    try:
        with open("trends.js", "w", encoding="utf-8") as f:
            f.write(trends_js_content)
        print("[+] trends.js updated successfully!")
    except Exception as e:
        print(f"[-] Error writing trends.js: {e}")

    # 4. Write Markdown report file as backup/log
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_md = f"# Relatório de Pesquisa de Tendências (Nuvem) - {date_str}\n\n"
    for item in updated_data:
        report_md += f"## {item.get('flag')} {item.get('title_pt')} ({item.get('country')})\n"
        report_meta = f"**Restaurante:** {item.get('restaurant')} | **Data:** {item.get('date')} | [Link]({item.get('url')})\n\n"
        report_md += report_meta
        report_md += f"{item.get('summary_pt')}\n\n"
        report_md += f"--- \n\n"

    try:
        with open("last_report.md", "w", encoding="utf-8") as f:
            f.write(report_md)
        print("[+] last_report.md written successfully!")
    except Exception as e:
        print(f"[-] Error writing last_report.md: {e}")

    # 5. Send email notification containing the new additions of today
    subject = f"Novas Tendências da Comida Venezuelana - {datetime.now().strftime('%d/%m/%Y')}"
    html_content = generate_html_report(items_to_add) # Email only lists the newly added ones
    
    recipient_emails = ["venezuelabistrosp@gmail.com", "linarezsanchez74@gmail.com"]
    send_email(subject, html_content, recipient_emails)

if __name__ == "__main__":
    main()
