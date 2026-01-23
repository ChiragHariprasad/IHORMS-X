# IHORMS - Integrated Hospital Resource Management System

## 🏥 Overview

**IHORMS** (Integrated Hospital Resource Management System) is a state-of-the-art, comprehensive, and scalable healthcare management platform designed for multi-branch hospital organizations. Unlike traditional hospital management systems that operate in silos, IHORMS offers a **centralized, multi-tenant architecture** that connects patients, doctors, nurses, pharmacists, and administrators across different physical branches under a parent organization.

This system digitizes the entire healthcare workflow—from patient registration and appointment scheduling to clinical documentation, real-time vital monitoring, pharmacy inventory, and billing. It is built with a focus on security, using strict **Role-Based Access Control (RBAC)** to ensure data privacy and compliance.

---

## 🚀 Unique Features

IHORMS distinguishes itself with several advanced capabilities:

### 1. 🧠 ML-Based Doctor Recommendation System
Instead of randomly booking doctors, patients or receptionists enter "Chief Complaints" (symptoms). The system utilizes an intelligent **Doctor Recommendation Service** that analyzes these symptoms and suggests the most relevant specialists (e.g., Cardiologist for chest pain) who are available at that specific time, reducing triage errors.

### 2. 📡 Real-Time Telemetry & Critical Alerts
The **Nurse Module** integration allows for the recording of patient vitals (Heart Rate, BP, SpO2). The system automatically analyzes these inputs against medical thresholds. If a paramater violates safety limits (e.g., SpO2 < 90%), a **Critical Alert** is instantly flagged to nurses and doctors, potentially saving lives through early intervention.

### 3. 🏢 Multi-Organization & Multi-Branch Support
Designed as a SaaS-ready platform, IHORMS supports:
- **Super Admins** who manage multiple hospital organizations (e.g., Apollo, Fortis).
- **Organization Admins** who oversee multiple branches of their specific hospital chain.
- Data isolation ensures that Branch A cannot see Branch B's data unless authorized at the organizational level.

### 4. 💰 Comprehensive Billing & Insurance Workflow
A fully integrated financial module that handles:
- **Itemized Billing**: Creating bills with multiple line items, discounts, and taxes.
- **Insurance Processing**: Tracking claims separately from direct payments.
- **Revenue Analytics**: Providing organization-level insights into monthly revenue trends.

---

## 👥 Roles & Features

IHORMS implements **8 distinct user roles**, each with a dedicated dashboard and specific permissions.

### 1. 🦸‍♂️ Super Admin
*The platform owner.*
- **Organization Management**: Create and onboard new hospital organizations.
- **Platform Analytics**: View total users, active organizations, and system health.
- **Global Settings**: Configure platform-wide policies.

### 2. 🏛️ Organization Admin
*The CEO/Administrator of a specific hospital chain.*
- **Branch Management**: Create and manage physical hospital branches.
- **Staff Oversight**: Hire and assign Branch Admins.
- **Billing Analytics**: Visualize monthly revenue trends, total bills, and outstanding payments via interactive charts.
- **User Access Control**: Toggle access for staff across all branches.

### 3. 🏥 Branch Admin
*The manager of a specific hospital location.*
- **Staff Management**: Onboard Doctors, Nurses, Receptionists, and Pharmacists for their branch.
- **Inventory Oversight**: Monitor stock levels of the branch pharmacy.
- **Operational Reports**: View appointment volumes and daily activity logs.

### 4. 👨‍⚕️ Doctor
*The primary care provider.*
- **Smart Scheduling**: View daily appointments and accepted patient slots.
- **Clinical Documentation**: Record diagnosis, prescriptions, and detailed clinical notes.
- **Admissions**: Admit patients to specific wards (General, ICU, Emergency) directly from the consult.
- **Discharge Approval**: Review and approve/reject discharge requests initiated by nurses, adding discharge summaries.
- **Patient History**: Access complete medical history of assigned patients.

