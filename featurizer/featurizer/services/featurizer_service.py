import os
import base64
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import httpx
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Load environment variables
load_dotenv()

from featurizer.models import PatientFeatures

logger = logging.getLogger("featurizer")


class FeaturizerService:
    """Core featurizer: fetch de-identified resources, extract structured features,
    decode attachments and produce simple NLP embeddings/tags.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, db_session: Optional[Session] = None):
        self.base_url = base_url or os.getenv("DEID_BASE_URL", "http://localhost:8000")
        self.client = httpx.Client(timeout=timeout)
        self.db = db_session

        # choose embedding backend; by default use sentence-transformers (small)
        self.use_biobert = os.getenv("USE_BIOBERT", "false").lower() in ("1", "true", "yes")
        self.embedding_backend = None
        self._init_embedding()

    def _init_embedding(self):
        """Initialize embedding backend with fallbacks for missing dependencies"""
        if self.use_biobert:
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch

                self._tok = AutoTokenizer.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
                self._model = AutoModel.from_pretrained("dmis-lab/biobert-base-cased-v1.1")
                self.embedding_backend = "biobert"
                logger.info("Using BioBERT for embeddings")
                return
            except Exception as e:
                logger.warning("BioBERT init failed: %s; falling back", e)

        try:
            from sentence_transformers import SentenceTransformer

            self._st = SentenceTransformer("all-MiniLM-L6-v2")
            self.embedding_backend = "sbert"
            logger.info("Using sentence-transformers (all-MiniLM-L6-v2)")
            return
        except Exception as e:
            logger.warning("Sentence transformers not available: %s", e)

        # Fallback: simple text features without embeddings
        self.embedding_backend = "simple"
        logger.info("Using simple text features (no embeddings) - faster for development")

    def _get(self, path: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/') }"
        r = self.client.get(url)
        r.raise_for_status()
        return r.json()

    def fetch_resources_for_patient(self, patient_id: str) -> Dict[str, List[Dict[str, Any]]]:
        endpoints = [
            "deid/patients?limit=10000",  # Get all patients
            "deid/encounters?limit=10000",  # Get all encounters
            "deid/conditions?limit=10000",  # Get all conditions
            "deid/observations?limit=10000",  # Get all observations
            "deid/medication-requests?limit=10000",  # Get all medication requests
            "deid/diagnostic-reports?limit=10000",  # Get all diagnostic reports
            "deid/document-references?limit=10000",  # Get all document references
        ]
        resources: Dict[str, List[Dict[str, Any]]] = {}
        for ep in endpoints:
            try:
                data = self._get(ep)
                # allow either plain list or wrapper dict
                items = data if isinstance(data, list) else list(data.values())[0] if isinstance(data, dict) else []
                
                # Different filtering logic for different resource types
                endpoint_name = ep.split('/')[-1].split('?')[0]  # Remove query params
                
                if endpoint_name == "patients":
                    # For patients, match resource_id
                    filtered = [i for i in items if i.get("resource_id") == patient_id]
                else:
                    # For other resources, match patient_resource_id to link to patient
                    filtered = [i for i in items if i.get("patient_resource_id") == patient_id]
                
                resources[endpoint_name] = filtered
                logger.debug(f"Fetched {len(filtered)} {endpoint_name} for patient {patient_id}")
                
                # Debug: Log if no encounters found for this patient
                if endpoint_name == "encounters" and len(filtered) == 0:
                    logger.warning(f"No encounters found for patient {patient_id} - checking if encounters exist in DEID")
                    logger.warning(f"Total {endpoint_name} in DEID service: {len(items)}")
                    if len(items) > 0:
                        sample_patient_ids = [item.get("patient_resource_id") for item in items[:5]]
                        logger.warning(f"Sample patient_resource_ids in encounters: {sample_patient_ids}")
                
            except Exception as e:
                logger.warning("Failed fetching %s: %s", ep, e)
                resources[ep.split('/')[-1].split('?')[0]] = []

        return resources

    def _decode_attachments(self, doc_refs: List[Dict[str, Any]]) -> List[str]:
        notes: List[str] = []
        for dr in doc_refs:
            att_data = dr.get("attachment_data")
            # fallback to parsing raw_fhir_data if needed
            if not att_data:
                raw = dr.get("raw_fhir_data")
                if raw:
                    try:
                        import json

                        raw_obj = json.loads(raw)
                        content = raw_obj.get("content", [])
                        if content:
                            a = content[0].get("attachment", {})
                            att_data = a.get("data")
                    except Exception:
                        pass

            if not att_data:
                continue

            try:
                text = base64.b64decode(att_data).decode("utf-8", errors="replace")
                notes.append(text)
            except Exception:
                notes.append(att_data)

        return notes

    def extract_structured_features(self, resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Extract essential features for 30-day readmission prediction from FHIR resources"""
        from datetime import datetime, timedelta
        import dateutil.parser
        
        out: Dict[str, Any] = {}
        
        # ====== DEMOGRAPHICS ======
        patients = resources.get("patients", [])
        
        # Initialize demographic fields with defaults
        out["gender"] = None
        out["birth_date"] = None
        out["age"] = None
        out["state"] = None
        
        if patients:
            p = patients[0]
            
            # Extract demographics using actual field names from the data
            out["gender"] = p.get("gender")  # Field exists as "gender"
            out["birth_date"] = p.get("birth_date")  # Field exists as "birth_date"
            out["state"] = p.get("state")  # Field exists as "state"
            
            # Compute age from birth_date
            birth_date_str = p.get("birth_date")
            if birth_date_str:
                try:
                    birth_date = dateutil.parser.parse(birth_date_str)
                    age = (datetime.now() - birth_date).days / 365.25
                    out["age"] = round(age, 1)
                except Exception as e:
                    logger.warning(f"Failed to parse birth_date '{birth_date_str}': {e}")
                    out["age"] = None

        # ====== ENCOUNTER FEATURES (key readmission predictors) ======
        encs = resources.get("encounters", [])
        out["num_encounters"] = len(encs)
        
        # Initialize encounter-based features
        out["length_of_stay_days"] = 0.0
        out["avg_los"] = 0.0
        out["class_code"] = None
        out["type_code"] = None
        out["is_emergency"] = False
        out["is_inpatient"] = False
        out["days_since_last_discharge"] = None
        out["readmission_30d"] = False  # Target variable
        
        if encs:
            # Sort encounters by end_date to find patterns
            sorted_encs = []
            for e in encs:
                end_date_str = e.get("end_date")
                if end_date_str:
                    try:
                        end_date = dateutil.parser.parse(end_date_str)
                        sorted_encs.append((end_date, e))
                    except Exception:
                        pass
            
            sorted_encs.sort(key=lambda x: x[0])  # Sort by end_date
            
            # Most recent encounter features
            if sorted_encs:
                _, most_recent = sorted_encs[-1]
                out["class_code"] = most_recent.get("class_code")
                out["type_code"] = most_recent.get("type_code")
                out["length_of_stay_days"] = most_recent.get("length_of_stay_days") or 0.0
                
                # Binary flags for encounter type
                class_code = most_recent.get("class_code", "").upper()
                out["is_emergency"] = class_code == "EMER"
                out["is_inpatient"] = class_code == "IMP"
                
                # Days since last discharge
                end_date_str = most_recent.get("end_date")
                if end_date_str:
                    try:
                        end_date = dateutil.parser.parse(end_date_str)
                        days_since = (datetime.now() - end_date).days
                        out["days_since_last_discharge"] = days_since
                    except Exception:
                        pass
            
            # Average LOS
            los_values = [e.get("length_of_stay_days") or 0 for e in encs]
            out["avg_los"] = float(np.mean(los_values)) if los_values else 0.0
            
            # **TARGET VARIABLE: 30-day readmission detection**
            # Updated logic: Check for readmission after inpatient OR emergency discharges
            # (since synthetic data may not have inpatient encounters)
            for i, (discharge_date, encounter) in enumerate(sorted_encs):
                # Consider both inpatient and emergency encounters as index admissions
                current_class = encounter.get("class_code", "").upper()
                if current_class not in ["IMP", "EMER"]:  # Only inpatient and emergency
                    continue
                
                # Look for subsequent inpatient/emergency encounters within 30 days
                for j in range(i + 1, len(sorted_encs)):
                    next_encounter = sorted_encs[j][1]
                    next_start_date_str = next_encounter.get("start_date")
                    next_class = next_encounter.get("class_code", "").upper()
                    
                    if next_start_date_str and next_class in ["IMP", "EMER"]:
                        try:
                            next_start_date = dateutil.parser.parse(next_start_date_str)
                            days_diff = (next_start_date - discharge_date).days
                            
                            # Readmission if within 30 days (exclude same-day transfers)
                            if 0 < days_diff <= 30:
                                out["readmission_30d"] = True
                                logger.info(f"Readmission detected: {current_class} -> {next_class} after {days_diff} days")
                                break
                        except Exception:
                            continue
                
                if out["readmission_30d"]:
                    break

        # ====== CONDITION FEATURES (major readmission driver) ======
        conds = resources.get("conditions", [])
        out["num_conditions"] = len(conds)
        out["primary_condition_code"] = None
        out["primary_condition_display"] = None
        out["has_chronic_conditions"] = False
        out["condition_codes"] = []
        
        chronic_condition_codes = ["E10", "E11", "I25", "I50", "J44", "N18"]  # Common chronic conditions
        
        if conds:
            # Extract condition codes and identify chronic conditions
            condition_codes = []
            for c in conds:
                code = c.get("code")
                display = c.get("display") or c.get("code_display")
                
                if code:
                    condition_codes.append({"code": code, "display": display})
                    
                    # Check for chronic conditions (simplified)
                    if any(chronic in str(code) for chronic in chronic_condition_codes):
                        out["has_chronic_conditions"] = True
            
            out["condition_codes"] = condition_codes
            
            # Primary condition (first/most recent)
            if condition_codes:
                out["primary_condition_code"] = condition_codes[0]["code"]
                out["primary_condition_display"] = condition_codes[0]["display"]

        # ====== OBSERVATION FEATURES (vitals/labs volatility) ======
        obs = resources.get("observations", [])
        out["num_observations"] = len(obs)
        out["obs_abnormal_count"] = 0
        out["has_abnormal_glucose"] = False
        out["has_abnormal_hr"] = False
        out["has_abnormal_temp"] = False
        out["has_abnormal_saturation"] = False
        out["vital_signs_available"] = len(obs) > 0
        
        for o in obs:
            # Check for abnormal values in observations
            value_str = str(o.get("value_string", "")).lower()
            code = str(o.get("code", "")).lower()
            display = str(o.get("display", "")).lower()
            
            # Generic abnormal detection
            if any(keyword in value_str for keyword in ["high", "low", "abnormal", "critical"]):
                out["obs_abnormal_count"] += 1
            
            # Specific vital sign abnormalities
            if any(term in code or term in display for term in ["glucose", "blood sugar"]):
                if "high" in value_str or "low" in value_str:
                    out["has_abnormal_glucose"] = True
                    
            elif any(term in code or term in display for term in ["heart rate", "pulse", "hr"]):
                if "high" in value_str or "low" in value_str:
                    out["has_abnormal_hr"] = True
                    
            elif any(term in code or term in display for term in ["temperature", "temp"]):
                if "high" in value_str or "fever" in value_str:
                    out["has_abnormal_temp"] = True
                    
            elif any(term in code or term in display for term in ["oxygen", "saturation", "spo2"]):
                if "low" in value_str:
                    out["has_abnormal_saturation"] = True

        # ====== MEDICATION/PROCEDURE FEATURES ======
        meds = resources.get("medication-requests", [])
        out["num_med_requests"] = len(meds)
        out["polypharmacy"] = len(meds) >= 5  # >= 5 medications indicates polypharmacy
        
        # Extract medication codes
        medication_codes = []
        for m in meds:
            code = m.get("medication_code") or m.get("code")
            display = m.get("medication_display") or m.get("display")
            if code:
                medication_codes.append({"code": code, "display": display})
        out["medication_codes"] = medication_codes
        
        # Procedures (if available in diagnostic reports or separate procedure resource)
        diag_reports = resources.get("diagnostic-reports", [])
        out["num_procedures"] = len(diag_reports)  # Using diagnostic reports as proxy for procedures
        
        # ====== DERIVED RISK INDICATORS (legacy features for compatibility) ======
        out["has_multiple_encounters"] = len(encs) > 1
        out["has_long_stay"] = out["avg_los"] > 7  # > 7 days average
        out["high_med_burden"] = out["polypharmacy"]
        out["high_condition_count"] = out["num_conditions"] >= 3
        out["has_abnormal_labs"] = out["obs_abnormal_count"] > 0
        
        # Clinical complexity score (simple heuristic)
        complexity_score = 0.0
        if out["num_conditions"] >= 3:
            complexity_score += 0.3
        if out["polypharmacy"]:
            complexity_score += 0.2
        if out["avg_los"] > 7:
            complexity_score += 0.2
        if out["obs_abnormal_count"] > 2:
            complexity_score += 0.1
        if out["is_emergency"]:
            complexity_score += 0.2
        
        out["clinical_complexity_score"] = round(complexity_score, 2)

        return out

    def _run_spacy_ner(self, texts: List[str]) -> List[Dict[str, Any]]:
        try:
            import spacy
            try:
                nlp = spacy.load("en_core_sci_md")
            except Exception:
                nlp = spacy.load("en_core_web_sm")

            entities = []
            for t in texts:
                doc = nlp(t)
                for ent in doc.ents:
                    entities.append({"text": ent.text, "label": ent.label_})
            return entities
        except Exception as e:
            logger.warning("spaCy unavailable: %s", e)
            return []

    def _get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not texts:
            return None
        if self.embedding_backend == "biobert":
            try:
                import torch

                toks = self._tok(texts, return_tensors="pt", padding=True, truncation=True)
                with torch.no_grad():
                    out = self._model(**toks)
                embs = out.last_hidden_state.mean(dim=1).cpu().numpy().tolist()
                return embs
            except Exception as e:
                logger.warning("BioBERT embedding failed: %s", e)
                return None

        if self.embedding_backend == "sbert":
            try:
                embs = self._st.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                return embs.tolist()
            except Exception as e:
                logger.warning("SentenceTransformer failed: %s", e)
                return None

        # Simple text features for development (no ML dependencies)
        if self.embedding_backend == "simple":
            try:
                import re
                simple_features = []
                for text in texts:
                    # Extract simple text statistics as features
                    features = [
                        len(text.split()),  # word count
                        len(text),  # character count
                        text.count('.'),  # sentence count (rough)
                        text.count(','),  # complexity indicator
                        len(re.findall(r'[A-Z][a-z]+', text)),  # capitalized words
                        1 if any(word in text.lower() for word in ['pain', 'severe', 'acute']) else 0,  # severity indicators
                        1 if any(word in text.lower() for word in ['chronic', 'diabetes', 'hypertension']) else 0,  # chronic conditions
                        1 if any(word in text.lower() for word in ['emergency', 'urgent', 'critical']) else 0,  # urgency
                    ]
                    simple_features.append(features)
                return simple_features
            except Exception as e:
                logger.warning("Simple text features failed: %s", e)
                return None

        return None

    def featurize_patient(self, patient_id: str) -> Dict[str, Any]:
        resources = self.fetch_resources_for_patient(patient_id)
        structured = self.extract_structured_features(resources)

        doc_refs = resources.get("document-references", []) or []
        diag_reports = resources.get("diagnostic-reports", []) or []

        texts = self._decode_attachments(doc_refs) + [d.get("conclusion") for d in diag_reports if d.get("conclusion")]
        texts = [t for t in texts if t]

        ner = self._run_spacy_ner(texts)
        emb = self._get_embeddings(texts)
        
        # Process embeddings - compute mean if available
        embedding_mean = None
        if emb:
            try:
                import numpy as np
                embedding_mean = np.mean(np.array(emb), axis=0).tolist()
            except Exception:
                embedding_mean = None

        features = {
            "patient_resource_id": patient_id,
            **structured,
            "ner_entities": ner,
            "embedding_mean": embedding_mean,
        }
        return features

    def featurize_bulk(self, patient_ids: List[str]) -> pd.DataFrame:
        rows = []
        for pid in patient_ids:
            try:
                f = self.featurize_patient(pid)
                # compute mean embedding if available
                if f.get("embeddings"):
                    import numpy as _np

                    mean_emb = _np.mean(_np.array(f.get("embeddings")), axis=0).tolist()
                    f["embedding_mean"] = mean_emb
                else:
                    f["embedding_mean"] = None
                f.pop("embeddings", None)
                rows.append(f)
            except Exception as e:
                logger.exception("Failed patient %s: %s", pid, e)

        return pd.DataFrame(rows)

    def save_features_to_db(self, features: Dict[str, Any]) -> Optional[PatientFeatures]:
        """Save patient features to database if db session is available"""
        if not self.db:
            return None
            
        try:
            # Check if patient already exists
            existing = self.db.query(PatientFeatures).filter(
                PatientFeatures.patient_resource_id == features["patient_resource_id"]
            ).first()
            
            if existing:
                # Update existing record
                for key, value in features.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                patient_features = existing
            else:
                # Create new record
                patient_features = PatientFeatures(**features)
                self.db.add(patient_features)
            
            self.db.commit()
            self.db.refresh(patient_features)
            return patient_features
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error: {e}")
            return None

    def get_features_from_db(self, patient_id: str) -> Optional[PatientFeatures]:
        """Get patient features from database if available"""
        if not self.db:
            return None
            
        try:
            return self.db.query(PatientFeatures).filter(
                PatientFeatures.patient_resource_id == patient_id
            ).first()
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None

    def featurize_patient_with_db(self, patient_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Featurize patient with database caching"""
        # Check database first unless force refresh
        if not force_refresh and self.db:
            cached = self.get_features_from_db(patient_id)
            if cached:
                logger.info(f"Retrieved cached features for patient {patient_id}")
                return cached.to_dict()
        
        # Generate features
        features = self.featurize_patient(patient_id)
        
        # Save to database
        if self.db:
            saved = self.save_features_to_db(features)
            if saved:
                logger.info(f"Saved features for patient {patient_id} to database")
                return saved.to_dict()
        
        return features
