"""
Database Schemas for HairWorx.co

Each Pydantic model represents a MongoDB collection. The collection name is the lowercase
of the class name (e.g., Appointment -> "appointment").
"""
from __future__ import annotations
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Appointment(BaseModel):
    customer_name: str = Field(..., description="Full name of the customer")
    customer_email: Optional[EmailStr] = Field(None, description="Email for confirmations")
    customer_phone: Optional[str] = Field(None, description="Phone for WhatsApp/SMS reminders")
    service_id: str = Field(..., description="Selected service id")
    service_name: str = Field(..., description="Selected service name")
    stylist_id: Optional[str] = Field(None, description="Selected stylist id")
    stylist_name: Optional[str] = Field(None, description="Selected stylist name")
    date: str = Field(..., description="Date string YYYY-MM-DD")
    time: str = Field(..., description="Time string HH:MM")
    notes: Optional[str] = Field(None, description="Additional notes")
    price: Optional[float] = Field(None, ge=0, description="Expected price at time of booking")
    source: str = Field("web", description="Booking source")
    calendar_synced: bool = Field(False, description="Whether synced to Google Calendar")
    reminder_method: Optional[str] = Field(None, description="email | whatsapp | sms")

class Service(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=15, le=300)
    price_from: float = Field(..., ge=0)
    category: Optional[str] = None

class Stylist(BaseModel):
    name: str
    bio: Optional[str] = None
    specialty: Optional[List[str]] = None
    photo_url: Optional[str] = None
    rating: Optional[float] = Field(4.9, ge=0, le=5)

class Review(BaseModel):
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    source: str = Field("Google", description="Review platform")
    date: Optional[datetime] = None

class Promotion(BaseModel):
    title: str
    description: Optional[str] = None
    code: Optional[str] = None
    valid_until: Optional[str] = None
    image_url: Optional[str] = None

class FAQ(BaseModel):
    question: str
    answer: str

class GalleryItem(BaseModel):
    image_url: str
    caption: Optional[str] = None
    category: Optional[str] = None

class ContactMessage(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    message: str
