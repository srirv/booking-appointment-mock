from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Path
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, time, datetime, timedelta
import random
import string
import logging
import traceback
import re

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

# Configure logger
logger = logging.getLogger(__name__)

# Create a router specifically for fixed paths (no path parameters)
fixed_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

# Create a router for single-segment parameterized paths (like /{id})
router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

# Create a router for multi-segment parameterized paths (like /{id}/action)
nested_router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@fixed_router.get("/", response_model=List[Appointment])
def get_all_appointments(request: Request, db: Session = Depends(get_db)):
    logger.info(f"Getting all appointments - Client: {request.client.host}")
    try:
        appointments = db.query(AppointmentModel).all()
        logger.debug(f"Retrieved {len(appointments)} appointments")
        return appointments
    except Exception as e:
        logger.error(f"Error fetching appointments: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

# Define specific routes with fixed paths in the fixed_router
@fixed_router.get("/availability", response_model=AppointmentAvailabilityResponse)
def get_appointment_availability(request: Request, appointmentDate: date = Query(...), db: Session = Depends(get_db)):
    logger.info(f"Checking appointment availability for date: {appointmentDate} - Client: {request.client.host}")
    try:
        # Check if there are slots available on the requested date
        logger.debug(f"Querying appointments for date {appointmentDate}")
        existing_appointments = db.query(AppointmentModel).filter(
            AppointmentModel.date == appointmentDate
        ).count()
        logger.debug(f"Found {existing_appointments} existing appointments for date {appointmentDate}")
        
        # Assuming a maximum of 10 appointments per day for simplicity
        slots_available = existing_appointments < 10
        logger.debug(f"Slots available: {slots_available}")
        
        # For demo purposes, return some mock data
        if slots_available:
            # Return first available time (9 AM + existing appointments hours)
            appointment_time = time(9 + existing_appointments, 0, 0)
            logger.debug(f"Next available time: {appointment_time}")
            return {
                "slotAvailable": True,
                "appointmentTime": appointment_time,
                "doctorName": "Dr. Priya Sharma"
            }
        else:
            # Return next available slot (next day)
            next_date = appointmentDate + timedelta(days=1)
            next_slot = datetime.combine(next_date, time(9, 0, 0))
            logger.debug(f"Next available slot: {next_slot}")
            return {
                "slotAvailable": False,
                "nextAvailableSlot": next_slot,
                "doctorName": "Dr. Priya Sharma"
            }
    except Exception as e:
        logger.error(f"Error checking appointment availability: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to check appointment availability")

@fixed_router.get("/booking-details", response_model=BookingDetailsResponse)
def get_booking_details(
    request: Request,
    appointmentNumber: str = Query(..., regex=r'^\d{6}$'),
    db: Session = Depends(get_db)
):
    logger.info(f"Getting booking details for appointment number: {appointmentNumber} - Client: {request.client.host}")
    try:
        # Look up the appointment by appointmentId (which is now our appointmentNumber)
        logger.debug(f"Querying appointment with ID {appointmentNumber}")
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.appointmentId == appointmentNumber
        ).first()
        
        if appointment:
            logger.debug(f"Found appointment: {appointment}")
            return {
                "appointmentDate": appointment.date,
                "appointmentNumber": appointment.appointmentId,
                "appointmentTime": appointment.time,
                "userPhoneNumber": appointment.userPhoneNumber,
                "userName": appointment.name
            }
        
        logger.warning(f"Booking not found for appointment number {appointmentNumber}")
        raise HTTPException(status_code=404, detail="Booking not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking details: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to get booking details")

@fixed_router.get("/details", response_model=AppointmentUserDetailsResponse)
def get_appointment_by_phone(request: Request, userPhoneNumber: str = Query(...), db: Session = Depends(get_db)):
    logger.info(f"Getting appointment details for phone number: {userPhoneNumber} - Client: {request.client.host}")
    try:
        # Look up appointment by phone number
        logger.debug(f"Querying appointments for phone number {userPhoneNumber}")
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.userPhoneNumber == userPhoneNumber,
            AppointmentModel.isCancelled == False
        ).first()
        
        if appointment:
            logger.debug(f"Found appointment for phone number {userPhoneNumber}: {appointment}")
            return {
                "appointmentAvailable": True,
                "appointmentNumber": appointment.appointmentId,
                "userName": appointment.name,
                "appointmentDate": appointment.date,
                "appointmentTime": appointment.time
            }
        
        logger.debug(f"No active appointments found for phone number {userPhoneNumber}")
        return {
            "appointmentAvailable": False
        }
    except Exception as e:
        logger.error(f"Error getting appointment by phone: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to get appointment details")

