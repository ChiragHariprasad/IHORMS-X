"""
IHORMS Database Populator
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
        self.org_codes = {} # Map org_id to code
        self.branch_codes = {} # Map branch_id to code
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
        self.patient_counters = {} # branch_id -> counter
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
                "ECG Machine", "X-Ray Machine", "Ultrasound", "CT Scanner", "MRI Scanner",
                "Ventilator", "Defibrillator", "Patient Monitor", "Infusion Pump", "Pulse Oximeter"
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
            branch_doctors = [d for d in self.doctors if self.session.query(User).filter_by(id=d.user_id, branch_id=patient.branch_id).first()]
            branch_nurses = [n for n in self.nurses if self.session.query(User).filter_by(id=n.user_id, branch_id=patient.branch_id).first()]
            branch_rooms = [r for r in self.rooms if r.branch_id == patient.branch_id and r.room_type == RoomType.CONSULTATION]
            
            if not branch_doctors or not branch_nurses or not branch_rooms:
                continue
                
            disease, severity, medications = random.choice(diseases)
            visits_map = { Severity.LOW: random.randint(1, 8), Severity.MEDIUM: random.randint(8, 20), Severity.HIGH: random.randint(20, 35), Severity.CRITICAL: random.randint(30, 40) }
            num_visits = visits_map[severity]
            start_date = datetime.now() - timedelta(days=random.randint(180, 730))
            
            for visit_num in range(num_visits):
                visit_date = start_date + timedelta(days=visit_num * random.randint(3, 30))
                if visit_date > datetime.now(): break
                
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
                    created_by=random.choice([u.id for u in self.receptionists if self.session.query(User).filter_by(id=u.id, branch_id=patient.branch_id).first()] or [1])
                )
                self.session.add(appointment)
                self.session.flush()
                total_appointments += 1
                
                history = MedicalHistory(
                    patient_id=patient.id,
                    appointment_id=appointment.id,
                    visit_date=visit_date,
                    diagnosis=disease,
                    symptoms=random.choice(["Cough, fever, fatigue", "Chest pain, shortness of breath", "Headache, dizziness", "Abdominal pain, nausea"]),
                    severity=severity,
                    treatment_given=f"Prescribed {', '.join(medications[:2])}",
                    medications={"medicines": [{"name": med, "dosage": "As prescribed"} for med in medications]},
                    follow_up_required=severity in [Severity.HIGH, Severity.CRITICAL],
                    follow_up_date=visit_date.date() + timedelta(days=random.randint(7, 30)) if severity in [Severity.HIGH, Severity.CRITICAL] else None,
                    doctor_notes=f"Patient condition: {'stable' if visit_num > 3 else 'monitoring required'}"
                )
                self.session.add(history)
                
                # ... Telemetry, Billing etc (Skipped for brevity in this mock, but you get the point)
        self.session.commit()
        print(f"Created {total_appointments} Appointments with Medical History")

    def populate_all(self):
        """Run all population methods"""
        print("=" * 60)
        print("IHORMS DATABASE POPULATION STARTED")
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
            print("\n" + "=" * 60)
            print("DATABASE POPULATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
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
