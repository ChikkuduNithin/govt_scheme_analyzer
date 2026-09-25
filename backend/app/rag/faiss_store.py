import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple

INDEX_FILE = "faiss_index.bin"
META_FILE = "faiss_meta.pkl"

class FAISSStore:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
            self.index = faiss.read_index(INDEX_FILE)
            with open(META_FILE, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatIP(dimension) # Cosine similarity (Inner Product on normalized vectors)
            self.metadata = [] # stores chunk_ids

    def add_embeddings(self, chunk_ids: List[int], embeddings: List[List[float]]):
        if not embeddings: return
        
        # Normalize vectors for cosine similarity
        vectors = np.array(embeddings).astype('float32')
        faiss.normalize_L2(vectors)
        
        self.index.add(vectors)
        self.metadata.extend(chunk_ids)
        self.save()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        if self.index.ntotal == 0: return []
        
        q_vec = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(q_vec)
        
        distances, indices = self.index.search(q_vec, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append((self.metadata[idx], float(dist)))
        return results

    def save(self):
        faiss.write_index(self.index, INDEX_FILE)
        with open(META_FILE, 'wb') as f:
            pickle.dump(self.metadata, f)

faiss_store = FAISSStore()
