from app.main import app

from config import Config

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8001,
        debug=Config().DEBUG,
    )