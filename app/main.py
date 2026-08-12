from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(title="ChargeHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.routers import vehicles, employees, activities, notifications, auth, dashboard
app.include_router(vehicles.router)
app.include_router(employees.router)
app.include_router(activities.router)
app.include_router(notifications.router)
app.include_router(auth.router)
app.include_router(dashboard.router)


@app.get("/health")
def health():
    return {"status": "ok"}
