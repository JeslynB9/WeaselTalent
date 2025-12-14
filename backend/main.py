from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from assessment import router as courses_router
from users import router as users_router
from auth import router as auth_router
from candidate import router as candidate_router
from recruiter_routes import router as recruiter_router

app = FastAPI(title="WeaselTalent API")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(candidate_router)
app.include_router(courses_router)
app.include_router(recruiter_router)

# -----------------------------
# Health check (optional but useful)
# -----------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}
