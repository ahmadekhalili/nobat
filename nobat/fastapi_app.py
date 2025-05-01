# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Create the app
app = FastAPI(
    title="My Notification Service",
    version="1.0.0",
    openapi_prefix="/api",            # optional: namespace all routes under /api
    docs_url="/docs",                # Swagger UI
    redoc_url="/redoc",              # ReDoc
)

# 2. Define a Pydantic model for your payload
class NotifyPayload(BaseModel):
    user_id: int
    message: str

# 3. Mount a router (best practice for larger apps)
from fastapi import APIRouter
notify_router = APIRouter(prefix="/notify", tags=["notify"])


@notify_router.post("/")
async def receive_notification(payload: NotifyPayload):
    return {"status": "ok", "received": payload.dict()}

@notify_router.get("/")
async def get_notifications():
    return {"status": "ok", "notifications": ["Hello", "World"]}

app.include_router(notify_router)


# 4. Run with Uvicorn on port 8002:
#    uvicorn app.main:app --host 0.0.0.0 --port 8002


# usage example:
'''
def send_notification(user_id: int, message: str) -> dict:
    url = "http://localhost:8002/notify/"  # note the trailing slash to match your router prefix
    payload = {
        "user_id": user_id,
        "message": message
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,           # automatically serializes to JSON and sets Content-Type
            headers=headers,
            timeout=5               # seconds; always set a timeout in production code
        )
        response.raise_for_status()  # raises HTTPError for 4xx/5xx responses
    except requests.exceptions.Timeout:
        print("Request timed out")
        return {}
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err} — Response body: {response.text}")
        return {}
    except requests.exceptions.RequestException as err:
        print(f"Error sending request: {err}")
        return {}

    # If we get here, the request was successful (2xx)
    return response.json()
'''


'''
workon nobat_as
python -m pip install --upgrade pip
python -m pip install uvicorn
pip install fastapi
'''