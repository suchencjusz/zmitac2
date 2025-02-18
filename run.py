from config import Config

from app.main import app

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8001,
        debug=Config().DEBUG,
    )
