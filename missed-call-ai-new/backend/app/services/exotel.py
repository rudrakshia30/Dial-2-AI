import os
from dotenv import load_dotenv

load_dotenv()

# Exotel credentials kept for reference / future API calls.
SID = os.getenv("EXOTEL_SID")
API_KEY = os.getenv("EXOTEL_API_KEY")
API_TOKEN = os.getenv("EXOTEL_API_TOKEN")
EXOTEL_NUM = os.getenv("EXOTEL_NUMBER", "09513886363")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# No outbound calls needed anymore.
# Callers dial the Exotel number directly and the flow
# connects them to /voice/start via Passthru applet.
