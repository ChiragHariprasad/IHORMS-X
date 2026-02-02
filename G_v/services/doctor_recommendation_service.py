"""
Doctor Recommendation Service - AI-powered doctor matching
"""
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Doctor, User, UserRole


class DoctorRecommendationService:
    """Intelligent doctor allocation based on symptoms"""
    
    # Symptom to specialty mapping (expandable database)
    SYMPTOM_SPECIALTY_MAP = {
        # Cardiology
        "chest pain": ["cardiology", "emergency medicine", "general medicine"],
        "heart": ["cardiology"],
        "palpitations": ["cardiology"],
        "shortness of breath": ["cardiology", "pulmonology"],
        
        # Neurology
        "headache": ["neurology", "general medicine"],
        "migraine": ["neurology"],
        "seizure": ["neurology"],
        "dizziness": ["neurology", "ent"],
        "numbness": ["neurology"],
        
        # Orthopedics
        "bone": ["orthopedics"],
        "fracture": ["orthopedics", "emergency medicine"],
        "joint pain": ["orthopedics", "rheumatology"],
        "back pain": ["orthopedics", "neurology"],
        "sprain": ["orthopedics"],
        
        # General Medicine
        "fever": ["general medicine", "infectious disease"],
        "cough": ["general medicine", "pulmonology"],
        "cold": ["general medicine", "ent"],
        "flu": ["general medicine"],
        "fatigue": ["general medicine"],
        
        # Gastroenterology
        "stomach": ["gastroenterology", "general medicine"],
        "abdominal pain": ["gastroenterology", "general surgery"],
        "nausea": ["gastroenterology", "general medicine"],
        "vomiting": ["gastroenterology", "general medicine"],
        "diarrhea": ["gastroenterology"],
        
        # Dermatology
        "rash": ["dermatology"],
        "skin": ["dermatology"],
        "acne": ["dermatology"],
        "itch": ["dermatology"],
        
        # Pediatrics
        "child": ["pediatrics"],
        "baby": ["pediatrics"],
        "infant": ["pediatrics"],
        
        # Obstetrics & Gynecology
        "pregnancy": ["obstetrics and gynecology"],
        "prenatal": ["obstetrics and gynecology"],
        "menstrual": ["obstetrics and gynecology"],
        
        # ENT
        "ear": ["ent"],
        "nose": ["ent"],
        "throat": ["ent"],
        "sinus": ["ent"],
        
        # Ophthalmology
        "eye": ["ophthalmology"],
        "vision": ["ophthalmology"],
        "blurry": ["ophthalmology"],
        
        # Pulmonology
        "breathing": ["pulmonology", "cardiology"],
        "asthma": ["pulmonology"],
        "lung": ["pulmonology"],
        
        # Emergency
        "accident": ["emergency medicine", "orthopedics"],
        "trauma": ["emergency medicine"],
        "bleeding": ["emergency medicine", "general surgery"],
        "unconscious": ["emergency medicine"],
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def extract_specialties(self, symptoms: str) -> List[str]:
        """Extract relevant specialties from symptom text"""
        symptoms_lower = symptoms.lower()
        matched_specialties = set()
        
        for symptom_keyword, specialties in self.SYMPTOM_SPECIALTY_MAP.items():
            if symptom_keyword in symptoms_lower:
                matched_specialties.update(specialties)
        
        # Default to general medicine if no match
        if not matched_specialties:
            matched_specialties.add("general medicine")
        
        return list(matched_specialties)
    
    def recommend_doctors(
        self, 
        symptoms: str, 
        branch_id: int, 
        limit: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Recommend doctors based on symptoms and availability
        Returns: List of (doctor_dict, confidence_score) tuples
        """
        specialties = self.extract_specialties(symptoms)
        
        # Query doctors with matching specialties in the branch
        doctors = self.db.query(Doctor, User).join(
            User, Doctor.user_id == User.id
        ).filter(
            and_(
                User.branch_id == branch_id,
                User.role == UserRole.DOCTOR,
                User.is_active == True
            )
        ).all()
        
        recommendations = []
        for doctor, user in doctors:
            score = self._calculate_match_score(
                doctor.specialization.lower() if doctor.specialization else "",
                specialties
            )
            
            if score > 0:
                recommendations.append(({
                    "id": doctor.id,
                    "user_id": user.id,
                    "name": f"Dr. {user.first_name} {user.last_name}",
                    "specialization": doctor.specialization,
                    "qualification": doctor.qualification,
                    "experience_years": doctor.experience_years,
                    "consultation_fee": float(doctor.consultation_fee) if doctor.consultation_fee else 0,
                    "match_score": score
                }, score))
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return [(doc, score) for doc, score in recommendations[:limit]]
    
    def _calculate_match_score(self, doctor_specialty: str, target_specialties: List[str]) -> float:
        """Calculate how well a doctor matches the required specialties"""
        if not doctor_specialty:
            return 0.3  # General practitioners get base score
        
        # Exact match = 1.0
        for specialty in target_specialties:
            if specialty in doctor_specialty or doctor_specialty in specialty:
                return 1.0
        
        # Partial match = 0.5
        words = doctor_specialty.split()
        for word in words:
            for specialty in target_specialties:
                if word in specialty or len(word) > 4 and word in specialty:
                    return 0.5
        
        # No match
        return 0.0
