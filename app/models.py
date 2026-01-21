from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid

# 1. THE STREAMER (Member)
class SquadMember(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str  # "twitch" or "youtube"
    username: str  # e.g., "shroud"
    
    # Foreign Key to Squad
    squad_id: Optional[int] = Field(default=None, foreign_key="squad.id")
    squad: Optional["Squad"] = Relationship(back_populates="members")

# 2. THE SQUAD (Group)
class Squad(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True) # e.g., "a1b2-c3d4"
    title: str
    
    # Relationship
    members: List[SquadMember] = Relationship(back_populates="squad")

# 3. Pydantic Models (For API Responses)
class SquadRead(SQLModel):
    slug: str
    title: str
    members: List[SquadMember]