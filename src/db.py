from typing import List, Optional
import os

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./activities.db")


class Signup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int = Field(foreign_key="activity.id")
    email: str
    activity: Optional["Activity"] = Relationship(back_populates="participants")


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: int = 0
    participants: List[Signup] = Relationship(back_populates="activity")


def create_db_and_tables(engine=None):
    if engine is None:
        engine = create_engine(DATABASE_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    # seed data if empty
    with Session(engine) as session:
        count = session.exec(select(Activity)).first()
        if count is None:
            seed_activities(session)


def get_engine():
    # SQLite needs check_same_thread=False for multi-threaded use by testclient
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def seed_activities(session: Session):
    # Mirror previous in-memory seed
    seeds = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        },
        "Basketball Team": {
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        },
        "Drama Club": {
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        },
        "Math Club": {
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
        },
    }

    for name, info in seeds.items():
        activity = Activity(
            name=name,
            description=info.get("description"),
            schedule=info.get("schedule"),
            max_participants=info.get("max_participants", 0),
        )
        session.add(activity)
        session.commit()
        session.refresh(activity)
        for email in info.get("participants", []):
            signup = Signup(activity_id=activity.id, email=email)
            session.add(signup)
        session.commit()
