import unittest
from app.ingestion.chunkers import chunk_document
from app.ingestion.extractors import extract_text
from app.api.api_v1.endpoints.analyze import _parse_income, _parse_age
from app.rag.faiss_store import FAISSStore
import numpy as np

class TestIngestionAndRetrieval(unittest.TestCase):
    def test_chunk_document_semantic(self):
        sample_doc = """--- Page 1 ---
The National Scholarship Scheme provides financial assistance to students from poor families.
The income limit is 2.5 Lakhs per annum.

--- Page 2 ---
Eligible applicants must submit their marksheets and caste certificates before the deadline."""
        
        chunks = chunk_document(sample_doc, chunk_size=200, chunk_overlap=20)
        self.assertGreater(len(chunks), 0)
        # Check that page metadata is extracted
        pages = [c["page_number"] for c in chunks]
        self.assertIn(1, pages)
        self.assertIn(2, pages)

    def test_parse_income_units(self):
        self.assertEqual(_parse_income("family income is 2.5 lakhs per year"), 250000.0)
        self.assertEqual(_parse_income("earning 50k per month"), 50000.0)
        self.assertEqual(_parse_income("salary 180000"), 180000.0)
        self.assertEqual(_parse_income("making 1.2 crore"), 12000000.0)

    def test_parse_age(self):
        dob = _parse_age("I am a 24 yr old student")
        self.assertIsNotNone(dob)
        today = unittest.mock = __import__("datetime").date.today()
        self.assertEqual(today.year - dob.year, 24)

    def test_faiss_store_l2_normalization(self):
        import faiss, tempfile, os
        # Test FAISS IndexFlatIP with isolated temporary index
        dim = 128
        index = faiss.IndexFlatIP(dim)
        vec = np.random.randn(1, dim).astype('float32')
        faiss.normalize_L2(vec)
        index.add(vec)
        self.assertEqual(index.ntotal, 1)
        
        # Search with the same vector
        distances, indices = index.search(vec, 1)
        self.assertEqual(len(distances[0]), 1)
        self.assertAlmostEqual(float(distances[0][0]), 1.0, places=4)

if __name__ == "__main__":
    unittest.main()
