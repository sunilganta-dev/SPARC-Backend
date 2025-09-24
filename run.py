import os
from app import create_app, db
from flask_migrate import Migrate
from config import config

# Get environment (default = development)
env = os.getenv("FLASK_ENV", "default")

# Create app with factory pattern
app = create_app(env)
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)
