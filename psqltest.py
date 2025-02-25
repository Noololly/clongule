import os

import psycopg2
import paramiko
from sshtunnel import SSHTunnelForwarder
import dotenv

class SQLConn:
    def __init__(self):
        dotenv.load_dotenv()
        self.PASSWORD = os.getenv('PASSWORD')

        self.mypkey = paramiko.Ed25519Key.from_private_key_file('SQLKey')

        tunnel = SSHTunnelForwarder(
            ('hackclub.app', 22),
            ssh_username="noololly",
            ssh_pkey=self.mypkey,
            remote_bind_address=('localhost', 5432)
        )

        tunnel.start()
        self.conn = psycopg2.connect(database="noololly", user="noololly", password=self.PASSWORD, host="127.76.48.123", port=tunnel.local_bind_port)