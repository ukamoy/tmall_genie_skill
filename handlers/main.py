from fastapi import FastAPI
from handlers import welcome
from utils.middleware import add_logger_to_state

app = FastAPI()
app.middleware("http")(add_logger_to_state)

# mount routers
app.include_router(welcome.router)
