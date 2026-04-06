from utils.logger import log
from services.api import start_api
from ui.display import start_display

def main():
    log("Starting Smart Clock...")

    # Start Flask API (runs in background thread)
    start_api()

    # Start Kivy UI (this blocks until the app closes)
    start_display()


if __name__ == "__main__":
    main()