### 5. 👩‍⚕️ Nurse
*The patient care monitor.*
- **Ward Management**: View occupied rooms and admitted patient details.
- **Telemetry Recording**: Input patient vitals (HR, BP, Temp, etc.).
- **Discharge Requests**: Initiate discharge workflows for recovered patients.
- **Critical Alerts**: Receive immediate notifications for patients with abnormal vitals.

### 6. 💁‍♀️ Receptionist
*The front-desk executive.*
- **Patient Registration**: Register new patients with demographics and insurance details.
- **Appointment Management**: Book, reschedule, and confirm appointments.
- **Triage**: Assign doctors manually if needed.
- **Billing**: Create itemized bills for patients, apply discounts/taxes, and process separate line items.

### 7. 💊 Pharmacist
*The medication manager.*
- **Inventory Management**: Track medicine stock levels in real-time.
- **Restocking**: Update stock counts and manage low-stock alerts.
- **Prescription Fulfillment**: (Future scope) View and fulfill digital prescriptions.

### 8. 👤 Patient
*The service receiver.*
- **Self-Service Portal**: View personal medical history and past visits.
- **Tele-Booking**: Book appointments online by describing symptoms.
- **My Bills**: View pending bills, pay them online, or submit insurance claims.

---

## 🔐 Role-Based Login & Security

IHORMS uses a secure, token-based authentication system.

1.  **Login Process**:
    - Users enter credentials on a unified login page.
    - The backend validates credentials and determines the user's **Role**.
2.  **JWT Authentication**:
    - Upon success, the server issues a **JSON Web Token (JWT)** containing the user's ID, Role, and Organization ID.
    - This token is encrypted and stored securely in the client browser.
3.  **Route Protection**:
    - **Frontend**: The UI checks the role in the stored token. A user attempting to access `doctor.html` with a `nurse` role is automatically redirected to `index.html` (Login).
    - **Backend**: Every API endpoint is protected by dependencies (e.g., `get_current_doctor`). If a user tries to hit a doctor-only API endpoint with a nurse token, the server returns a `403 Forbidden` error.
    - **Data Isolation**: Database queries automatically filter results based on the user's `organization_id` and `branch_id`, preventing data leakage between branches.

---

## 🛠️ Technology Stack

-   **Backend**: Python 3.11+, FastAPI (High-performance API), SQLAlchemy (ORM), Pydantic (Validation).
-   **Database**: PostgreSQL 14+ (Relational Data Model in 3NF).
-   **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+ Modules), Chart.js.
-   **Security**: OAuth2 with Password Bearer flow, BCrypt password hashing.

---

## 📂 Code Structure & Functionality

This section details the core components of the IHORMS codebase, explaining the role of each key file and directory.

### 1. `main.py`
The entry point of the FastAPI application.
- **`app = FastAPI(...)`**: Initializes the web server.
- **`app.include_router(...)`**: Aggregate all role-specific routers (e.g., `doctor_router`, `nurse_router`) into the main application.
- **`Base.metadata.create_all(...)`**: Automatically creates database tables (User, Patient, Doctor, etc.) if they don't exist on startup.

### 2. `routers/` Directory
Contains the API endpoints (controllers) for each user role. Each file maps HTTP requests (GET, POST) to service logic.

- **`auth.py`**:
  - `POST /login`: Validates username/password, returns JWT token.
  - `get_current_user()`: Dependency used by other routers to decode tokens and verify identity.
  
- **`doctor.py`**:
  - `GET /appointments`: Fetches the doctor's daily schedule.
  - `POST /notes`: Saves clinical diagnosis and prescriptions.
  - `POST /admit`: Admits a patient to a ward.
  
- **`nurse.py`**:
  - `POST /telemetry`: Accepts vital sign data (HR, BP).
  - `GET /admissions`: Lists currently admitted patients.
  
- **`receptionist/billing.py`**:
  - `POST /register`: Creates new patient records.
  - `POST /bill`: Generates financial invoices.

### 3. `services/` Directory
Contains the business logic layer. This separates "what to do" from "how to handle requests".

