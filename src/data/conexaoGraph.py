import requests
from utils.config import client_secret, client_id, tenant_id, scope, email_from
import json
import logging

class conexaoGraph:
    def acessoTokenGraph(self):
        # url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        # data = {
        #     'grant_type': 'client_credentials',
        #     'client_id': client_id,
        #     'client_secret': client_secret,
        #     'scope': scope
        # }
        # response = requests.post(url, data=data)
        # return response.json().get('access_token')
        pass

    def enviaEmailGraph(self, email_to, subject, body):
        email_group = email_to
        # Obter token de acesso
        url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope
        }
        response = requests.post(url, data=data)
        token = response.json().get('access_token')
        to_recipients = [{'emailAddress': {'address': email}} for email in email_group]
        url = f'https://graph.microsoft.com/v1.0/users/{email_from}/sendMail'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        email_msg = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML',
                    'content': body
                },
                'toRecipients': to_recipients
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(email_msg))
        if response.status_code == 202:
            logging.info(f"E-mail enviado para {email_group}")
            logging.info("------------------------------------------------------------------------------------")        
        else:
            logging.error(f'Falha ao enviar e-mail: {response.status_code}: {response.text}')
    
    # so essa função
    def enviar_email(self, lista_emails, assunto, corpo):
        email_group = lista_emails  

        # Obter token de acesso
        url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope
        }
        response = requests.post(url, data=data)
        token = response.json().get('access_token')

        # Preparar lista de destinatários
        destinatarios = [{'emailAddress': {'address': email}} for email in email_group]

        # Enviar email
        url = f'https://graph.microsoft.com/v1.0/users/{email_from}/sendMail'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        mensagem = {
            'message': {
                'subject': assunto,
                'body': {
                    'contentType': 'HTML',
                    'content': corpo
                },
                'toRecipients': destinatarios
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(mensagem))

        if response.status_code == 202:
            logging.info(f"Enviado e-mail para {email_group}")
            logging.info("------------------------------------------------------------------------------------")
        else:
            logging.error(f'Falha ao enviar email: {response.status_code}: {response.text}')
        # pass