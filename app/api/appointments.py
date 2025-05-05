from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta
import random
import string

from app.models.appointment import Appointment as AppointmentModel
from app.schemas.appointment import (
    Appointment, 
    AppointmentCreateRequest, 
    AppointmentUpdateRequest, 
    AppointmentPatchRequest,
    AppointmentAvailabilityResponse,
    BookingDetailsResponse,
    AppointmentUserDetailsResponse,
    OtpRequest,
    OtpResponse,
    RescheduleDetailsResponse,
    CancellationDetailsResponse,
    SmsBookingRequest,
    SmsCancellationRequest,
    SmsRescheduleRequest,
    SmsResponse
)
from app.db.base import get_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@router.get("/", response_model=List[Appointment])
def get_all_appointments(db: Session = Depends(get_db)):
    appointments = db.query(AppointmentModel).all()
    return appointments

@router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(appointment: AppointmentCreateRequest, db: Session = Depends(get_db)):
    # Delete any existing appointments for this patient
    existing_appointments = db.query(AppointmentModel).filter(
        AppointmentModel.patientId == appointment.patientId
    ).all()
    
    if existing_appointments:
        for existing_appointment in existing_appointments:
            db.delete(existing_appointment)
        db.commit()
    
    # Create new appointment
    db_appointment = AppointmentModel(
        appointmentId=AppointmentModel.generate_id(),
        patientId=appointment.patientId,
        name=appointment.name,
        date=appointment.date,
        time=appointment.time,
        department=appointment.department,
        doctorName=appointment.doctorName,
        userPhoneNumber=appointment.userPhoneNumber,
        isCancelled=False
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/{appointmentId}", response_model=Appointment)
def get_appointment_by_id(appointmentId: str, db: Session = Depends(get_db)):
    appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.put("/{appointmentId}", response_model=Appointment)
def update_appointment(appointmentId: str, appointment: AppointmentUpdateRequest, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update all fields
    update_data = appointment.dict()
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.patch("/{appointmentId}", response_model=Appointment)
def patch_appointment(appointmentId: str, appointment: AppointmentPatchRequest, db: Session = Depends(get_db)):
    db_appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Update only provided fields
    update_data = appointment.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# New endpoints based on OpenAPI spec
@router.get("/availability", response_model=AppointmentAvailabilityResponse)
def get_appointment_availability(appointmentDate: date = Query(...), db: Session = Depends(get_db)):
    # Check if there are slots available on the requested date
    existing_appointments = db.query(AppointmentModel).filter(
        AppointmentModel.date == appointmentDate
    ).count()
    
    # Assuming a maximum of 10 appointments per day for simplicity
    slots_available = existing_appointments < 10
    
    # For demo purposes, return some mock data
    if slots_available:
        # Return first available time (9 AM + existing appointments hours)
        appointment_time = time(9 + existing_appointments, 0, 0)
        return {
            "slotAvailable": True,
            "appointmentTime": appointment_time,
            "doctorName": "Dr. Priya Sharma"
        }
    else:
        # Return next available slot (next day)
        next_date = appointmentDate + timedelta(days=1)
        next_slot = datetime.combine(next_date, time(9, 0, 0))
        return {
            "slotAvailable": False,
            "nextAvailableSlot": next_slot,
            "doctorName": "Dr. Priya Sharma"
        }

@router.get("/booking-details", response_model=BookingDetailsResponse)
def get_booking_details(
    appointmentNumber: str = Query(..., regex=r'^\d{6}$'),
    db: Session = Depends(get_db)
):
    # Look up the appointment by appointmentId (which is now our appointmentNumber)
    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.appointmentId == appointmentNumber
    ).first()
    
    if appointment:
        return {
            "appointmentDate": appointment.date,
            "appointmentNumber": appointment.appointmentId,
            "appointmentTime": appointment.time,
            "userPhoneNumber": appointment.userPhoneNumber,
            "userName": appointment.name
        }
    
    raise HTTPException(status_code=404, detail="Booking not found")

@router.get("/details", response_model=AppointmentUserDetailsResponse)
def get_appointment_by_phone(userPhoneNumber: str = Query(...), db: Session = Depends(get_db)):
    # Look up appointment by phone number
    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.userPhoneNumber == userPhoneNumber,
        AppointmentModel.isCancelled == False
    ).first()
    
    if appointment:
        return {
            "appointmentAvailable": True,
            "appointmentNumber": appointment.appointmentId,
            "userName": appointment.name,
            "appointmentDate": appointment.date,
            "appointmentTime": appointment.time
        }
    
    return {
        "appointmentAvailable": False
    }

@router.get("/{appointmentNumber}/reschedule", response_model=RescheduleDetailsResponse)
def get_reschedule_details(
    appointmentNumber: str,
    userValidated: bool = Query(...),
    db: Session = Depends(get_db)
):
    if not userValidated:
        raise HTTPException(status_code=400, detail="User not validated")
    
    # Check if appointment exists and is not cancelled
    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.appointmentId == appointmentNumber,
        AppointmentModel.isCancelled == False
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "rescheduleAvailable": True
    }

@router.get("/{appointmentNumber}/cancellation", response_model=CancellationDetailsResponse)
def get_cancellation_details(
    appointmentNumber: str,
    userValidated: bool = Query(...),
    db: Session = Depends(get_db)
):
    if not userValidated:
        raise HTTPException(status_code=400, detail="User not validated")
    
    # Check if appointment exists
    appointment = db.query(AppointmentModel).filter(
        AppointmentModel.appointmentId == appointmentNumber
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return {
        "appointmentCancelled": appointment.isCancelled
    }

# Create a separate router for authentication
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/send-otp", response_model=OtpResponse)
def send_otp(otp_request: OtpRequest):
    # Generate a random 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # In a real application, you would send this OTP to the user's phone number
    # For demo purposes, just return the OTP
    return {
        "sentOtp": otp
    }

# Create a separate router for notifications
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notifications_router.post("/sms/booking", response_model=SmsResponse)
def send_sms_booking_details(sms_request: SmsBookingRequest):
    # In a real application, you would send an SMS with the booking details
    # For demo purposes, just return success
    return {
        "smsSent": True
    }

@notifications_router.post("/sms/cancellation", response_model=SmsResponse)
def send_sms_cancellation_details(sms_request: SmsCancellationRequest):
    # In a real application, you would send an SMS with the cancellation details
    # For demo purposes, just return success
    return {
        "smsSent": True
    }

@notifications_router.post("/sms/reschedule", response_model=SmsResponse)
def send_sms_reschedule_details(sms_request: SmsRescheduleRequest):
    # In a real application, you would send an SMS with the rescheduled details
    # For demo purposes, just return success
    return {
        "smsSent": True
    } 