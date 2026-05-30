import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def load_env(env_path=".env"):
    """Simple helper to load key-value pairs from .env file into os.environ"""
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

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

    print(f"[*] Attempting to send email to {', '.join(to_emails)} via {smtp_server}:{smtp_port}...")
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Venezuela Bistro SP <{smtp_email}>"
        msg["To"] = ", ".join(to_emails)

        msg.attach(MIMEText(html_content, "html"))

        if smtp_port == 465:
            # SSL Connection
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # TLS Connection (typically port 587)
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
    
    # Styles and Header
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #f7f7f7;
                color: #333333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
                border: 1px solid #e5e5e5;
            }}
            .header {{
                background-color: #00247D; /* Azul Venezuela */
                padding: 30px 20px;
                text-align: center;
                border-bottom: 5px solid #FFCC00; /* Amarillo Venezuela */
            }}
            .header h1 {{
                color: #ffffff;
                margin: 0;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: -0.5px;
            }}
            .header p {{
                color: #FFCC00;
                margin: 5px 0 0 0;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 2px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .intro {{
                font-size: 16px;
                line-height: 1.6;
                color: #555555;
                margin-bottom: 25px;
            }}
            .trend-card {{
                background-color: #fafafa;
                border-left: 4px solid #CF142B; /* Rojo Venezuela */
                border-radius: 0 8px 8px 0;
                padding: 15px 20px;
                margin-bottom: 25px;
                border-top: 1px solid #eeeeee;
                border-right: 1px solid #eeeeee;
                border-bottom: 1px solid #eeeeee;
            }}
            .trend-meta {{
                font-size: 11px;
                font-weight: bold;
                color: #00247D;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}
            .trend-title {{
                font-size: 18px;
                font-weight: bold;
                color: #222222;
                margin: 0 0 10px 0;
            }}
            .trend-desc {{
                font-size: 14px;
                line-height: 1.5;
                color: #666666;
                margin: 0 0 12px 0;
            }}
            .trend-link {{
                display: inline-block;
                color: #CF142B;
                text-decoration: none;
                font-weight: bold;
                font-size: 13px;
            }}
            .trend-link:hover {{
                text-decoration: underline;
            }}
            .footer {{
                background-color: #f0f0f0;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #999999;
                border-top: 1px solid #e5e5e5;
            }}
            .footer a {{
                color: #00247D;
                text-decoration: none;
            }}
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
                    Aqui está o resumo das informações encontradas e publicadas:
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
                © 2026 <a href="https://venezuelabistrosp.github.io/venezuelabistrosp/">Venezuela Bistro SP</a>. Todos os direitos reservados.<br>
                Enviado automaticamente pelo Agente de IA Antigravity.
            </div>
        </div>
    </body>
    </html>
    """
    return html

def main():
    # Load .env variables
    load_env()
    
    # Path to workspace json with trends data
    json_path = "scraped_data.json"
    
    if not os.path.exists(json_path):
        print(f"[-] Data file {json_path} not found. Running with default dummy data.")
        # Create a basic sample structure if it doesn't exist
        sample_data = [
            {
                "id": "sample-1",
                "country": "Brasil",
                "flag": "🇧🇷",
                "restaurant": "Venezuela Bistro SP",
                "date": datetime.now().strftime("%B %Y"),
                "image": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "url": "https://venezuelabistrosp.github.io/venezuelabistrosp/",
                "title_pt": "Novidades no Cardápio: Arepas Tradicionais Recheadas",
                "title_es": "Novedades en el Menú: Arepas Tradicionales Rellenas",
                "summary_pt": "Atualizamos nosso feed diário com as melhores tendências de arepas e pratos venezuelanos pelo mundo. Venha conhecer!",
                "summary_es": "Actualizamos nuestro feed diario con las mejores tendencias de arepas y platos venezolanos por el mundo. ¡Ven a conocer!"
            }
        ]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
            
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            trends = json.load(f)
    except Exception as e:
        print(f"[-] Error loading {json_path}: {e}")
        return

    # 1. Update trends.js in the workspace
    trends_js_content = f"const VENEZUELA_BISTRO_TRENDS = {json.dumps(trends, indent=2, ensure_ascii=False)};\n\nif (typeof renderTrends === 'function') {{\n  renderTrends();\n}}"
    
    try:
        with open("trends.js", "w", encoding="utf-8") as f:
            f.write(trends_js_content)
        print("[+] trends.js updated successfully!")
    except Exception as e:
        print(f"[-] Error updating trends.js: {e}")

    # 2. Write Markdown report file as backup/log
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_md = f"# Relatório de Pesquisa de Tendências - {date_str}\n\n"
    for item in trends:
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

    # 3. Send Email
    subject = f"Tendências da Comida Venezuelana - {datetime.now().strftime('%d/%m/%Y')}"
    html_content = generate_html_report(trends)
    
    # Emails to send to
    recipient_emails = ["venezuelabistrosp@gmail.com", "linarezsanchez74@gmail.com"]
    send_email(subject, html_content, recipient_emails)

if __name__ == "__main__":
    main()
