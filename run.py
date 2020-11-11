from config import Config
from opinions import create_app

app = create_app(config=Config)

if __name__ == "__main__":
    app.run()
