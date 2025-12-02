from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.models.email_subscription import EmailSubscription

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


class SubscriptionCreate(BaseModel):
    email: EmailStr


class SubscriptionUpdate(BaseModel):
    email: EmailStr
    is_active: bool


class SubscriptionResponse(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Subscribe an email for event notifications"""
    # Check if email already exists
    existing = (
        db.query(EmailSubscription)
        .filter(EmailSubscription.email == subscription.email)
        .first()
    )

    if existing:
        # Reactivate if inactive
        if not existing.is_active:
            existing.is_active = True
            db.commit()
            db.refresh(existing)
        return existing

    # Create new subscription
    new_subscription = EmailSubscription(
        email=subscription.email,
        is_active=True
    )
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return new_subscription


@router.get("/{email}", response_model=SubscriptionResponse)
async def get_subscription(email: str, db: Session = Depends(get_db)):
    """Get subscription status for an email"""
    subscription = (
        db.query(EmailSubscription)
        .filter(EmailSubscription.email == email)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@router.put("/{email}", response_model=SubscriptionResponse)
async def update_subscription(
    email: str,
    update: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """Update subscription (change email or active status)"""
    subscription = (
        db.query(EmailSubscription)
        .filter(EmailSubscription.email == email)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update fields
    if update.email != email:
        # Check if new email already exists
        existing = (
            db.query(EmailSubscription)
            .filter(EmailSubscription.email == update.email)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Email already subscribed")
        subscription.email = update.email

    subscription.is_active = update.is_active

    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/{email}")
async def delete_subscription(email: str, db: Session = Depends(get_db)):
    """Unsubscribe an email"""
    subscription = (
        db.query(EmailSubscription)
        .filter(EmailSubscription.email == email)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Soft delete - just deactivate
    subscription.is_active = False
    db.commit()

    return {"message": "Successfully unsubscribed"}
