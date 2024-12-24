from dotenv import load_dotenv

from myproject.application.bootstrap import Bootstrap

load_dotenv()

app = Bootstrap.create_app()
