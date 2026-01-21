from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database import create_db_and_tables, get_session
from app.models import Squad, SquadMember, SquadRead
import uuid
from fastapi import Request
from fastapi.templating import Jinja2Templates

# Setup Templates Directory
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Create DB on Startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# --- CORE FEATURE: CREATE SQUAD ---
def parse_streamer_input(input_str: str):
    """
    Detects if input is a YouTube Link or Twitch Username.
    Returns tuple: (platform, clean_id)
    """
    if "youtube.com" in input_str or "youtu.be" in input_str:
        # Simple extraction for 'v=VIDEO_ID'
        # Input: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        try:
            if "v=" in input_str:
                return "youtube", input_str.split("v=")[1].split("&")[0]
            elif "youtu.be" in input_str:
                return "youtube", input_str.split("/")[-1]
        except:
            return "twitch", input_str # Fallback
    
    # Default to Twitch if it's just a name like "shroud"
    return "twitch", input_str
@app.post("/create", response_model=SquadRead)
def create_squad(title: str, usernames: list[str], session: Session = Depends(get_session)):
    slug = str(uuid.uuid4())[:8]
    
    new_squad = Squad(title=title, slug=slug)
    session.add(new_squad)
    session.commit()
    session.refresh(new_squad)
    
    for user_input in usernames:
        # Use the helper function to detect platform
        platform, clean_id = parse_streamer_input(user_input)
        
        member = SquadMember(
            platform=platform, 
            username=clean_id, 
            squad_id=new_squad.id
        )
        session.add(member)
    
    session.commit()
    session.refresh(new_squad)
    return new_squad

# --- CORE FEATURE: GET SQUAD ---
@app.get("/squad/{slug}")
def get_squad_html(request: Request, slug: str, session: Session = Depends(get_session)):
    # 1. Fetch data from DB
    statement = select(Squad).where(Squad.slug == slug)
    squad = session.exec(statement).first()
    
    if not squad:
        raise HTTPException(status_code=404, detail="Squad not found")
    
    # 2. Render HTML with the squad data
    return templates.TemplateResponse("squad.html", {
        "request": request, 
        "squad": squad
    })
