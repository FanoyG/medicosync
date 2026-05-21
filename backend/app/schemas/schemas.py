import uuid
from pydantic import BaseModel, EmailStr, Field, computed_field
from datetime import datetime, date
from enum import Enum


# ─── Enums ────────────────────────────────────────────────

class RecordType(str, Enum):
    lab   = "lab"
    visit = "visit"
    xray  = "xray"
    image = "image"
    other = "other"

class Gender(str, Enum):
    male   = "male"
    female = "female"
    other  = "other"


# ─── Auth ─────────────────────────────────────────────────

class UserRegister(BaseModel):
    email     : EmailStr
    password  : str      = Field(min_length=6)
    full_name : str      = Field(min_length=2)
    specialty : str | None = None

class UserLogin(BaseModel):
    email    : EmailStr
    password : str

class TokenOut(BaseModel):
    access_token : str
    token_type   : str = "bearer"

class UserOut(BaseModel):
    id         : uuid.UUID
    email      : str
    full_name  : str
    specialty  : str | None
    is_active  : bool
    created_at : datetime

    model_config = {"from_attributes": True}


# ─── Patient ──────────────────────────────────────────────

class PatientCreate(BaseModel):
    first_name    : str
    last_name     : str
    date_of_birth : date
    gender        : Gender
    blood_group   : str | None = None
    phone_number  : str | None = None  

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip().title()

    model_config = {"from_attributes": True}

class PatientOut(BaseModel):
    id            : uuid.UUID
    doctor_id     : uuid.UUID
    first_name    : str
    last_name     : str
    date_of_birth : date
    gender        : str
    blood_group   : str | None
    phone_number  : str | None = None  
    created_at    : datetime

    model_config = {"from_attributes": True}


# ─── Medical Record ───────────────────────────────────────

class RecordCreate(BaseModel):
    patient_id  : uuid.UUID
    title       : str
    record_type : RecordType
    # file arrives as UploadFile in the router — not here

class RecordOut(BaseModel):
    id           : uuid.UUID
    patient_id   : uuid.UUID
    doctor_id    : uuid.UUID
    title        : str
    record_type  : str
    download_url : str          # renamed — frontend never needs to know it's S3
    file_type    : str
    uploaded_at  : datetime

    model_config = {"from_attributes": True}


# ─── Share Link ───────────────────────────────────────────

class ShareLinkCreate(BaseModel):
    record_id        : uuid.UUID
    expires_in_hours : int = Field(default=24, ge=1, le=720)  # 1hr min → 30 days max

class ShareLinkOut(BaseModel):
    token      : str
    expires_at : datetime
    plain_otp_code : str  # Added so service can safely return the code to your router


    model_config = {"from_attributes": True}

class ShareVerify(BaseModel):
    token             : str
    verification_code : str = Field(min_length=6, max_length=6)

class ShareVerifyOut(BaseModel):
    record_title : str
    record_type  : RecordType
    download_url : str          # renamed — clean URL, not raw S3 path
    doctor_name  : str          # "Verified: Record from Dr. [Name]"
    expires_at   : datetime

    model_config = {"from_attributes": True}


# ─── Dashboard  ───────────────────────────────────────────
class DashboardStatsOut(BaseModel):
    total_patients : int
    total_records  : int
    active_shares  : int

    model_config = {"from_attributes": True}