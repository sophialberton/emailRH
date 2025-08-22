import os 
from dotenv import load_dotenv
import logging
dotenv_path = os.path.join(os.path.dirname(__file__), '../..', '.env')  # Corrigido!
load_dotenv(dotenv_path)


#Database
host_data = os.getenv('host_senior')
port_data = os.getenv('port_senior')
service_name_data=os.getenv('service_name_senior')
user_data=os.getenv('user_senior')
password_data=os.getenv('password_senior')
pictureBirth = os.getenv('PICTUREBIRTH')
pictureNew = os.getenv('PICTURENEW')
linkRedirect= os.getenv('LINKREDIRECT')

#API
scope = os.getenv("SCOPE")
tenant_id = os.getenv("TENANT_ID")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
email_from = os.getenv("USER_MAIL")


#Database
host_senior           = os.getenv('host_senior')
port_senior           = os.getenv('port_senior')
service_name_senior   =os.getenv('service_name_senior')
user_senior           =os.getenv('user_senior')
password_senior       =os.getenv('password_senior')

dict_extract = {
    "Senior":{
        "host_senior":     host_senior,
        "port_senior":     port_senior,
        "service_name_senior":  service_name_senior,
        "user_senior":     user_senior,
        "password_senior": password_senior
    }   
}
masked_password = '*' * len(password_senior) if password_senior else None
logging.info(f"[DEBUG] host: {host_senior}, port: {port_senior}, service: {service_name_senior}, user: {user_senior}, password: {masked_password}")
