import sys
from gunicorn.app import wsgiapp
import os
from dotenv import load_dotenv


def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    sys.argv.append("Tblog:create_app()")
    wsgiapp.run()
