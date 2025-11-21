import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Appointment, Service, Stylist, Review, Promotion, FAQ, GalleryItem, ContactMessage

app = FastAPI(title="HairWorx.co API", description="Backend API for HairWorx.co website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "HairWorx.co API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# --------- Helpers with graceful fallbacks ---------

def collection_list(name: str, placeholder: List[dict]):
    try:
        docs = get_documents(name)
        if docs:
            for d in docs:
                d["id"] = str(d.get("_id"))
                d.pop("_id", None)
            return docs
    except Exception:
        pass
    return placeholder


# --------- Placeholder Data ---------

PLACEHOLDER_SERVICES = [
    {"name": "Signature Cut & Finish", "description": "Precision cut, luxury cleanse, high-gloss finish.", "duration_minutes": 60, "price_from": 95.0, "category": "Cut & Style"},
    {"name": "Balayage Luminé", "description": "Hand-painted highlights for sunlit dimension.", "duration_minutes": 180, "price_from": 240.0, "category": "Color"},
    {"name": "Keratin Silk Infusion", "description": "Smoothing treatment for mirror-shine and control.", "duration_minutes": 150, "price_from": 280.0, "category": "Treatment"},
]

PLACEHOLDER_STYLISTS = [
    {"name": "Aria Bennett", "bio": "Creative Director. Editorial finishes and precision bobs.", "specialty": ["Cutting", "Editorial"], "photo_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1200&auto=format&fit=crop"},
    {"name": "Luca Romano", "bio": "Senior Colourist. Lived-in blondes and Italian brunettes.", "specialty": ["Balayage", "Color"], "photo_url": "https://images.unsplash.com/photo-1520975922203-b8807aabde6c?q=80&w=1200&auto=format&fit=crop"},
    {"name": "Maya Chen", "bio": "Treatment Specialist. Keratin and scalp wellness.", "specialty": ["Treatment", "Scalp"], "photo_url": "https://images.unsplash.com/photo-1607247130973-1eaba0e1ff55?q=80&w=1200&auto=format&fit=crop"},
]

PLACEHOLDER_REVIEWS = [
    {"name": "Sofia", "rating": 5, "comment": "Flawless service – my hair has never looked better.", "source": "Google"},
    {"name": "James", "rating": 5, "comment": "Luxury from start to finish. Highly recommend.", "source": "Google"},
    {"name": "Layla", "rating": 5, "comment": "Beautiful space, expert team, immaculate results.", "source": "Google"},
]

PLACEHOLDER_PROMOS = [
    {"title": "New Guest Welcome", "description": "Enjoy 15% off your first colour service.", "code": "WELCOME15"},
]

PLACEHOLDER_FAQS = [
    {"question": "Do you offer consultations?", "answer": "Yes, complimentary consultations are available for all services."},
    {"question": "What is your cancellation policy?", "answer": "We kindly ask for 24 hours' notice to reschedule or cancel."},
]

PLACEHOLDER_GALLERY = [
    {"image_url": "https://images.unsplash.com/photo-1514575114800-4eec5aadae06?q=80&w=1600&auto=format&fit=crop", "caption": "Balayage Luminé", "category": "Color"},
    {"image_url": "https://images.unsplash.com/photo-1503951458645-643d53bfd90f?q=80&w=1600&auto=format&fit=crop", "caption": "Classic Bob", "category": "Cut"},
    {"image_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1600&auto=format&fit=crop", "caption": "Runway Finish", "category": "Style"},
]


# --------- Public Content Endpoints ---------

@app.get("/api/services")
async def get_services():
    return collection_list("service", PLACEHOLDER_SERVICES)


@app.get("/api/stylists")
async def get_stylists():
    return collection_list("stylist", PLACEHOLDER_STYLISTS)


@app.get("/api/reviews")
async def get_reviews():
    return collection_list("review", PLACEHOLDER_REVIEWS)


@app.get("/api/promotions")
async def get_promotions():
    return collection_list("promotion", PLACEHOLDER_PROMOS)


@app.get("/api/faqs")
async def get_faqs():
    return collection_list("faq", PLACEHOLDER_FAQS)


@app.get("/api/gallery")
async def get_gallery():
    return collection_list("galleryitem", PLACEHOLDER_GALLERY)


# --------- Booking & Slots ---------

class SlotsQuery(BaseModel):
    service_id: Optional[str] = None
    stylist_id: Optional[str] = None
    date: str


@app.get("/api/slots")
async def get_slots(date: str, service_id: Optional[str] = None, stylist_id: Optional[str] = None):
    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    base_times = [10, 11, 12, 14, 15, 16, 17]
    slots = [f"{h:02d}:00" for h in base_times]
    # Placeholder logic to block some slots
    if day.weekday() in (5, 6):  # weekends fewer slots
        slots = [t for t in slots if t not in ("12:00", "16:00")]
    return {"date": date, "slots": slots}


@app.post("/api/appointments")
async def create_appointment(appt: Appointment):
    try:
        appt_id = create_document("appointment", appt)
        return {"status": "ok", "id": appt_id, "calendar_synced": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Contact ---------

@app.post("/api/contact")
async def contact(msg: ContactMessage):
    try:
        msg_id = create_document("contactmessage", msg)
        return {"status": "ok", "id": msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- AI Hair Diagnosis (Placeholder rules) ---------

class QuizInput(BaseModel):
    hair_type: str
    condition: str
    scalp: Optional[str] = None
    goals: List[str]
    past_treatments: Optional[List[str]] = None


@app.post("/api/quiz")
async def ai_quiz(data: QuizInput):
    # Very simple placeholder logic mapping to services
    recommendations = []
    if "frizz" in data.condition.lower() or "smooth" in " ".join(data.goals).lower():
        recommendations.append({
            "service": "Keratin Silk Infusion",
            "price_from": 280.0,
            "why": "Intensive smoothing to reduce frizz and add mirror-shine.",
        })
    if "volume" in " ".join(data.goals).lower():
        recommendations.append({
            "service": "Signature Cut & Finish",
            "price_from": 95.0,
            "why": "Precision shape tailored to enhance natural volume.",
        })
    if "colour" in data.goals or "color" in " ".join(data.goals).lower():
        recommendations.append({
            "service": "Balayage Luminé",
            "price_from": 240.0,
            "why": "Lived-in dimension with soft, seamless tones.",
        })

    if not recommendations:
        recommendations.append({
            "service": "Personalised Consultation",
            "price_from": 0.0,
            "why": "Meet your stylist to design a bespoke plan.",
        })

    return {
        "summary": "Curated for your hair profile.",
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
