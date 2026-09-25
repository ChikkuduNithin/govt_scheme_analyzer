import os
import shutil
from datetime import date
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.models.user import User, UserProfile
from app.models.scheme import Scheme
from app.models.eligibility import EligibilityRule
from app.models.document import Document, DocumentChunk
from app.ingestion.embeddings import generate_embeddings
import app.models  # to ensure all models are registered

# 1. Reset Database and FAISS Index
print("Resetting database and FAISS index...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

for f in ["faiss_index.bin", "faiss_meta.pkl"]:
    if os.path.exists(f):
        os.remove(f)

# Re-initialize FAISS store dynamically
from app.rag.faiss_store import FAISSStore
faiss_store = FAISSStore(768)

db = SessionLocal()

# 2. Create User
dummy_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq"
user = User(email="test@example.com", hashed_password=dummy_hash, is_active=True)
db.add(user)
db.commit()
db.refresh(user)

profile = UserProfile(
    user_id=user.id, 
    state="Telangana", 
    date_of_birth=date(2002, 5, 14), 
    annual_income=150000.0,
    category="OBC"
)
db.add(profile)
db.commit()

# 3. Real Scheme Data (30 Schemes: 10 Scholarship, 10 Health, 10 Insurance)
schemes_data = [
    # --- SCHOLARSHIPS (10) ---
    {
        "name": "Post Matric Scholarship for SC/ST/OBC", "dept": "Ministry of Social Justice", "state": "Central",
        "desc": "Financial assistance to SC/ST/OBC students studying at post matriculation or post-secondary stage.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 250000}, "desc": "Family income must be below 2.5 Lakhs"},
            {"type": "category", "cond": {"field": "category", "operator": "IN", "value": ["SC", "ST", "OBC"]}, "desc": "Must belong to SC, ST, or OBC category"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 25}, "desc": "Age must be 25 or below for student scholarship"}
        ],
        "doc": "The objective of the scheme is to appreciably increase the Gross Enrolment Ratio of SC/ST/OBC students in higher education with a focus on those from the poorest households, by providing financial assistance at post-matriculation or post-secondary stage. Scholarships will be paid to the students whose parents/guardians' income from all sources does not exceed Rs. 2,50,000/- per annum."
    },
    {
        "name": "National Means cum Merit Scholarship (NMMS)", "dept": "Ministry of Education", "state": "Central",
        "desc": "Award scholarships to meritorious students of economically weaker sections to arrest their drop out at class VIII.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 350000}, "desc": "Family income must be below 3.5 Lakhs"}
        ],
        "doc": "Under the NMMS Scheme, scholarships are awarded to meritorious students of economically weaker sections to arrest their drop out at class VIII and encourage them to continue study at secondary stage. The income ceiling is Rs. 3,50,000/- per annum. Students must have minimum of 55% marks or equivalent grade in Class VII examination."
    },
    {
        "name": "AICTE Pragati Scholarship for Girls", "dept": "AICTE", "state": "Central",
        "desc": "Empowerment of girls through technical education.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 800000}, "desc": "Family income must be below 8 Lakhs"}
        ],
        "doc": "Pragati is a MHRD Scheme being implemented by AICTE aimed at providing assistance for advancement of Girls pursuing Technical Education. A total of 5,000 scholarships are earmarked every year. The family income should be less than Rs. 8 Lakhs per annum. It provides Rs. 50,000 per annum for every year of study."
    },
    {
        "name": "Swami Vivekananda Merit Cum Means Scholarship", "dept": "Govt of West Bengal", "state": "West Bengal",
        "desc": "Assist meritorious students belonging to economically backward families in West Bengal.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 250000}, "desc": "Family income must be below 2.5 Lakhs"},
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "West Bengal"}, "desc": "Must be a resident of West Bengal"}
        ],
        "doc": "To assist the meritorious students having economically backward families in the State of West Bengal. The income criteria to apply under the Scheme is Rs. 2,50,000/- per annum. Scholarship amounts vary from Rs. 1000 to Rs. 8000 per month depending on the course."
    },
    {
        "name": "Begum Hazrat Mahal National Scholarship", "dept": "Ministry of Minority Affairs", "state": "Central",
        "desc": "Scholarship for meritorious girl students belonging to minority communities.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 200000}, "desc": "Family income must be below 2 Lakhs"},
            {"type": "category", "cond": {"field": "category", "operator": "IN", "value": ["Minority"]}, "desc": "Must belong to Minority community"}
        ],
        "doc": "This scheme provides financial assistance to meritorious girl students belonging to national minorities (Muslim, Christian, Jain, Buddhist, Sikh, Parsi) to continue their education. Income criteria: Parents/guardian income not to exceed Rs. 2.00 lakh per annum. Awarded for classes 9th to 12th."
    },
    {
        "name": "Prime Minister's Scholarship Scheme (PMSS)", "dept": "Kendriya Sainik Board", "state": "Central",
        "desc": "Encourage higher technical and professional education for wards of Ex-Servicemen / Ex-Coast Guard personnel.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 25}, "desc": "Usually for students, age should be reasonable (<= 25)."}
        ],
        "doc": "The PMSS introduced in 2006 to encourage higher technical and professional education for the dependent wards of Ex-Servicemen / Ex-Coast Guard personnel and their widows. Provides scholarships for courses like B.Tech, BDS, MBBS, B.Ed, BBA, BCA, etc. Minimum 60% marks required in MEQ."
    },
    {
        "name": "ePASS Telangana Post Matric Scholarship", "dept": "Govt of Telangana", "state": "Telangana",
        "desc": "Electronic Payment & Application System of Scholarships for students in Telangana.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Telangana"}, "desc": "Must be a resident of Telangana"},
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 200000}, "desc": "Income less than 2 Lakhs"}
        ],
        "doc": "ePASS (Electronic Payment & Application System of Scholarships) provides Post Matric Scholarships to SC/ST/BC/Disabled/Minority students of Telangana. Income ceiling is Rs. 2 Lakhs for SC/ST and Minorities, and Rs. 1.5 Lakhs for BC/EBC in rural areas. Reimburses tuition fees and maintenance charges."
    },
    {
        "name": "Chief Minister's Overseas Scholarship Scheme", "dept": "Govt of Telangana", "state": "Telangana",
        "desc": "Financial assistance to minority/SC/ST/BC students for pursuing higher studies abroad.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Telangana"}, "desc": "Must be a resident of Telangana"},
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 500000}, "desc": "Income less than 5 Lakhs"}
        ],
        "doc": "Provides financial assistance to eligible minority, SC, ST, and BC graduates to pursue Post Graduate and Ph.D. courses in foreign universities. Maximum grant is Rs. 20 Lakhs. Family income should be less than Rs. 5 Lakhs per annum."
    },
    {
        "name": "National Fellowship for OBC", "dept": "Ministry of Social Justice", "state": "Central",
        "desc": "Financial assistance to OBC students for pursuing higher education leading to M.Phil and Ph.D degrees.",
        "rules": [
            {"type": "category", "cond": {"field": "category", "operator": "==", "value": "OBC"}, "desc": "Must be OBC category"}
        ],
        "doc": "The scheme aims at providing financial assistance to the OBC students in obtaining quality higher education leading to degrees such as M.Phil and Ph.D in universities, research institutions and scientific institutions. It provides JRF and SRF fellowships."
    },
    {
        "name": "INSPIRE Scholarship for Higher Education (SHE)", "dept": "Department of Science & Technology", "state": "Central",
        "desc": "Scholarship to attract talented youth to study natural and basic sciences.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 17}, "desc": "Age must be >= 17 for college"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 22}, "desc": "Age must be <= 22 for undergraduate start"}
        ],
        "doc": "Innovation in Science Pursuit for Inspired Research (INSPIRE) offers 10,000 scholarships every year @ Rs. 80,000/- each for undertaking Bachelor and Masters level education in the Natural & Basic sciences. Eligible applicants must be in top 1% of 12th board examinations."
    },

    # --- HEALTH BENEFITS (10) ---
    {
        "name": "Ayushman Bharat PM-JAY", "dept": "Ministry of Health", "state": "Central",
        "desc": "World's largest health insurance scheme fully financed by the government.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 100000}, "desc": "Targeted at BPL and vulnerable families (proxy income < 1L)"}
        ],
        "doc": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB PM-JAY) provides a health cover of Rs. 5 lakhs per family per year for secondary and tertiary care hospitalization to over 12 crores poor and vulnerable families. There is no cap on family size, age or gender."
    },
    {
        "name": "Aarogyasri Health Care Trust", "dept": "Govt of Telangana", "state": "Telangana",
        "desc": "Provides quality healthcare to the poor.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Telangana"}, "desc": "Must be a resident of Telangana"},
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 500000}, "desc": "Income less than 5 Lakhs (BPL proxy)"}
        ],
        "doc": "Aarogyasri is the flagship scheme of all health initiatives of the State Government with a mission to provide quality healthcare to the poor. It provides financial protection to families living below poverty line up to Rs. 5 lakhs in a year for the treatment of serious ailments requiring hospitalization and surgery."
    },
    {
        "name": "Central Government Health Scheme (CGHS)", "dept": "Ministry of Health", "state": "Central",
        "desc": "Comprehensive medical care to Central Government employees and pensioners.",
        "rules": [
            # In a real engine we'd have employment_type=="Central Govt", using age as proxy here or leaving empty
        ],
        "doc": "CGHS provides comprehensive health care facilities for the Central Govt. employees and pensioners and their dependents residing in CGHS covered cities. It provides dispensary services, domiciliary care, and hospitalization."
    },
    {
        "name": "Employees' State Insurance Scheme (ESIS)", "dept": "Ministry of Labour", "state": "Central",
        "desc": "Multi-dimensional social security system for workers.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 252000}, "desc": "Monthly wage limit is Rs 21000 (Annual ~2.5L)"}
        ],
        "doc": "ESI is a self-financing social security and health insurance scheme for Indian workers. The wage limit for coverage under the Act is Rs. 21,000/- per month. It provides full medical care to the employee and their family from day one of entering insurable employment."
    },
    {
        "name": "Chief Minister's Comprehensive Health Insurance Scheme", "dept": "Govt of Tamil Nadu", "state": "Tamil Nadu",
        "desc": "Health insurance for residents of Tamil Nadu.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Tamil Nadu"}, "desc": "Must be a resident of Tamil Nadu"},
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 120000}, "desc": "Family income less than 1.2 Lakhs"}
        ],
        "doc": "CMCHIS provides life-saving medical treatments for the poor families in Tamil Nadu. The scheme provides health coverage up to Rs. 5 Lakhs per family per year on a floater basis. Family annual income should be less than Rs. 1,20,000/-."
    },
    {
        "name": "Mahatma Jyotiba Phule Jan Arogya Yojana", "dept": "Govt of Maharashtra", "state": "Maharashtra",
        "desc": "Health insurance scheme for residents of Maharashtra.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Maharashtra"}, "desc": "Must be a resident of Maharashtra"}
        ],
        "doc": "MJPJAY provides health insurance coverage to families holding Yellow, Orange, and Antyodaya Anna Yojana (AAY) ration cards in Maharashtra. Provides coverage of Rs. 1.5 Lakhs per family per year. Kidney transplant limit is Rs. 2.5 Lakhs."
    },
    {
        "name": "Mukhyamantri Chiranjeevi Swasthya Bima Yojana", "dept": "Govt of Rajasthan", "state": "Rajasthan",
        "desc": "Universal health coverage for all families in Rajasthan.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Rajasthan"}, "desc": "Must be a resident of Rajasthan"}
        ],
        "doc": "A landmark scheme in Rajasthan providing health insurance of up to Rs. 25 Lakhs to every family in the state. Free for NFSA, SECC, SMF categories. Others can join by paying a nominal premium of Rs. 850 per year."
    },
    {
        "name": "Biju Swasthya Kalyan Yojana", "dept": "Govt of Odisha", "state": "Odisha",
        "desc": "Health protection to all families in Odisha.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Odisha"}, "desc": "Must be a resident of Odisha"}
        ],
        "doc": "BSKY provides universal health coverage, with special emphasis on the health protection of economically vulnerable families. Free health services at all state govt healthcare facilities. Up to Rs. 5 Lakh per family (Rs. 10 Lakh for women) in empanelled private hospitals for BPL."
    },
    {
        "name": "Rashtriya Arogya Nidhi (RAN)", "dept": "Ministry of Health", "state": "Central",
        "desc": "Financial assistance to patients living below poverty line suffering from major life-threatening diseases.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 100000}, "desc": "Must be below poverty line"}
        ],
        "doc": "RAN provides financial assistance to patients living below poverty line who are suffering from major life-threatening diseases (like cancer, rare diseases) to receive medical treatment at super specialty Government hospitals. Maximum assistance is up to Rs. 15 Lakhs."
    },
    {
        "name": "Janani Suraksha Yojana (JSY)", "dept": "National Health Mission", "state": "Central",
        "desc": "Safe motherhood intervention under the National Health Mission.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 19}, "desc": "Must be 19 or older for benefits"}
        ],
        "doc": "JSY is a safe motherhood intervention under NHM. It aims to reduce maternal and neonatal mortality by promoting institutional delivery among poor pregnant women. It provides cash assistance to mothers in Low Performing States irrespective of age and number of children."
    },

    # --- INSURANCE (10) ---
    {
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)", "dept": "Ministry of Finance", "state": "Central",
        "desc": "One year life insurance scheme renewable from year to year offering coverage for death.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 50}, "desc": "Maximum age to join is 50"}
        ],
        "doc": "PMJJBY is a life insurance scheme available to people in the age group of 18 to 50 years having a bank account who give their consent to join/enable auto-debit. It offers a life cover of Rs. 2 Lakhs at a premium of Rs. 436 per annum. The life cover is available up to age 55."
    },
    {
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)", "dept": "Ministry of Finance", "state": "Central",
        "desc": "Accident insurance scheme offering accidental death and disability cover.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 70}, "desc": "Maximum age is 70"}
        ],
        "doc": "PMSBY is available to people in the age group 18 to 70 years with a bank account. It provides accidental death and full disability cover of Rs. 2 Lakhs and Rs. 1 Lakh for partial disability. The premium is Rs. 20 per annum, auto-debited from the account."
    },
    {
        "name": "Atal Pension Yojana (APY)", "dept": "PFRDA", "state": "Central",
        "desc": "Pension scheme focused on the unorganized sector workers.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 40}, "desc": "Maximum age to join is 40"}
        ],
        "doc": "APY is a guaranteed pension scheme administered by PFRDA. Any Indian citizen aged 18-40 years with a savings bank account can join. It provides a guaranteed minimum monthly pension of Rs. 1000 to Rs. 5000 from the age of 60 years, depending on the contributions."
    },
    {
        "name": "Aam Aadmi Bima Yojana (AABY)", "dept": "LIC", "state": "Central",
        "desc": "Social security scheme for rural landless households.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 59}, "desc": "Maximum age is 59"}
        ],
        "doc": "AABY provides insurance cover to the head of the family or earning member of rural landless households. Covers natural death (Rs. 30,000), accidental death (Rs. 75,000). Also provides a scholarship of Rs. 100 per month for up to 2 children studying in classes 9 to 12."
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)", "dept": "Ministry of Agriculture", "state": "Central",
        "desc": "Crop insurance scheme in line with One Nation - One Scheme theme.",
        "rules": [
            # In real system, occupation == "Farmer"
        ],
        "doc": "PMFBY provides comprehensive insurance cover against failure of the crop thus helping in stabilizing the income of the farmers. The premium paid by farmers is 2% for Kharif crops, 1.5% for Rabi crops, and 5% for commercial/horticultural crops. The balance premium is paid by the Government."
    },
    {
        "name": "Rythu Bima", "dept": "Govt of Telangana", "state": "Telangana",
        "desc": "Farmers Group Life Insurance Scheme by Govt of Telangana.",
        "rules": [
            {"type": "state", "cond": {"field": "state", "operator": "==", "value": "Telangana"}, "desc": "Must be a resident of Telangana"},
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 59}, "desc": "Maximum age is 59"}
        ],
        "doc": "The main objective of the Farmers Group Life Insurance Scheme (Rythu Bima) is to provide financial relief and social security to the family members/dependents in case of loss of farmer's life. Provides Rs. 5 Lakhs insured amount directly to the nominee's account within 10 days of death."
    },
    {
        "name": "Mahatma Gandhi Bunkar Bima Yojana", "dept": "Ministry of Textiles", "state": "Central",
        "desc": "Insurance cover to handloom weavers.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 18}, "desc": "Minimum age is 18"},
            {"type": "age", "cond": {"field": "age", "operator": "<=", "value": 59}, "desc": "Maximum age is 59"}
        ],
        "doc": "The objective of the scheme is to provide enhanced insurance cover to the handloom weavers in the case of natural as well as accidental death. Covers natural death (Rs. 60,000), accidental death (Rs. 1,50,000). The weaver should be between 18 and 59 years of age."
    },
    {
        "name": "Senior Citizen Health Insurance Scheme (SCHIS)", "dept": "Ministry of Health", "state": "Central",
        "desc": "Provides additional health insurance to senior citizens.",
        "rules": [
            {"type": "age", "cond": {"field": "age", "operator": ">=", "value": 60}, "desc": "Must be a senior citizen (Age >= 60)"}
        ],
        "doc": "SCHIS provides easy access to curative geriatric health care services by providing additional cover of Rs. 30,000 per senior citizen in the eligible families already covered under Rashtriya Swasthya Bima Yojana (RSBY). Available for citizens aged 60 and above."
    },
    {
        "name": "Universal Health Insurance Scheme (UHIS)", "dept": "Public Sector Insurance Companies", "state": "Central",
        "desc": "Health insurance for BPL and APL families.",
        "rules": [
            {"type": "income", "cond": {"field": "annual_income", "operator": "<=", "value": 150000}, "desc": "Targeted mostly at lower incomes (BPL proxy)"}
        ],
        "doc": "UHIS offers health care cover to APL and BPL families. The premium for BPL families is highly subsidized by the Government. It covers hospitalization benefits up to Rs. 30,000, accidental death cover of Rs. 25,000 to the earning head, and compensation due to loss of earning."
    },
    {
        "name": "Niramaya Health Insurance Scheme", "dept": "National Trust", "state": "Central",
        "desc": "Health insurance for persons with Autism, Cerebral Palsy, Mental Retardation and Multiple Disabilities.",
        "rules": [
            # Real engine: disability == True
        ],
        "doc": "Niramaya scheme provides affordable Health Insurance to persons with Autism, Cerebral Palsy, Mental Retardation and Multiple Disabilities. Insurance cover up to Rs. 1.0 Lakh. The scheme operates on a pan-India basis. Enrolment fee is heavily subsidized for BPL families."
    }
]