# Routes with single path parameters go in the regular router
@router.get("/{appointmentId}", response_model=Appointment)
def get_appointment_by_id(
    request: Request, 
    appointmentId: str = Path(..., regex=r'^\d{6}$', description="The 6-digit appointment ID"), 
    db: Session = Depends(get_db)
):
    logger.info(f"Getting appointment by ID: {appointmentId} - Client: {request.client.host}")
    try:
        appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
        if appointment is None:
            logger.warning(f"Appointment with ID {appointmentId} not found")
            raise HTTPException(status_code=404, detail="Appointment not found")
        logger.debug(f"Retrieved appointment: {appointment}")
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment by ID: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@fixed_router.post("/", response_model=Appointment, status_code=status.HTTP_201_CREATED)
def create_appointment(request: Request, appointment: AppointmentCreateRequest, db: Session = Depends(get_db)):
    logger.info(f"Creating appointment for patient: {appointment.name} - Client: {request.client.host}")
    try:
        # Delete any existing appointments for this patient
        existing_appointments = db.query(AppointmentModel).filter(
            AppointmentModel.patientId == appointment.patientId
        ).all()
        
        if existing_appointments:
            logger.debug(f"Found {len(existing_appointments)} existing appointments for patient ID {appointment.patientId}")
            for existing_appointment in existing_appointments:
                logger.debug(f"Deleting appointment {existing_appointment.appointmentId} for patient {appointment.patientId}")
                db.delete(existing_appointment)
            db.commit()
        
        # Create new appointment
        logger.debug(f"Creating new appointment for patient {appointment.patientId} on {appointment.date} at {appointment.time}")
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
        logger.info(f"Appointment created successfully with ID: {db_appointment.appointmentId}")
        return db_appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        logger.debug(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create appointment")

@router.patch("/{appointmentId}", response_model=Appointment)
def patch_appointment(
    request: Request, 
    appointmentId: str = Path(..., regex=r'^\d{6}$'), 
    appointment: AppointmentPatchRequest = None, 
    db: Session = Depends(get_db)
):
    logger.info(f"Partially updating appointment with ID: {appointmentId} - Client: {request.client.host}")
    try:
        db_appointment = db.query(AppointmentModel).filter(AppointmentModel.appointmentId == appointmentId).first()
        if db_appointment is None:
            logger.warning(f"Appointment with ID {appointmentId} not found for patch")
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update only provided fields
        logger.debug(f"Partially updating fields for appointment {appointmentId}")
        update_data = appointment.dict(exclude_unset=True)
        logger.debug(f"Fields to update: {list(update_data.keys())}")
        for key, value in update_data.items():
            if value is not None:
                logger.debug(f"Setting {key} = {value}")
                setattr(db_appointment, key, value)
        
        db.commit()
        db.refresh(db_appointment)
        logger.info(f"Appointment {appointmentId} patched successfully")
        return db_appointment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching appointment: {str(e)}")
        logger.debug(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to patch appointment")

# Multi-segment paths go in the nested_router
@nested_router.get("/{appointmentNumber}/reschedule", response_model=RescheduleDetailsResponse)
def get_reschedule_details(
    request: Request,
    appointmentNumber: str = Path(..., regex=r'^\d{6}$'),
    userValidated: bool = Query(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Checking reschedule availability for appointment: {appointmentNumber}, validated: {userValidated} - Client: {request.client.host}")
    try:
        if not userValidated:
            logger.warning(f"User not validated for appointment {appointmentNumber}")
            raise HTTPException(status_code=400, detail="User not validated")
        
        # Check if appointment exists and is not cancelled
        logger.debug(f"Querying appointment with ID {appointmentNumber}")
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.appointmentId == appointmentNumber,
            AppointmentModel.isCancelled == False
        ).first()
        
        if not appointment:
            logger.warning(f"Appointment with ID {appointmentNumber} not found or is cancelled")
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.debug(f"Appointment {appointmentNumber} is available for reschedule")
        return {
            "rescheduleAvailable": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking reschedule availability: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to check reschedule availability")

@nested_router.get("/{appointmentNumber}/cancellation", response_model=CancellationDetailsResponse)
def get_cancellation_details(
    request: Request,
    appointmentNumber: str = Path(..., regex=r'^\d{6}$'),
    userValidated: bool = Query(...),
    db: Session = Depends(get_db)
):
    logger.info(f"Checking cancellation status for appointment: {appointmentNumber}, validated: {userValidated} - Client: {request.client.host}")
    try:
        if not userValidated:
            logger.warning(f"User not validated for appointment {appointmentNumber}")
            raise HTTPException(status_code=400, detail="User not validated")
        
        # Check if appointment exists
        logger.debug(f"Querying appointment with ID {appointmentNumber}")
        appointment = db.query(AppointmentModel).filter(
            AppointmentModel.appointmentId == appointmentNumber
        ).first()
        
        if not appointment:
            logger.warning(f"Appointment with ID {appointmentNumber} not found")
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.debug(f"Appointment {appointmentNumber} cancellation status: {appointment.isCancelled}")
        return {
            "appointmentCancelled": appointment.isCancelled
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking cancellation status: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to check cancellation status")

# Create a separate router for authentication
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/send-otp", response_model=OtpResponse)
def send_otp(request: Request, otp_request: OtpRequest):
    logger.info(f"Sending OTP to phone number: {otp_request.userPhoneNumber} - Client: {request.client.host}")
    try:
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        logger.debug(f"Generated OTP for phone number {otp_request.userPhoneNumber}: {otp}")
        
        # In a real application, you would send this OTP to the user's phone number
        # For demo purposes, just return the OTP
        logger.info(f"OTP sent successfully to {otp_request.userPhoneNumber}")
        return {
            "sentOtp": otp
        }
    except Exception as e:
        logger.error(f"Error sending OTP: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send OTP")

# Create a separate router for notifications
notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notifications_router.post("/sms/booking", response_model=SmsResponse)
def send_sms_booking_details(request: Request, sms_request: SmsBookingRequest):
    logger.info(f"Sending booking SMS to {sms_request.userPhoneNumber} for {sms_request.appointmentDate} - Client: {request.client.host}")
    try:
        # In a real application, you would send an SMS with the booking details
        # For demo purposes, just return success
        logger.debug(f"SMS content would include: date={sms_request.appointmentDate}, time={sms_request.appointmentTime}, doctor={sms_request.doctorName}")
        logger.info(f"Booking SMS sent successfully to {sms_request.userPhoneNumber}")
        return {
            "smsSent": True
        }
    except Exception as e:
        logger.error(f"Error sending booking SMS: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send booking SMS")

@notifications_router.post("/sms/cancellation", response_model=SmsResponse)
def send_sms_cancellation_details(request: Request, sms_request: SmsCancellationRequest):
    logger.info(f"Sending cancellation SMS to {sms_request.userPhoneNumber} for {sms_request.appointmentDate} - Client: {request.client.host}")
    try:
        # In a real application, you would send an SMS with the cancellation details
        # For demo purposes, just return success
        logger.debug(f"Cancellation SMS content would include: date={sms_request.appointmentDate}, time={sms_request.appointmentTime}")
        logger.info(f"Cancellation SMS sent successfully to {sms_request.userPhoneNumber}")
        return {
            "smsSent": True
        }
    except Exception as e:
        logger.error(f"Error sending cancellation SMS: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send cancellation SMS")

@notifications_router.post("/sms/reschedule", response_model=SmsResponse)
def send_sms_reschedule_details(request: Request, sms_request: SmsRescheduleRequest):
    logger.info(f"Sending reschedule SMS to {sms_request.userPhoneNumber} for {sms_request.appointmentDate} - Client: {request.client.host}")
    try:
        # In a real application, you would send an SMS with the rescheduled details
        # For demo purposes, just return success
        logger.debug(f"Reschedule SMS content would include: date={sms_request.appointmentDate}, time={sms_request.appointmentTime}")
        logger.info(f"Reschedule SMS sent successfully to {sms_request.userPhoneNumber}")
        return {
            "smsSent": True
        }
    except Exception as e:
        logger.error(f"Error sending reschedule SMS: {str(e)}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send reschedule SMS") 