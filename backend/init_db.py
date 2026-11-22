import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("mysql"):
    # db_url format: mysql+pymysql://root:261008@localhost:3306/examvault
    try:
        parts = db_url.split("@")
        creds = parts[0].split("://")[1]
        user, password = creds.split(":")
        
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 3306
        db_name = host_port_db[1]

        connection = pymysql.connect(host=host, user=user, password=password, port=port)
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")
        connection.commit()
        connection.close()
        print(f"[init_db] Ensured MySQL database '{db_name}' exists.")
    except Exception as e:
        print(f"[init_db] Error creating database: {e}")