print(f"Preparing to insert {len(schemes_data)} schemes and generate real embeddings...")

texts_to_embed = []
for scheme_data in schemes_data:
    scheme = Scheme(
        name=scheme_data["name"],
        department=scheme_data["dept"],
        state=scheme_data["state"],
        description=scheme_data["desc"],
        is_active=True
    )
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    
    for r in scheme_data["rules"]:
        rule = EligibilityRule(
            scheme_id=scheme.id,
            rule_type=r["type"],
            condition=r["cond"],
            description=r["desc"]
        )
        db.add(rule)
    db.commit()
    
    doc = Document(scheme_id=scheme.id, filename=f"{scheme.name.replace(' ', '_')}.pdf", file_type="pdf", status="COMPLETED")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    chunk = DocumentChunk(
        document_id=doc.id,
        scheme_id=scheme.id,
        text=scheme_data["doc"],
        page_number=1,
        section="Overview"
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    
    # Save mapping for later embedding assignment
    texts_to_embed.append((chunk.id, scheme_data["doc"]))

# Batch generate embeddings via OpenAI to save time and API overhead
# OpenAI text-embedding-3-small allows up to 8192 items in one request!
print("Sending batch request to OpenAI for embeddings...")
just_texts = [item[1] for item in texts_to_embed]
embeddings = generate_embeddings(just_texts)

chunk_ids = [item[0] for item in texts_to_embed]
faiss_store.add_embeddings(chunk_ids, embeddings)

print("Successfully populated database with 30 real government schemes and their Gemini Vector Embeddings!")
