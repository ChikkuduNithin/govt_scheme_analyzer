import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple
from app.core.config import settings

class FAISSStore:
    def __init__(self, dimension: int = None):
        self.dimension = dimension or settings.EMBEDDING_DIM
        self.index_path = settings.FAISS_INDEX_PATH
        self.meta_path = settings.FAISS_META_PATH
        self._load_or_initialize()

    def _load_or_initialize(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                loaded_index = faiss.read_index(self.index_path)
                if loaded_index.d == self.dimension:
                    self.index = loaded_index
                    with open(self.meta_path, 'rb') as f:
                        self.metadata = pickle.load(f)
                    return
                else:
                    print(f"FAISS index dimension mismatch ({loaded_index.d} vs expected {self.dimension}). Reinitializing...")
            except Exception as e:
                print(f"Error loading existing FAISS index: {e}. Reinitializing...")
                
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []

    def add_embeddings(self, chunk_ids: List[int], embeddings: List[List[float]]):
        if not embeddings or not chunk_ids:
            return
        
        vectors = np.array(embeddings).astype('float32')
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match FAISS dimension {self.dimension}")
            
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.metadata.extend(chunk_ids)
        self.save()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        if self.index.ntotal == 0 or not query_embedding:
            return []
        
        q_vec = np.array([query_embedding]).astype('float32')
        if q_vec.shape[1] != self.dimension:
            print(f"Query vector dimension {q_vec.shape[1]} does not match index {self.dimension}")
            return []
            
        faiss.normalize_L2(q_vec)
        distances, indices = self.index.search(q_vec, min(top_k, self.index.ntotal))
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))
        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'wb') as f:
            pickle.dump(self.metadata, f)

faiss_store = FAISSStore()
