import os
from datetime import date

from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models.document import Document, DocumentChunk
from app.models.eligibility import EligibilityRule
from app.models.scheme import Scheme
from app.models.user import User, UserProfile
import app.models


SCHEME_DATA = [
    {
        "category": "Pension & Social Security",
        "name": "Atal Pension Yojana",
        "department": "Ministry of Finance / PFRDA",
        "state": "Central",
        "description": "Pension scheme for citizens, especially workers in the unorganised sector.",
        "source_url": "https://www.myscheme.gov.in/schemes/apy",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old."),
            ("age", {"field": "age", "operator": "<=", "value": 40}, "Applicant should be 40 years old or below at joining."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Pradhan Mantri Shram Yogi Maandhan",
        "department": "Ministry of Labour & Employment",
        "state": "Central",
        "description": "Voluntary contributory pension scheme for unorganised workers.",
        "source_url": "https://www.myscheme.gov.in/schemes/pm-sym",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old."),
            ("age", {"field": "age", "operator": "<=", "value": 40}, "Applicant should be 40 years old or below."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 180000}, "Monthly income should be up to Rs. 15,000."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "National Pension Scheme for Traders and Self Employed Persons",
        "department": "Ministry of Labour & Employment",
        "state": "Central",
        "description": "Old age protection scheme for retail traders, shopkeepers, and self-employed persons.",
        "source_url": "https://labour.gov.in/nps-traders",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old."),
            ("age", {"field": "age", "operator": "<=", "value": 40}, "Applicant should be 40 years old or below."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Indira Gandhi National Old Age Pension Scheme",
        "department": "Ministry of Rural Development",
        "state": "Central",
        "description": "Pension support for elderly persons from BPL households.",
        "source_url": "https://nsap.nic.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 60}, "Applicant should be 60 years or above."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 150000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Indira Gandhi National Widow Pension Scheme",
        "department": "Ministry of Rural Development",
        "state": "Central",
        "description": "Pension assistance for widows from BPL households.",
        "source_url": "https://nsap.nic.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 40}, "Applicant should be 40 years or above."),
            ("gender", {"field": "gender", "operator": "==", "value": "Female"}, "Applicant should be a woman."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 150000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Indira Gandhi National Disability Pension Scheme",
        "department": "Ministry of Rural Development",
        "state": "Central",
        "description": "Pension assistance for persons with severe or multiple disabilities from BPL households.",
        "source_url": "https://nsap.nic.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be 18 years or above."),
            ("disability", {"field": "disability_status", "operator": "==", "value": True}, "Applicant should be a person with disability."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 150000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Telangana Aasara Old Age Pension",
        "department": "Government of Telangana",
        "state": "Telangana",
        "description": "Monthly pension support for eligible elderly residents of Telangana.",
        "source_url": "https://www.aasara.telangana.gov.in/",
        "rules": [
            ("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."),
            ("age", {"field": "age", "operator": ">=", "value": 57}, "Applicant should meet the old age pension age requirement."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 200000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Telangana Aasara Widow Pension",
        "department": "Government of Telangana",
        "state": "Telangana",
        "description": "Monthly pension support for eligible widows in Telangana.",
        "source_url": "https://www.aasara.telangana.gov.in/",
        "rules": [
            ("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."),
            ("gender", {"field": "gender", "operator": "==", "value": "Female"}, "Applicant should be a woman."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 200000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Telangana Aasara Disabled Pension",
        "department": "Government of Telangana",
        "state": "Telangana",
        "description": "Monthly pension support for eligible persons with disabilities in Telangana.",
        "source_url": "https://www.aasara.telangana.gov.in/",
        "rules": [
            ("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."),
            ("disability", {"field": "disability_status", "operator": "==", "value": True}, "Applicant should be a person with disability."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 200000}, "Applicant should be from a low-income household."),
        ],
    },
    {
        "category": "Pension & Social Security",
        "name": "Employees' Pension Scheme, 1995",
        "department": "EPFO / Ministry of Labour & Employment",
        "state": "Central",
        "description": "Pension benefit for eligible EPFO members.",
        "source_url": "https://www.epfindia.gov.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 58}, "Regular pension generally starts at retirement age."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana",
        "department": "Ministry of Health & Family Welfare",
        "state": "Central",
        "description": "Health assurance cover for poor and vulnerable families.",
        "source_url": "https://pmjay.gov.in/",
        "rules": [
            ("income", {"field": "annual_income", "operator": "<=", "value": 150000}, "Applicant household should be economically vulnerable."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Rajiv Aarogyasri / Cheyutha Health Coverage",
        "department": "Government of Telangana",
        "state": "Telangana",
        "description": "Telangana health coverage for eligible families through empanelled hospitals.",
        "source_url": "https://rajivaarogyasri.telangana.gov.in/",
        "rules": [
            ("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."),
            ("income", {"field": "annual_income", "operator": "<=", "value": 500000}, "Applicant should be from an eligible low-income family."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Employees' State Insurance Scheme",
        "department": "Ministry of Labour & Employment",
        "state": "Central",
        "description": "Social security and medical care scheme for eligible workers.",
        "source_url": "https://www.esic.gov.in/",
        "rules": [
            ("income", {"field": "annual_income", "operator": "<=", "value": 252000}, "Monthly wage should be up to Rs. 21,000."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Central Government Health Scheme",
        "department": "Ministry of Health & Family Welfare",
        "state": "Central",
        "description": "Healthcare facilities for eligible central government employees and pensioners.",
        "source_url": "https://cghs.gov.in/",
        "rules": [
            ("employment", {"field": "employment_status", "operator": "IN", "value": ["Employed", "Pensioner"]}, "Applicant should be an eligible employee or pensioner."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
        "department": "Ministry of Finance",
        "state": "Central",
        "description": "Renewable one-year life insurance cover for eligible bank or post office account holders.",
        "source_url": "https://jansuraksha.gov.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old."),
            ("age", {"field": "age", "operator": "<=", "value": 50}, "Applicant should be 50 years old or below to join."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Pradhan Mantri Suraksha Bima Yojana",
        "department": "Ministry of Finance",
        "state": "Central",
        "description": "Accident insurance cover for eligible bank or post office account holders.",
        "source_url": "https://jansuraksha.gov.in/",
        "rules": [
            ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old."),
            ("age", {"field": "age", "operator": "<=", "value": 70}, "Applicant should be 70 years old or below."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Telangana Employees Health Scheme",
        "department": "Government of Telangana",
        "state": "Telangana",
        "description": "Cashless healthcare scheme for eligible Telangana government employees and pensioners.",
        "source_url": "https://ehf.telangana.gov.in/",
        "rules": [
            ("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be connected to Telangana."),
            ("employment", {"field": "employment_status", "operator": "IN", "value": ["Employed", "Pensioner"]}, "Applicant should be an eligible employee or pensioner."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Niramaya Health Insurance Scheme",
        "department": "National Trust",
        "state": "Central",
        "description": "Health insurance for persons with eligible disabilities covered by the National Trust.",
        "source_url": "https://thenationaltrust.gov.in/",
        "rules": [
            ("disability", {"field": "disability_status", "operator": "==", "value": True}, "Applicant should be a person with disability."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Rashtriya Arogya Nidhi",
        "department": "Ministry of Health & Family Welfare",
        "state": "Central",
        "description": "Financial assistance for poor patients with major life-threatening diseases.",
        "source_url": "https://mohfw.gov.in/",
        "rules": [
            ("income", {"field": "annual_income", "operator": "<=", "value": 150000}, "Applicant should be from a poor household."),
        ],
    },
    {
        "category": "Health & Insurance",
        "name": "Janani Suraksha Yojana",
        "department": "National Health Mission",
        "state": "Central",
        "description": "Safe motherhood intervention promoting institutional deliveries.",
        "source_url": "https://nhm.gov.in/",
        "rules": [
            ("gender", {"field": "gender", "operator": "==", "value": "Female"}, "Applicant should be a woman."),
            ("age", {"field": "age", "operator": ">=", "value": 19}, "Applicant should generally be 19 years or above."),
        ],
    },
]


MORE_SCHEMES = [
    ("Scholarships & Education", "National Means-cum-Merit Scholarship", "Ministry of Education", "Central", "Scholarship for meritorious students from economically weaker sections.", "https://scholarships.gov.in/", [("income", {"field": "annual_income", "operator": "<=", "value": 350000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Central Sector Scheme of Scholarship for College and University Students", "Ministry of Education", "Central", "Merit scholarship for college and university students.", "https://scholarships.gov.in/", [("education", {"field": "education_level", "operator": "IN", "value": ["Class 12", "Undergraduate", "Graduate"]}, "Applicant should be pursuing eligible higher education."), ("income", {"field": "annual_income", "operator": "<=", "value": 450000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Post Matric Scholarship for SC Students", "Ministry of Social Justice & Empowerment", "Central", "Financial support for SC students in post-matric education.", "https://scholarships.gov.in/", [("category", {"field": "category", "operator": "==", "value": "SC"}, "Applicant should belong to SC category."), ("income", {"field": "annual_income", "operator": "<=", "value": 250000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Post Matric Scholarship for ST Students", "Ministry of Tribal Affairs", "Central", "Financial support for ST students in post-matric education.", "https://scholarships.gov.in/", [("category", {"field": "category", "operator": "==", "value": "ST"}, "Applicant should belong to ST category."), ("income", {"field": "annual_income", "operator": "<=", "value": 250000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Post Matric Scholarship for OBC Students", "Ministry of Social Justice & Empowerment", "Central", "Financial support for OBC students in post-matric education.", "https://scholarships.gov.in/", [("category", {"field": "category", "operator": "==", "value": "OBC"}, "Applicant should belong to OBC category."), ("income", {"field": "annual_income", "operator": "<=", "value": 250000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "AICTE Pragati Scholarship for Girls", "AICTE", "Central", "Scholarship to support girls pursuing technical education.", "https://www.aicte-india.org/", [("gender", {"field": "gender", "operator": "==", "value": "Female"}, "Applicant should be a girl student."), ("income", {"field": "annual_income", "operator": "<=", "value": 800000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "AICTE Saksham Scholarship", "AICTE", "Central", "Scholarship for specially abled students pursuing technical education.", "https://www.aicte-india.org/", [("disability", {"field": "disability_status", "operator": "==", "value": True}, "Applicant should be a person with disability."), ("income", {"field": "annual_income", "operator": "<=", "value": 800000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Telangana ePASS Post Matric Scholarship", "Government of Telangana", "Telangana", "Scholarship and fee reimbursement support for eligible Telangana students.", "https://telanganaepass.cgg.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."), ("income", {"field": "annual_income", "operator": "<=", "value": 200000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "Telangana Overseas Scholarship Scheme", "Government of Telangana", "Telangana", "Financial assistance for eligible students pursuing higher education abroad.", "https://telanganaepass.cgg.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."), ("income", {"field": "annual_income", "operator": "<=", "value": 500000}, "Family income should be within the prescribed limit.")]),
    ("Scholarships & Education", "PM YASASVI Scholarship", "Ministry of Social Justice & Empowerment", "Central", "Scholarship support for OBC, EBC and DNT students.", "https://socialjustice.gov.in/schemes", [("category", {"field": "category", "operator": "IN", "value": ["OBC", "EBC", "DNT"]}, "Applicant should belong to an eligible category.")]),
    ("Entrepreneurship & Startups", "Startup India Seed Fund Scheme", "DPIIT", "Central", "Financial assistance for proof of concept, prototype development, product trials, market entry, and commercialization.", "https://www.startupindia.gov.in/", [("employment", {"field": "employment_status", "operator": "IN", "value": ["Self-employed", "Unemployed", "Student"]}, "Applicant should be pursuing a startup or entrepreneurial activity.")]),
    ("Entrepreneurship & Startups", "PM Formalisation of Micro Food Processing Enterprises", "Ministry of Food Processing Industries", "Central", "Support for micro food processing enterprises.", "https://mofpi.gov.in/", [("employment", {"field": "employment_status", "operator": "IN", "value": ["Self-employed", "Unemployed"]}, "Applicant should be interested in self-employment or enterprise.")]),
    ("Entrepreneurship & Startups", "Prime Minister Employment Generation Programme", "Ministry of MSME", "Central", "Credit-linked subsidy programme for generating employment through micro-enterprises.", "https://www.kviconline.gov.in/pmegpeportal/", [("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old.")]),
    ("Entrepreneurship & Startups", "MUDRA Loan under PMMY", "Ministry of Finance", "Central", "Loans for non-corporate, non-farm small and micro enterprises.", "https://www.mudra.org.in/", [("employment", {"field": "employment_status", "operator": "IN", "value": ["Self-employed", "Unemployed", "Employed"]}, "Applicant should be starting or running a small business.")]),
    ("Entrepreneurship & Startups", "Stand-Up India", "Ministry of Finance", "Central", "Bank loans for SC/ST and women entrepreneurs for greenfield enterprises.", "https://www.standupmitra.in/", [("category", {"field": "category", "operator": "IN", "value": ["SC", "ST"]}, "Applicant should be SC/ST, or a woman entrepreneur."), ("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old.")]),
    ("Entrepreneurship & Startups", "PM Vishwakarma", "Ministry of MSME", "Central", "Support for traditional artisans and craftspeople through training, toolkit, credit and market linkage.", "https://pmvishwakarma.gov.in/", [("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be at least 18 years old.")]),
    ("Entrepreneurship & Startups", "Telangana T-IDEA Industrial Incentives", "Government of Telangana", "Telangana", "Industrial incentives for eligible enterprises in Telangana.", "https://invest.telangana.gov.in/policies/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Enterprise should be based in Telangana.")]),
    ("Entrepreneurship & Startups", "Telangana T-PRIDE", "Government of Telangana", "Telangana", "Incentives for SC/ST entrepreneurs in Telangana.", "https://invest.telangana.gov.in/policies/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Enterprise should be based in Telangana."), ("category", {"field": "category", "operator": "IN", "value": ["SC", "ST"]}, "Applicant should belong to SC/ST category.")]),
    ("Entrepreneurship & Startups", "Telangana Startup Ecosystem Support", "Telangana Innovation Cell", "Telangana", "State startup ecosystem, incubation, policy and funding support information.", "https://startup.telangana.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant or startup should be connected to Telangana.")]),
    ("Entrepreneurship & Startups", "Telangana WE Hub Women Entrepreneurship Support", "Government of Telangana", "Telangana", "Entrepreneurship support platform for women-led businesses.", "https://wehub.telangana.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be connected to Telangana."), ("gender", {"field": "gender", "operator": "==", "value": "Female"}, "Applicant should be a woman entrepreneur.")]),
    ("Student Benefits & Livelihood", "National Career Service", "Ministry of Labour & Employment", "Central", "Career, employment and counselling platform for job seekers and employers.", "https://www.ncs.gov.in/", [("age", {"field": "age", "operator": ">=", "value": 14}, "Applicant should be old enough to access career services.")]),
    ("Student Benefits & Livelihood", "Skill India Digital Hub", "Ministry of Skill Development & Entrepreneurship", "Central", "Digital platform for skilling, learning, apprenticeships and jobs.", "https://www.skillindiadigital.gov.in/", [("age", {"field": "age", "operator": ">=", "value": 14}, "Applicant should be old enough for skilling opportunities.")]),
    ("Student Benefits & Livelihood", "PM Internship Scheme", "Ministry of Corporate Affairs", "Central", "Internship opportunities for youth in top companies.", "https://pminternship.mca.gov.in/", [("age", {"field": "age", "operator": ">=", "value": 21}, "Applicant should meet the lower age requirement."), ("age", {"field": "age", "operator": "<=", "value": 24}, "Applicant should meet the upper age requirement.")]),
    ("Student Benefits & Livelihood", "PM-DAKSH Yojana", "Ministry of Social Justice & Empowerment", "Central", "Skill development for eligible SC, OBC, EBC, DNT and sanitation worker communities.", "https://pmdaksh.dosje.gov.in/", [("category", {"field": "category", "operator": "IN", "value": ["SC", "OBC", "EBC", "DNT"]}, "Applicant should belong to an eligible target group.")]),
    ("Student Benefits & Livelihood", "Deen Dayal Upadhyaya Grameen Kaushalya Yojana", "Ministry of Rural Development", "Central", "Skill training and placement support for rural youth.", "https://ddugky.gov.in/", [("age", {"field": "age", "operator": ">=", "value": 15}, "Applicant should meet youth skilling age criteria."), ("income", {"field": "annual_income", "operator": "<=", "value": 300000}, "Applicant should be from a lower-income household.")]),
    ("Student Benefits & Livelihood", "Telangana TASK", "Government of Telangana", "Telangana", "Skill development and employability support for students in Telangana.", "https://www.task.telangana.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be connected to Telangana."), ("employment", {"field": "employment_status", "operator": "IN", "value": ["Student", "Unemployed"]}, "Applicant should be a student or job seeker.")]),
    ("Student Benefits & Livelihood", "Telangana Rajiv Yuva Vikasam", "Government of Telangana", "Telangana", "Self-employment support for eligible unemployed youth from weaker sections.", "https://tgobmms.cgg.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."), ("employment", {"field": "employment_status", "operator": "==", "value": "Unemployed"}, "Applicant should be unemployed.")]),
    ("Student Benefits & Livelihood", "Telangana Minority Finance Corporation Schemes", "Government of Telangana", "Telangana", "Economic support and skill development assistance for eligible minority beneficiaries.", "https://tgobmms.cgg.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."), ("category", {"field": "category", "operator": "==", "value": "Minority"}, "Applicant should belong to a minority community.")]),
    ("Student Benefits & Livelihood", "Telangana BC Welfare Economic Support", "Government of Telangana", "Telangana", "Economic support for eligible Backward Classes beneficiaries.", "https://tgobmms.cgg.gov.in/", [("state", {"field": "state", "operator": "==", "value": "Telangana"}, "Applicant should be a Telangana resident."), ("category", {"field": "category", "operator": "==", "value": "OBC"}, "Applicant should belong to BC/OBC category.")]),
    ("Student Benefits & Livelihood", "Mahatma Gandhi National Rural Employment Guarantee Scheme", "Ministry of Rural Development", "Central", "Demand-based wage employment programme for rural households.", "https://nrega.nic.in/", [("age", {"field": "age", "operator": ">=", "value": 18}, "Applicant should be an adult member of a rural household.")]),
]


def build_doc_text(item):
    rules = " ".join(rule[2] for rule in item["rules"])
    return f"{item['name']} is a {item['category']} scheme. {item['description']} Eligibility notes: {rules}"


def normalize(item):
    category, name, department, state, description, source_url, rules = item
    return {
        "category": category,
        "name": name,
        "department": department,
        "state": state,
        "description": description,
        "source_url": source_url,
        "rules": rules,
    }


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    for filename in ["faiss_index.bin", "faiss_meta.pkl"]:
        if os.path.exists(filename):
            os.remove(filename)

    db = SessionLocal()
    try:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            full_name="Demo User",
            date_of_birth=date(2007, 1, 1),
            gender="Male",
            state="Telangana",
            district="Hyderabad",
            annual_income=200000,
            occupation="Student",
            employment_status="Student",
            education_level="Undergraduate",
            category="OBC",
            disability_status=False,
        )
        db.add(profile)

        all_schemes = SCHEME_DATA + [normalize(item) for item in MORE_SCHEMES]
        for item in all_schemes:
            scheme = Scheme(
                name=item["name"],
                department=item["department"],
                state=item["state"],
                description=f"[{item['category']}] {item['description']}",
                source_url=item["source_url"],
                publication_date=None,
                last_updated_date=date.today(),
                document_version="seed-2026-09-04",
                is_active=True,
            )
            db.add(scheme)
            db.commit()
            db.refresh(scheme)

            for rule_type, condition, description in item["rules"]:
                db.add(EligibilityRule(
                    scheme_id=scheme.id,
                    rule_type=rule_type,
                    condition=condition,
                    description=description,
                ))

            document = Document(
                scheme_id=scheme.id,
                filename=f"{scheme.name[:70].replace(' ', '_')}.html",
                file_type="html",
                status="COMPLETED",
            )
            db.add(document)
            db.commit()
            db.refresh(document)

            db.add(DocumentChunk(
                document_id=document.id,
                scheme_id=scheme.id,
                text=build_doc_text(item),
                page_number=1,
                section=item["category"],
            ))
            db.commit()

        print(f"Seeded {len(all_schemes)} schemes and demo user test@example.com / password123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