- **`appointment_service.py`**:
  - `check_doctor_availability()`: Ensures no double-booking.
  - `auto_assign_doctor()`: Finds an available doctor if one isn't specified.
  - `recommend_doctors()`: Returns a list of suitable specialists based on patient symptoms (ML logic).
  
- **`clinical_service.py`**:
  - `analyze_vitals()`: Checks if telemetry data exceeds safe thresholds (e.g., Temp > 104°F) and triggers alerts.
  
- **`billing_service.py`**:
  - `calculate_total()`: Sums up line items, applies tax/discounts.
  - `process_insurance()`: Handles claim submission logic.

### 4. `models.py`
Defines the database schema using SQLAlchemy ORM.
- **`User`**: Base table for all login accounts.
- **`Doctor`, `Nurse`, `Patient`**: Extension tables linked to `User` via Foreign Keys.
- **`Appointment`**: Links Patients and Doctors.
- **`Telemetry`**: Stores time-series vital data.

### 5. `database.py`
Handles the PostgreSQL connection.
- **`get_db()`**: A generator function that yields a database session for each request and closes it afterwards (Dependency Injection).

---

## 🤖 Advanced Technology Integrations

IHORMS pushes the boundaries of traditional hospital management by integrating robust database principles with cutting-edge AI.

### 1. Database Architecture (RDBMS)
The core of IHORMS is a **PostgreSQL** database designed with strict adherence to **ACID principles** (Atomicity, Consistency, Isolation, Durability) to ensure data integrity in a critical healthcare environment.

- **3NF Normalization**: The schema is normalized to the Third Normal Form to eliminate data redundancy. For example, `Branch` details are stored once and referenced by `User` records via a Foreign Key, preventing inconsistencies.
- **Complex Relationships**: The system handles intricate many-to-many relationships, such as a `Doctor` working across multiple `DEPARTMENTS` or a `Patient` having multiple `APPOINTMENTS`.
- **Indexing & Performance**: Critical columns like `patient_uid` and appointment `dates` are indexed to ensure sub-second query responses even with millions of records.
- **Transaction Management**: Financial transactions (Billing) and Clinical transactions (Admissions) are wrapped in atomic database sessions. If an error occurs during bill generation, the entire transaction rolls back, preventing "ghost" financial records.

### 2. AI & Machine Learning Integration
We embed intelligence directly into clinical workflows:

#### 🧠 Intelligent Doctor Triaging (Deployed)
- **Problem**: Patients often don't know which specialist to see (e.g., visiting a General Physician for a specific cardiac issue).
- **Solution**: A Natural Language Understanding (NLU) model processes the patient's "Chief Complaint" (e.g., "persistent cough and fever"). It maps these symptoms to the correct distinct specialization (Pulmonology) and recommends available doctors in that department.

#### 📈 Time-Series Stock Prediction (Beta)
*Located in the Pharmacist Dashboard.*
- **Problem**: Hospitals often face drug shortages or wastage due to overstocking.
- **Solution**: An ARIMA (AutoRegressive Integrated Moving Average) model analyzes historical consumption data of medicines over the last 12 months.
- **Output**: It predicts the **Demand Forecast** for the upcoming month.
- **UI Interaction**: The Pharmacy dashboard displays a "Predicted Demand" graph overlaying the current stock levels, alerting pharmacists to reorder specific antibiotics or critical care drugs *before* they run out.

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-org/ihoums.git
    cd ihorms
    ```

2.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup**:
    -   Ensure PostgreSQL is running.
    -   Update `database.py` or environment variables with your DB credentials.
    -   Run migrations (if Alembic is configured) or `main.py` will auto-create tables.

5.  **Run the Backend**:
    ```bash
    python main.py
    ```
    Server starts at `http://localhost:8000`.

6.  **Run the Frontend**:
    In a separate terminal:
    ```bash
    cd frontend
    python serve.py
    ```
    Access the app at `http://localhost:3000`.

---
*IHORMS - Revolutionizing Healthcare Management*
