from config import Config
from main import app

if __name__ == "__main__":
    config = Config()

    ssl_context = "adhoc" if config.DEBUG else None

    app.run(
        host="0.0.0.0",
        port=5001,
        ssl_context=ssl_context,
        debug=config.DEBUG,
    )

