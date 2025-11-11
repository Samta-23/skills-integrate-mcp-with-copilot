"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from sqlmodel import Session, select

from src.db import get_engine, create_db_and_tables, Activity, Signup


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize DB and engine
engine = get_engine()
create_db_and_tables(engine)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with Session(engine) as session:
        activities = session.exec(select(Activity)).all()
        result = {}
        for a in activities:
            # load participants
            participants = session.exec(select(Signup).where(Signup.activity_id == a.id)).all()
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": [p.email for p in participants]
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    with Session(engine) as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participants = session.exec(select(Signup).where(Signup.activity_id == activity.id)).all()

        # Validate student is not already signed up
        if any(p.email == email for p in participants):
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Validate capacity
        if len(participants) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        signup = Signup(activity_id=activity.id, email=email)
        session.add(signup)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    with Session(engine) as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        signup = session.exec(
            select(Signup).where((Signup.activity_id == activity.id) & (Signup.email == email))
        ).first()

        # Validate student is signed up
        if not signup:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(signup)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
