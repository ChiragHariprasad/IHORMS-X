"""
IHORMS-X Database Populator
Generates realistic hospital data with standardized ID format: <ORG>-<BRANCH>-<ENTITY>-<SEQUENCE>
"""

import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
import hashlib

# Initialize Faker with Indian locale
fake = Faker('en_IN')
Faker.seed(42)
random.seed(42)

# Database connection
DATABASE_URL = "postgresql://postgres:chiragh@localhost:5432/ihorms_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def hash_password(password):
    """Simple password hashing for demo"""
    return hashlib.sha256(password.encode()).hexdigest()

class DataPopulator:
    def __init__(self):
        self.session = SessionLocal()
        self.organizations = []
        self.branches = []
        self.org_codes = {}  # Map org_id to code
        self.branch_codes = {}  # Map branch_id to code
        self.super_admins = []
        self.org_admins = []
        self.deans = []
        self.doctors = []
        self.nurses = []
        self.receptionists = []
        self.pharmacy_staff = []
        self.patients = []
        self.equipment = []
        self.rooms = []
        self.suppliers = []
        
        # Counters for entity sequences per branch
        self.patient_counters = {}  # branch_id -> counter
        self.doctor_counters = {}
        self.nurse_counters = {}
        self.receptionist_counters = {}
        self.pharmacy_counters = {}
        self.equipment_counters = {}
        
    def generate_user_id(self, org_code, branch_code, entity_type, sequence):
        """Generate standardized user/equipment ID"""
        return f"{org_code}-{branch_code}-{entity_type}{sequence:05d}"
    
    def get_next_sequence(self, branch_id, entity_type):
        """Get next sequence number for entity type at branch"""
        counter_map = {
            'P': self.patient_counters,
            'D': self.doctor_counters,
            'N': self.nurse_counters,
            'R': self.receptionist_counters,
            'PH': self.pharmacy_counters,
            'EQ': self.equipment_counters
        }
        
        counter = counter_map.get(entity_type, {})
        if branch_id not in counter:
            counter[branch_id] = 0
        counter[branch_id] += 1
        return counter[branch_id]
        
    def create_super_admins(self):
        """Create 3 super admins (platform owners)"""
        print("Creating Super Admins...")
        admins_data = [
            ("Chirag", "H", "chirag.h@ihorms.com", "superadmin1"),
            ("KS", "Gowda", "ks.gowda@ihorms.com", "superadmin2"),
            ("Super", "Admin", "superadmin@ihorms.com", "superadmin3")
        ]
        
        for first, last, email, password in admins_data:
            user = User(
                role=UserRole.SUPER_ADMIN,
                email=email,
                password_hash=hash_password(password),
                first_name=first,
                last_name=last,
                phone=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=50),
                gender=random.choice(['Male', 'Female']),
                is_active=True
            )
            self.session.add(user)
            self.super_admins.append(user)
        
        self.session.commit()
        print(f"Created {len(self.super_admins)} Super Admins")
    
    def create_organizations(self):
        """Create 4 hospital organizations with codes"""
        print("\nCreating Organizations...")
        org_data = [
            ("Apollo Hospitals", "APL"),
            ("Fortis Healthcare", "FRT"),
            ("Max Healthcare", "MAX"),
            ("Manipal Hospitals", "MNP")
        ]
        
        for name, code in org_data:
            org = Organization(
                name=name,
                address=fake.address(),
                phone=fake.phone_number(),
                email=f"contact@{name.lower().replace(' ', '')}.com",
                is_active=True
            )
            self.session.add(org)
            self.session.flush()
            self.organizations.append(org)
            self.org_codes[org.id] = code
        
        self.session.commit()
        print(f"Created {len(self.organizations)} Organizations")
    
    def create_branches(self):
        """Create 3 branches per organization with codes"""
        print("\nCreating Branches...")
        cities_data = [
            [("Mumbai", "MUM"), ("Delhi", "DEL"), ("Bangalore", "BLR")],
            [("Chennai", "CHN"), ("Hyderabad", "HYD"), ("Pune", "PUN")],
            [("Kolkata", "KOL"), ("Ahmedabad", "AMD"), ("Jaipur", "JPR")],
            [("Chandigarh", "CHD"), ("Lucknow", "LKO"), ("Indore", "IDR")]
        ]
        
        for idx, org in enumerate(self.organizations):
            for city, city_code in cities_data[idx]:
                branch = Branch(
                    organization_id=org.id,
                    name=f"{org.name} - {city}",
                    address=fake.address(),
                    phone=fake.phone_number(),
                    city=city,
                    state=fake.state(),
                    pincode=fake.postcode(),
                    is_active=True
                )
                self.session.add(branch)
                self.session.flush()
                self.branches.append(branch)
                self.branch_codes[branch.id] = city_code
        
        self.session.commit()
        print(f"Created {len(self.branches)} Branches")
    
    def create_org_admins(self):
        """Create 1 org admin per organization"""
        print("\nCreating Org Admins...")
        
        for org in self.organizations:
            user = User(
                organization_id=org.id,
                role=UserRole.ORG_ADMIN,
                email=f"admin@{org.name.lower().replace(' ', '')}.com",
                password_hash=hash_password("orgadmin1"),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=35, maximum_age=55),
                gender=random.choice(['Male', 'Female']),
                is_active=True
            )
            self.session.add(user)
            self.org_admins.append(user)
        
        self.session.commit()
        print(f"Created {len(self.org_admins)} Org Admins")
    
    def create_branch_admins(self):
        """Create 2 deans per branch"""
        print("\nCreating Branch Admins (Deans)...")
        
        for branch in self.branches:
            for dean_num in [1, 2]:
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.BRANCH_ADMIN,
                    email=f"dean{dean_num}.{branch.city.lower()}@{branch.organization.name.lower().replace(' ', '')}.com",
                    password_hash=hash_password(f"dean{dean_num}"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=40, maximum_age=60),
                    gender=random.choice(['Male', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.deans.append(user)
        
        self.session.commit()
        print(f"Created {len(self.deans)} Deans")
    
    def create_rooms_and_equipment(self):
        """Create rooms and equipment for each branch with standardized IDs"""
        print("\nCreating Rooms and Equipment...")
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            
            # Create rooms
            room_types_count = {
                RoomType.CONSULTATION: random.randint(10, 15),
                RoomType.ICU: random.randint(5, 10),
                RoomType.GENERAL_WARD: random.randint(15, 25),
                RoomType.EMERGENCY: random.randint(3, 5),
                RoomType.OPERATION_THEATER: random.randint(2, 4)
            }
            
            room_counter = 1
            for room_type, count in room_types_count.items():
                for _ in range(count):
                    room = Room(
                        branch_id=branch.id,
                        room_number=f"{branch_code}-{room_counter:03d}",
                        room_type=room_type,
                        floor=random.randint(1, 5),
                        capacity=1 if room_type in [RoomType.CONSULTATION, RoomType.ICU] else random.randint(2, 6),
                        is_available=True
                    )
                    self.session.add(room)
                    self.rooms.append(room)
                    room_counter += 1
            
            # Create equipment with standardized IDs
            equipment_types = [
                "ECG Machine", "X-Ray Machine", "Ultrasound", "CT Scanner", 
                "MRI Scanner", "Ventilator", "Defibrillator", "Patient Monitor",
                "Infusion Pump", "Pulse Oximeter"
            ]
            
            for _ in range(random.randint(20, 30)):
                seq = self.get_next_sequence(branch.id, 'EQ')
                equipment_id = self.generate_user_id(org_code, branch_code, 'EQ', seq)
                
                equip = Equipment(
                    branch_id=branch.id,
                    name=random.choice(equipment_types),
                    equipment_type=random.choice(equipment_types),
                    serial_number=equipment_id,
                    purchase_date=fake.date_between(start_date='-5y', end_date='today'),
                    last_maintenance=fake.date_between(start_date='-3m', end_date='today'),
                    is_operational=random.choice([True, True, True, False])
                )
                self.session.add(equip)
                self.equipment.append(equip)
        
        self.session.commit()
        print(f"Created {len(self.rooms)} Rooms and {len(self.equipment)} Equipment")
    
    def create_doctors(self):
        """Create 20-30 doctors per branch with standardized IDs"""
        print("\nCreating Doctors...")
        
        specializations = [
            "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Gynecology",
            "Dermatology", "ENT", "Ophthalmology", "Psychiatry", "General Medicine",
            "Surgery", "Oncology", "Urology", "Nephrology", "Gastroenterology"
        ]
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            num_doctors = random.randint(20, 30)
            
            for _ in range(num_doctors):
                seq = self.get_next_sequence(branch.id, 'D')
                doctor_id = self.generate_user_id(org_code, branch_code, 'D', seq)
                
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.DOCTOR,
                    email=fake.unique.email(),
                    password_hash=hash_password("doctor123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=28, maximum_age=65),
                    gender=random.choice(['Male', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.session.flush()
                
                doctor = Doctor(
                    user_id=user.id,
                    specialization=random.choice(specializations),
                    qualification=random.choice(["MBBS, MD", "MBBS, MS", "MBBS, DNB", "MBBS, DM"]),
                    experience_years=random.randint(2, 35),
                    license_number=doctor_id,
                    consultation_fee=Decimal(random.randint(500, 2000))
                )
                self.session.add(doctor)
                self.doctors.append(doctor)
        
        self.session.commit()
        print(f"Created {len(self.doctors)} Doctors")
    
    def create_nurses(self):
        """Create 30-40 nurses per branch with standardized IDs"""
        print("\nCreating Nurses...")
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            num_nurses = random.randint(30, 40)
            
            for _ in range(num_nurses):
                seq = self.get_next_sequence(branch.id, 'N')
                nurse_id = self.generate_user_id(org_code, branch_code, 'N', seq)
                
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.NURSE,
                    email=fake.unique.email(),
                    password_hash=hash_password("nurse123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=55),
                    gender=random.choice(['Male', 'Female', 'Female', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.session.flush()
                
                nurse = Nurse(
                    user_id=user.id,
                    qualification=random.choice(["GNM", "BSc Nursing", "MSc Nursing"]),
                    license_number=nurse_id
                )
                self.session.add(nurse)
                self.nurses.append(nurse)
        
        self.session.commit()
        print(f"Created {len(self.nurses)} Nurses")
    
    def create_receptionists(self):
        """Create 8-10 receptionists per branch with standardized IDs"""
        print("\nCreating Receptionists...")
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            num_receptionists = random.randint(8, 10)
            
            for _ in range(num_receptionists):
                seq = self.get_next_sequence(branch.id, 'R')
                receptionist_id = self.generate_user_id(org_code, branch_code, 'R', seq)
                
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.RECEPTIONIST,
                    email=fake.unique.email(),
                    password_hash=hash_password("reception123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=45),
                    gender=random.choice(['Male', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.receptionists.append(user)
        
        self.session.commit()
        print(f"Created {len(self.receptionists)} Receptionists")
    
    def create_pharmacy_staff(self):
        """Create 5-7 pharmacy staff per branch with standardized IDs"""
        print("\nCreating Pharmacy Staff...")
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            num_pharma = random.randint(5, 7)
            
            for _ in range(num_pharma):
                seq = self.get_next_sequence(branch.id, 'PH')
                pharma_id = self.generate_user_id(org_code, branch_code, 'PH', seq)
                
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.PHARMACY_STAFF,
                    email=fake.unique.email(),
                    password_hash=hash_password("pharma123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=22, maximum_age=50),
                    gender=random.choice(['Male', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.pharmacy_staff.append(user)
        
        self.session.commit()
        print(f"Created {len(self.pharmacy_staff)} Pharmacy Staff")
    
    def create_patients(self):
        """Create 60-100 patients per branch with standardized IDs"""
        print("\nCreating Patients...")
        
        insurance_providers = [
            "Star Health Insurance", "ICICI Lombard", "HDFC ERGO", 
            "Care Health Insurance", "Max Bupa", "Religare Health Insurance"
        ]
        
        for branch in self.branches:
            org_code = self.org_codes[branch.organization_id]
            branch_code = self.branch_codes[branch.id]
            num_patients = random.randint(60, 100)
            
            for _ in range(num_patients):
                seq = self.get_next_sequence(branch.id, 'P')
                patient_uid = self.generate_user_id(org_code, branch_code, 'P', seq)
                
                user = User(
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    role=UserRole.PATIENT,
                    email=fake.unique.email(),
                    password_hash=hash_password("patient123"),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=1, maximum_age=90),
                    gender=random.choice(['Male', 'Female']),
                    is_active=True
                )
                self.session.add(user)
                self.session.flush()
                
                has_insurance = random.choice([True, False, False])
                
                patient = Patient(
                    user_id=user.id,
                    organization_id=branch.organization_id,
                    branch_id=branch.id,
                    patient_uid=patient_uid,
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                    emergency_contact=fake.phone_number(),
                    emergency_contact_name=fake.name(),
                    address=fake.address(),
                    insurance_provider=random.choice(insurance_providers) if has_insurance else None,
                    insurance_policy_number=f"POL-{fake.uuid4()[:12].upper()}" if has_insurance else None,
                    insurance_expiry=fake.date_between(start_date='today', end_date='+2y') if has_insurance else None
                )
                self.session.add(patient)
                self.patients.append(patient)
        
        self.session.commit()
        print(f"Created {len(self.patients)} Patients")
    
    def create_appointments_and_history(self):
        """Create appointments and medical history for all patients"""
        print("\nCreating Appointments and Medical History...")
        
        diseases = [
            ("Common Cold", Severity.LOW, ["Paracetamol", "Vitamin C"]),
            ("Fever", Severity.LOW, ["Paracetamol", "Ibuprofen"]),
            ("Hypertension", Severity.MEDIUM, ["Amlodipine", "Losartan"]),
            ("Diabetes Type 2", Severity.HIGH, ["Metformin", "Insulin"]),
            ("Asthma", Severity.MEDIUM, ["Salbutamol Inhaler", "Budesonide"]),
            ("Pneumonia", Severity.HIGH, ["Antibiotics", "Amoxicillin"]),
            ("Heart Disease", Severity.CRITICAL, ["Aspirin", "Atorvastatin", "Metoprolol"]),
            ("Kidney Disease", Severity.CRITICAL, ["ACE Inhibitors", "Diuretics"]),
            ("Cancer", Severity.CRITICAL, ["Chemotherapy", "Radiation"]),
            ("Tuberculosis", Severity.HIGH, ["Rifampicin", "Isoniazid"])
        ]
        
        total_appointments = 0
        total_access_logs = 0
        
        for patient in self.patients:
            branch_doctors = [d for d in self.doctors if d.user_id in 
                            [u.id for u in self.session.query(User).filter_by(branch_id=patient.branch_id, role=UserRole.DOCTOR).all()]]
            branch_nurses = [n for n in self.nurses if n.user_id in 
                           [u.id for u in self.session.query(User).filter_by(branch_id=patient.branch_id, role=UserRole.NURSE).all()]]
            branch_rooms = [r for r in self.rooms if r.branch_id == patient.branch_id and r.room_type == RoomType.CONSULTATION]
            
            if not branch_doctors or not branch_nurses or not branch_rooms:
                continue
            
            disease, severity, medications = random.choice(diseases)
            
            visits_map = {
                Severity.LOW: random.randint(1, 8),
                Severity.MEDIUM: random.randint(8, 20),
                Severity.HIGH: random.randint(20, 35),
                Severity.CRITICAL: random.randint(30, 40)
            }
            num_visits = visits_map[severity]
            
            start_date = datetime.now() - timedelta(days=random.randint(180, 730))
            
            for visit_num in range(num_visits):
                visit_date = start_date + timedelta(days=visit_num * random.randint(3, 30))
                
                if visit_date > datetime.now():
                    break
                
                doctor = random.choice(branch_doctors)
                room = random.choice(branch_rooms)
                
                appointment = Appointment(
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    room_id=room.id,
                    appointment_date=visit_date.date(),
                    appointment_time=time(hour=random.randint(9, 17), minute=random.choice([0, 15, 30, 45])),
                    status=AppointmentStatus.COMPLETED,
                    chief_complaint=f"Follow-up for {disease}" if visit_num > 0 else disease,
                    notes=f"Patient showing {'improvement' if visit_num > 2 else 'symptoms of'} {disease}",
                    diagnosis=disease,
                    prescription=", ".join(medications),
                    verdict="Continue medication and follow-up" if severity != Severity.LOW else "Complete rest advised",
                    created_by=random.choice([u.id for u in self.receptionists if u.branch_id == patient.branch_id])
                )
                self.session.add(appointment)
                self.session.flush()
                total_appointments += 1
                
                history = MedicalHistory(
                    patient_id=patient.id,
                    appointment_id=appointment.id,
                    visit_date=visit_date,
                    diagnosis=disease,
                    symptoms=random.choice([
                        "Cough, fever, fatigue",
                        "Chest pain, shortness of breath",
                        "Headache, dizziness",
                        "Abdominal pain, nausea"
                    ]),
                    severity=severity,
                    treatment_given=f"Prescribed {', '.join(medications[:2])}",
                    medications={"medicines": [{"name": med, "dosage": "As prescribed"} for med in medications]},
                    follow_up_required=severity in [Severity.HIGH, Severity.CRITICAL],
                    follow_up_date=visit_date.date() + timedelta(days=random.randint(7, 30)) if severity in [Severity.HIGH, Severity.CRITICAL] else None,
                    doctor_notes=f"Patient condition: {'stable' if visit_num > 3 else 'monitoring required'}"
                )
                self.session.add(history)
                
                if severity in [Severity.HIGH, Severity.CRITICAL] or random.random() < 0.3:
                    nurse = random.choice(branch_nurses)
                    equipment = random.choice([e for e in self.equipment if e.branch_id == patient.branch_id])
                    
                    telemetry = TelemetryData(
                        appointment_id=appointment.id,
                        nurse_id=nurse.id,
                        equipment_id=equipment.id,
                        heart_rate=random.randint(60, 140),
                        blood_pressure_systolic=random.randint(90, 180),
                        blood_pressure_diastolic=random.randint(60, 110),
                        temperature=Decimal(random.uniform(97.0, 103.5)).quantize(Decimal('0.1')),
                        oxygen_saturation=random.randint(85, 100),
                        respiratory_rate=random.randint(12, 30),
                        is_icu_patient=severity == Severity.CRITICAL,
                        alert_triggered=random.choice([True, False]) if severity == Severity.CRITICAL else False,
                        alert_message="Critical vitals - immediate attention" if severity == Severity.CRITICAL and random.random() < 0.2 else None,
                        recorded_at=visit_date
                    )
                    self.session.add(telemetry)
                
                bill_number = f"BILL-{patient.organization_id:02d}-{visit_date.year}-{total_appointments:06d}"
                consultation_fee = self.session.query(Doctor).filter_by(id=doctor.id).first().consultation_fee
                
                billing = Billing(
                    appointment_id=appointment.id,
                    patient_id=patient.id,
                    bill_number=bill_number,
                    bill_date=visit_date,
                    consultation_fee=consultation_fee,
                    medication_cost=Decimal(random.randint(200, 5000)),
                    room_charges=Decimal(random.randint(500, 3000)) if severity in [Severity.HIGH, Severity.CRITICAL] else Decimal(0),
                    test_charges=Decimal(random.randint(500, 8000)),
                    other_charges=Decimal(random.randint(0, 1000)),
                    subtotal=Decimal(0),
                    tax=Decimal(0),
                    discount=Decimal(0),
                    total_amount=Decimal(0),
                    amount_paid=Decimal(0),
                    payment_status='paid',
                    payment_method=random.choice(['Cash', 'Card', 'UPI', 'Insurance'])
                )
                
                billing.subtotal = (billing.consultation_fee + billing.medication_cost + 
                                  billing.room_charges + billing.test_charges + billing.other_charges)
                billing.tax = billing.subtotal * Decimal('0.05')
                billing.total_amount = billing.subtotal + billing.tax
                billing.amount_paid = billing.total_amount
                
                self.session.add(billing)
                self.session.flush()
                
                if patient.insurance_provider and random.random() < 0.6:
                    claim = InsuranceClaim(
                        billing_id=billing.id,
                        patient_id=patient.id,
                        claim_number=f"CLM-{fake.uuid4()[:12].upper()}",
                        insurance_provider=patient.insurance_provider,
                        policy_number=patient.insurance_policy_number,
                        claimed_amount=billing.total_amount * Decimal(random.uniform(0.6, 1.0)),
                        approved_amount=billing.total_amount * Decimal(random.uniform(0.5, 0.9)),
                        status=random.choice([ClaimStatus.APPROVED, ClaimStatus.PAID, ClaimStatus.SUBMITTED]),
                        submitted_date=visit_date,
                        processed_date=visit_date + timedelta(days=random.randint(7, 30))
                    )
                    self.session.add(claim)
                
                num_accesses = random.randint(1, 3)
                for _ in range(num_accesses):
                    access_log = PatientAccessLog(
                        patient_id=patient.id,
                        accessed_by=doctor.user_id,
                        access_type="Medical History View",
                        access_reason="Treatment planning",
                        ip_address=fake.ipv4(),
                        accessed_at=visit_date + timedelta(minutes=random.randint(-30, 30))
                    )
                    self.session.add(access_log)
                    total_access_logs += 1
        
        self.session.commit()
        print(f"Created {total_appointments} Appointments with Medical History")
        print(f"Created {total_access_logs} Patient Access Logs")
    
    def create_pharmacy_data(self):
        """Create pharmacy inventory and orders"""
        print("\nCreating Pharmacy Data...")
        
        supplier_names = [
            "Sun Pharma Distributors", "Cipla Healthcare", "Dr. Reddy's Labs",
            "Lupin Pharmaceuticals", "Torrent Pharma", "Alkem Laboratories"
        ]
        
        for name in supplier_names:
            supplier = Supplier(
                name=name,
                contact_person=fake.name(),
                phone=fake.phone_number(),
                email=f"contact@{name.lower().replace(' ', '').replace(chr(39), '')}.com",
                address=fake.address()
            )
            self.session.add(supplier)
            self.suppliers.append(supplier)
        
        self.session.commit()
        
        medicines = [
            "Paracetamol 500mg", "Ibuprofen 400mg", "Amoxicillin 250mg",
            "Azithromycin 500mg", "Metformin 500mg", "Amlodipine 5mg",
            "Losartan 50mg", "Atorvastatin 10mg", "Aspirin 75mg",
            "Omeprazole 20mg", "Salbutamol Inhaler", "Insulin Injection",
            "Ciprofloxacin 500mg", "Cefixime 200mg", "Pantoprazole 40mg"
        ]
        
        for branch in self.branches:
            for medicine in medicines:
                inventory = Inventory(
                    branch_id=branch.id,
                    medicine_name=medicine,
                    generic_name=medicine.split()[0],
                    manufacturer=random.choice([s.name for s in self.suppliers]),
                    batch_number=f"BATCH-{fake.uuid4()[:8].upper()}",
                    quantity=random.randint(100, 2000),
                    unit_price=Decimal(random.uniform(5, 500)).quantize(Decimal('0.01')),
                    expiry_date=fake.date_between(start_date='+6m', end_date='+3y'),
                    reorder_level=50,
                    last_restocked=fake.date_between(start_date='-3m', end_date='today')
                )
                self.session.add(inventory)
        
        self.session.commit()
        
        order_count = 0
        for patient in random.sample(self.patients, min(500, len(self.patients))):
            num_orders = random.randint(1, 5)
            for _ in range(num_orders):
                pharma_staff = random.choice([p for p in self.pharmacy_staff if 
                                            self.session.query(User).filter_by(id=p.id).first().branch_id == patient.branch_id])
                
                order = PharmacyOrder(
                    patient_id=patient.id,
                    pharmacy_staff_id=pharma_staff.id,
                    order_number=f"ORD-{patient.organization_id:02d}-{order_count+1:06d}",
                    order_date=fake.date_time_between(start_date='-1y', end_date='now'),
                    items={"medicines": [
                        {"name": random.choice(medicines), "quantity": random.randint(1, 3), "price": float(Decimal(random.uniform(50, 500)).quantize(Decimal('0.01')))}
                        for _ in range(random.randint(1, 4))
                    ]},
                    total_amount=Decimal(random.uniform(100, 2000)).quantize(Decimal('0.01')),
                    status=random.choice([OrderStatus.FULFILLED, OrderStatus.FULFILLED, OrderStatus.PENDING]),
                    fulfilled_date=fake.date_time_between(start_date='-1y', end_date='now') if random.random() < 0.8 else None
                )
                self.session.add(order)
                order_count += 1
        
        self.session.commit()
        print(f"Created {len(self.suppliers)} Suppliers, Inventory items, and {order_count} Pharmacy Orders")
    
    def create_audit_logs(self):
        """Create audit logs for various actions"""
        print("\nCreating Audit Logs...")
        
        actions = [
            "USER_LOGIN", "USER_LOGOUT", "PATIENT_CREATED", "APPOINTMENT_CREATED",
            "APPOINTMENT_UPDATED", "MEDICAL_RECORD_ACCESSED", "BILLING_CREATED",
            "INVENTORY_UPDATED", "PRESCRIPTION_ISSUED"
        ]
        
        all_users = self.session.query(User).all()
        
        for _ in range(5000):
            user = random.choice(all_users)
            audit = AuditLog(
                user_id=user.id,
                action=random.choice(actions),
                entity_type=random.choice(["User", "Patient", "Appointment", "Billing"]),
                entity_id=random.randint(1, 1000),
                before_state={"status": "old_value"} if random.random() < 0.5 else None,
                after_state={"status": "new_value"},
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            self.session.add(audit)
        
        self.session.commit()
        print("Created 5000 Audit Logs")
    
    def create_system_events(self):
        """Create system events"""
        print("\nCreating System Events...")
        
        event_types = [
            "SERVER_START", "SERVER_STOP", "DATABASE_BACKUP", "SYSTEM_UPDATE",
            "SECURITY_ALERT", "PERFORMANCE_WARNING", "API_ERROR"
        ]
        
        for _ in range(1000):
            event = SystemEvent(
                event_type=random.choice(event_types),
                severity=random.choice(["INFO", "WARNING", "ERROR", "CRITICAL"]),
                message=fake.sentence(),
                event_metadata={"source": "system", "module": random.choice(["auth", "api", "database"])},
                created_at=fake.date_time_between(start_date='-1y', end_date='now')
            )
            self.session.add(event)
        
        self.session.commit()
        print("Created 1000 System Events")
    
    def populate_all(self):
        """Run all population methods"""
        print("=" * 60)
        print("IHORMS-X DATABASE POPULATION STARTED")
        print("=" * 60)
        
        try:
            self.create_super_admins()
            self.create_organizations()
            self.create_branches()
            self.create_org_admins()
            self.create_branch_admins()
            self.create_rooms_and_equipment()
            self.create_doctors()
            self.create_nurses()
            self.create_receptionists()
            self.create_pharmacy_staff()
            self.create_patients()
            self.create_appointments_and_history()
            self.create_pharmacy_data()
            self.create_audit_logs()
            self.create_system_events()
            
            print("\n" + "=" * 60)
            print("DATABASE POPULATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"\nSummary:")
            print(f"  Organizations: {len(self.organizations)}")
            print(f"  Branches: {len(self.branches)}")
            print(f"  Doctors: {len(self.doctors)}")
            print(f"  Nurses: {len(self.nurses)}")
            print(f"  Patients: {len(self.patients)}")
            print(f"  Total Users: {self.session.query(User).count()}")
            print(f"  Appointments: {self.session.query(Appointment).count()}")
            print(f"  Medical Records: {self.session.query(MedicalHistory).count()}")
            
            # Show sample IDs
            print(f"\n  Sample IDs generated:")
            if self.patients:
                sample_patient = self.patients[0]
                print(f"    Patient: {sample_patient.patient_uid}")
            if self.doctors:
                sample_doctor = self.doctors[0]
                print(f"    Doctor: {sample_doctor.license_number}")
            if self.equipment:
                sample_equipment = self.equipment[0]
                print(f"    Equipment: {sample_equipment.serial_number}")
            
        except Exception as e:
            print(f"\nERROR: {str(e)}")
            self.session.rollback()
            raise
        finally:
            self.session.close()

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully!\n")
    
    populator = DataPopulator()
    populator.populate_all()