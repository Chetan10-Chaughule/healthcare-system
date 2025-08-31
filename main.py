# main.py - FastAPI Backend for Healthcare Management System

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uuid
import json

app = FastAPI(title="Healthcare Management System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security
security = HTTPBearer()

# Pydantic Models
class User(BaseModel):
    id: str
    email: str
    password: str
    name: str
    user_type: str  # 'patient' or 'doctor'

class Patient(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    date_of_birth: date
    address: str
    blood_group: str
    emergency_contact: str

class Doctor(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    specialization: str
    qualification: str
    experience_years: int

class MedicalRecord(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    visit_date: date
    diagnosis: str
    treatment: str
    prescription: str
    notes: str

class Appointment(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: str
    status: str  # 'scheduled', 'completed', 'cancelled'
    reason: str

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    date_of_birth: str
    address: str
    blood_group: str
    emergency_contact: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AppointmentRequest(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_date: str
    appointment_time: str
    reason: str

# In-memory database (in production, use a real database)
users_db = {}
patients_db = {}
doctors_db = {}
medical_records_db = {}
appointments_db = {}
current_sessions = {}

# Initialize sample data
def initialize_data():
    # Sample Doctors with Indian names
    doctors = [
        {
            "id": "doc1",
            "name": "Dr. Rajesh Sharma",
            "email": "rajesh.sharma@hospital.com",
            "phone": "+91-9876543210",
            "specialization": "Cardiology",
            "qualification": "MD, DM Cardiology",
            "experience_years": 15
        },
        {
            "id": "doc2",
            "name": "Dr. Priya Patel",
            "email": "priya.patel@hospital.com",
            "phone": "+91-9876543211",
            "specialization": "Pediatrics",
            "qualification": "MBBS, MD Pediatrics",
            "experience_years": 10
        },
        {
            "id": "doc3",
            "name": "Dr. Amit Kumar",
            "email": "amit.kumar@hospital.com",
            "phone": "+91-9876543212",
            "specialization": "Orthopedics",
            "qualification": "MBBS, MS Orthopedics",
            "experience_years": 12
        },
        {
            "id": "doc4",
            "name": "Dr. Sunita Rao",
            "email": "sunita.rao@hospital.com",
            "phone": "+91-9876543213",
            "specialization": "Gynecology",
            "qualification": "MBBS, MD Gynecology",
            "experience_years": 8
        }
    ]
    
    # Sample Patients
    patients = [
        {
            "id": "pat1",
            "name": "Arjun Mehta",
            "email": "arjun.mehta@email.com",
            "phone": "+91-9876543220",
            "date_of_birth": "1990-05-15",
            "address": "Mumbai, Maharashtra",
            "blood_group": "A+",
            "emergency_contact": "+91-9876543221"
        },
        {
            "id": "pat2",
            "name": "Kavya Singh",
            "email": "kavya.singh@email.com",
            "phone": "+91-9876543222",
            "date_of_birth": "1985-08-22",
            "address": "Delhi, India",
            "blood_group": "O+",
            "emergency_contact": "+91-9876543223"
        }
    ]
    
    # Sample Users (login credentials)
    sample_users = [
        {"id": "doc1", "email": "rajesh.sharma@hospital.com", "password": "doc123", "name": "Dr. Rajesh Sharma", "user_type": "doctor"},
        {"id": "doc2", "email": "priya.patel@hospital.com", "password": "doc123", "name": "Dr. Priya Patel", "user_type": "doctor"},
        {"id": "doc3", "email": "amit.kumar@hospital.com", "password": "doc123", "name": "Dr. Amit Kumar", "user_type": "doctor"},
        {"id": "doc4", "email": "sunita.rao@hospital.com", "password": "doc123", "name": "Dr. Sunita Rao", "user_type": "doctor"},
        {"id": "pat1", "email": "arjun.mehta@email.com", "password": "pat123", "name": "Arjun Mehta", "user_type": "patient"},
        {"id": "pat2", "email": "kavya.singh@email.com", "password": "pat123", "name": "Kavya Singh", "user_type": "patient"}
    ]
    
    # Sample Medical Records
    medical_records = [
        {
            "id": "rec1",
            "patient_id": "pat1",
            "doctor_id": "doc1",
            "visit_date": "2024-01-15",
            "diagnosis": "Hypertension",
            "treatment": "Lifestyle changes and medication",
            "prescription": "Amlodipine 5mg once daily",
            "notes": "Patient advised to reduce salt intake and exercise regularly"
        },
        {
            "id": "rec2",
            "patient_id": "pat1",
            "doctor_id": "doc3",
            "visit_date": "2024-02-20",
            "diagnosis": "Lower back pain",
            "treatment": "Physiotherapy and pain management",
            "prescription": "Ibuprofen 400mg twice daily",
            "notes": "Recommended ergonomic workplace setup"
        },
        {
            "id": "rec3",
            "patient_id": "pat2",
            "doctor_id": "doc2",
            "visit_date": "2024-01-10",
            "diagnosis": "Routine checkup",
            "treatment": "No treatment required",
            "prescription": "Multivitamin supplements",
            "notes": "Patient in good health, continue regular checkups"
        }
    ]
    
    # Sample Appointments
    appointments = [
        {
            "id": "app1",
            "patient_id": "pat1",
            "doctor_id": "doc1",
            "appointment_date": "2024-08-25",
            "appointment_time": "10:00",
            "status": "scheduled",
            "reason": "Follow-up for hypertension"
        },
        {
            "id": "app2",
            "patient_id": "pat2",
            "doctor_id": "doc2",
            "appointment_date": "2024-08-26",
            "appointment_time": "14:00",
            "status": "scheduled",
            "reason": "Annual health checkup"
        }
    ]
    
    # Populate databases
    for user in sample_users:
        users_db[user["email"]] = user
    
    for doctor in doctors:
        doctors_db[doctor["id"]] = doctor
    
    for patient in patients:
        patients_db[patient["id"]] = patient
    
    for record in medical_records:
        medical_records_db[record["id"]] = record
    
    for appointment in appointments:
        appointments_db[appointment["id"]] = appointment

# Initialize data on startup
initialize_data()

# Authentication helper
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in current_sessions:
        raise HTTPException(status_code=401, detail="Invalid token")
    return current_sessions[token]

# Add explicit OPTIONS handler for all routes
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

# API Endpoints

@app.post("/signup")
async def signup(signup_data: SignupRequest):
    # Check if user already exists
    if signup_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate unique IDs
    patient_id = f"pat{len(patients_db) + 1}"
    
    # Create new user
    new_user = {
        "id": patient_id,
        "email": signup_data.email,
        "password": signup_data.password,  # In production, hash this password
        "name": signup_data.name,
        "user_type": "patient"
    }
    
    # Create new patient
    new_patient = {
        "id": patient_id,
        "name": signup_data.name,
        "email": signup_data.email,
        "phone": signup_data.phone,
        "date_of_birth": signup_data.date_of_birth,
        "address": signup_data.address,
        "blood_group": signup_data.blood_group,
        "emergency_contact": signup_data.emergency_contact
    }
    
    # Save to databases
    users_db[signup_data.email] = new_user
    patients_db[patient_id] = new_patient
    
    return {"message": "Account created successfully", "patient_id": patient_id}

@app.post("/login")
async def login(login_data: LoginRequest):
    user = users_db.get(login_data.email)
    if not user or user["password"] != login_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate session token
    token = str(uuid.uuid4())
    current_sessions[token] = user
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "user_type": user["user_type"]
        }
    }

@app.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # Remove session (in a real app, you'd get the token from the request)
    return {"message": "Logged out successfully"}

@app.get("/doctors")
async def get_doctors():
    return list(doctors_db.values())

@app.get("/patients")
async def get_patients(current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")
    return list(patients_db.values())

@app.get("/patient/{patient_id}")
async def get_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    patient = patients_db.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/medical-records/{patient_id}")
async def get_medical_records(patient_id: str, current_user: dict = Depends(get_current_user)):
    # Patients can only see their own records, doctors can see records of their patients
    if current_user["user_type"] == "patient" and current_user["id"] != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    records = []
    for record in medical_records_db.values():
        if record["patient_id"] == patient_id:
            # Add doctor information to the record
            doctor = doctors_db.get(record["doctor_id"])
            record_with_doctor = record.copy()
            record_with_doctor["doctor_name"] = doctor["name"] if doctor else "Unknown"
            record_with_doctor["doctor_specialization"] = doctor["specialization"] if doctor else "Unknown"
            records.append(record_with_doctor)
    
    return records

@app.get("/doctor-patients/{doctor_id}")
async def get_doctor_patients(doctor_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "doctor" or current_user["id"] != doctor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get unique patient IDs from medical records for this doctor
    patient_ids = set()
    for record in medical_records_db.values():
        if record["doctor_id"] == doctor_id:
            patient_ids.add(record["patient_id"])
    
    patients = []
    for patient_id in patient_ids:
        patient = patients_db.get(patient_id)
        if patient:
            patients.append(patient)
    
    return patients

@app.get("/appointments")
async def get_appointments(current_user: dict = Depends(get_current_user)):
    user_appointments = []
    for appointment in appointments_db.values():
        if ((current_user["user_type"] == "patient" and appointment["patient_id"] == current_user["id"]) or
            (current_user["user_type"] == "doctor" and appointment["doctor_id"] == current_user["id"])):
            
            # Add patient and doctor names to appointment
            appointment_with_names = appointment.copy()
            patient = patients_db.get(appointment["patient_id"])
            doctor = doctors_db.get(appointment["doctor_id"])
            appointment_with_names["patient_name"] = patient["name"] if patient else "Unknown"
            appointment_with_names["doctor_name"] = doctor["name"] if doctor else "Unknown"
            appointment_with_names["doctor_specialization"] = doctor["specialization"] if doctor else "Unknown"
            user_appointments.append(appointment_with_names)
    
    return user_appointments

@app.post("/appointments")
async def create_appointment(appointment_data: AppointmentRequest, current_user: dict = Depends(get_current_user)):
    if current_user["user_type"] != "patient":
        raise HTTPException(status_code=403, detail="Only patients can book appointments")
    
    appointment_id = str(uuid.uuid4())
    new_appointment = {
        "id": appointment_id,
        "patient_id": appointment_data.patient_id,
        "doctor_id": appointment_data.doctor_id,
        "appointment_date": appointment_data.appointment_date,
        "appointment_time": appointment_data.appointment_time,
        "status": "scheduled",
        "reason": appointment_data.reason
    }
    
    appointments_db[appointment_id] = new_appointment
    return {"message": "Appointment created successfully", "appointment_id": appointment_id}

@app.get("/facility-info")
async def get_facility_info():
    return {
        "hospital_name": "MedCare Hospital & Research Center",
        "tagline": "Your Health, Our Priority",
        "description": "A leading healthcare institution committed to providing world-class medical care with cutting-edge technology and compassionate service.",
        "services": [
            {
                "name": "Emergency Care",
                "description": "24/7 emergency medical services with state-of-the-art trauma center",
                "icon": "🚑"
            },
            {
                "name": "Specialized Treatments",
                "description": "Expert care in Cardiology, Pediatrics, Orthopedics, and Gynecology",
                "icon": "🏥"
            },
            {
                "name": "Diagnostic Services",
                "description": "Advanced imaging, laboratory tests, and health screenings",
                "icon": "🔬"
            },
            {
                "name": "Telemedicine",
                "description": "Virtual consultations and remote patient monitoring",
                "icon": "💻"
            },
            {
                "name": "Pharmacy Services",
                "description": "Complete pharmaceutical care and medication management",
                "icon": "💊"
            },
            {
                "name": "Wellness Programs",
                "description": "Preventive care, health education, and lifestyle counseling",
                "icon": "🌟"
            }
        ],
        "stats": [
            {"label": "Years of Excellence", "value": "25+", "icon": "⭐"},
            {"label": "Expert Doctors", "value": "50+", "icon": "👨‍⚕️"},
            {"label": "Patients Served", "value": "100K+", "icon": "👥"},
            {"label": "Success Rate", "value": "98%", "icon": "📈"}
        ],
        "contact_info": {
            "address": "123 Health Street, Medical District, Mumbai, Maharashtra 400001",
            "phone": "+91-22-2345-6789",
            "emergency": "+91-22-2345-6790",
            "email": "info@medcare.com",
            "hours": {
                "opd": "8:00 AM - 8:00 PM",
                "emergency": "24/7",
                "pharmacy": "24/7"
            }
        },
        "specializations": [
            {"name": "Cardiology", "doctor": "Dr. Rajesh Sharma"},
            {"name": "Pediatrics", "doctor": "Dr. Priya Patel"},
            {"name": "Orthopedics", "doctor": "Dr. Amit Kumar"},
            {"name": "Gynecology", "doctor": "Dr. Sunita Rao"}
        ]
    }
@app.get("/facility-info")
async def get_facility_info():
    return {
        "hospital_name": "MedCare Hospital & Research Center",
        "tagline": "Your Health, Our Priority",
        "description": "A leading healthcare institution committed to providing world-class medical care with cutting-edge technology and compassionate service.",
        "services": [
            {
                "name": "Emergency Care",
                "description": "24/7 emergency medical services with state-of-the-art trauma center",
                "icon": "🚑"
            },
            {
                "name": "Specialized Treatments",
                "description": "Expert care in Cardiology, Pediatrics, Orthopedics, and Gynecology",
                "icon": "🏥"
            },
            {
                "name": "Diagnostic Services",
                "description": "Advanced imaging, laboratory tests, and health screenings",
                "icon": "🔬"
            },
            {
                "name": "Telemedicine",
                "description": "Virtual consultations and remote patient monitoring",
                "icon": "💻"
            },
            {
                "name": "Pharmacy Services",
                "description": "Complete pharmaceutical care and medication management",
                "icon": "💊"
            },
            {
                "name": "Wellness Programs",
                "description": "Preventive care, health education, and lifestyle counseling",
                "icon": "🌟"
            }
        ],
        "stats": [
            {"label": "Years of Excellence", "value": "25+", "icon": "⭐"},
            {"label": "Expert Doctors", "value": "50+", "icon": "👨‍⚕️"},
            {"label": "Patients Served", "value": "100K+", "icon": "👥"},
            {"label": "Success Rate", "value": "98%", "icon": "📈"}
        ],
        "contact_info": {
            "address": "123 Health Street, Medical District, Mumbai, Maharashtra 400001",
            "phone": "+91-22-2345-6789",
            "emergency": "+91-22-2345-6790",
            "email": "info@medcare.com",
            "hours": {
                "opd": "8:00 AM - 8:00 PM",
                "emergency": "24/7",
                "pharmacy": "24/7"
            }
        },
        "specializations": [
            {"name": "Cardiology", "doctor": "Dr. Rajesh Sharma"},
            {"name": "Pediatrics", "doctor": "Dr. Priya Patel"},
            {"name": "Orthopedics", "doctor": "Dr. Amit Kumar"},
            {"name": "Gynecology", "doctor": "Dr. Sunita Rao"}
        ]
    }

@app.get("/")
async def root():
    return {"message": "Healthcare Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# To run the server, save this file as main.py and run:
# pip install fastapi uvicorn
# uvicorn main:app --reload