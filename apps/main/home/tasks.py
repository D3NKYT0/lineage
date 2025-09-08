import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from django.conf import settings


@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    """
    Envia email usando Python puro (smtplib) ao invés do Django
    """
    # Configurações de email do ambiente
    email_enable = os.getenv('CONFIG_EMAIL_ENABLE', 'False').lower() in ['true', '1', 'yes']
    
    if not email_enable:
        print(f"[EMAIL DISABLED] Subject: {subject} | To: {recipient_list}")
        return False
    
    email_host = os.getenv('CONFIG_EMAIL_HOST')
    email_user = os.getenv('CONFIG_EMAIL_HOST_USER')
    email_password = os.getenv('CONFIG_EMAIL_HOST_PASSWORD')
    email_port = int(os.getenv('CONFIG_EMAIL_PORT', 587))
    email_use_tls = os.getenv('CONFIG_EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    default_from = os.getenv('CONFIG_DEFAULT_FROM_EMAIL', email_user)
    
    # Validações
    if not all([email_host, email_user, email_password]):
        print(f"[EMAIL ERROR] Missing SMTP configuration")
        return False
    
    if not recipient_list:
        print(f"[EMAIL ERROR] No recipients provided")
        return False
    
    # Configurar email
    msg = MIMEMultipart()
    msg['From'] = from_email or default_from
    msg['To'] = ', '.join(recipient_list) if isinstance(recipient_list, list) else recipient_list
    msg['Subject'] = subject
    
    # Adicionar corpo do email
    msg.attach(MIMEText(message, 'plain', 'utf-8'))
    
    try:
        # Conectar ao servidor SMTP
        print(f"[EMAIL] Connecting to {email_host}:{email_port}")
        server = smtplib.SMTP(email_host, email_port, timeout=30)
        
        # Habilitar TLS se configurado
        if email_use_tls:
            print(f"[EMAIL] Starting TLS")
            server.starttls()
        
        # Login
        print(f"[EMAIL] Logging in as {email_user}")
        server.login(email_user, email_password)
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(
            from_email or default_from, 
            recipient_list, 
            text
        )
        
        # Fechar conexão
        server.quit()
        
        print(f"[EMAIL SUCCESS] Sent to {recipient_list}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL ERROR] Authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EMAIL ERROR] Recipients refused: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"[EMAIL ERROR] Server disconnected: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[EMAIL ERROR] SMTP error: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] Unexpected error: {e}")
        return False 
