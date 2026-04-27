"""Root entry point — works on Render and locally."""
import os
from backend.app import app

application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)