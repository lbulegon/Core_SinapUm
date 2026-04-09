import os
import json
import faiss
from sentence_transformers import SentenceTransformer


class FaissStore:
    def __init__(self, data_dir: str, model_name: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.index_path = os.path.join(self.data_dir, "index.faiss")
        self.map_path = os.path.join(self.data_dir, "id_map.json")
        self.texts_path = os.path.join(self.data_dir, "doc_texts.json")

        self.model = SentenceTransformer(model_name)
        self.id_map: list[str] = []
        self.doc_texts: dict[str, str] = {}
        self.index = None

        self._load()

    def _load(self):
        if os.path.exists(self.map_path):
            with open(self.map_path, "r", encoding="utf-8") as f:
                self.id_map = json.load(f)
        if os.path.exists(self.texts_path):
            with open(self.texts_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.doc_texts = {str(k): str(v) for k, v in data.items()}
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = None

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        with open(self.map_path, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f, ensure_ascii=False, indent=2)
        with open(self.texts_path, "w", encoding="utf-8") as f:
            json.dump(self.doc_texts, f, ensure_ascii=False, indent=2)

    def upsert(self, item_id: str, text: str):
        vec = self.model.encode([text], normalize_embeddings=True).astype("float32")
        dim = vec.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatIP(dim)

        self.index.add(vec)
        self.id_map.append(item_id)
        # Último texto por id (vários vetores com o mesmo id podem existir no índice)
        self.doc_texts[str(item_id)] = text
        self._save()

    def search(self, text: str, k: int = 5, include_text: bool = True):
        if self.index is None or len(self.id_map) == 0:
            return []

        q = self.model.encode([text], normalize_embeddings=True).astype("float32")
        scores, idxs = self.index.search(q, k)

        results = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx == -1:
                continue
            doc_id = self.id_map[idx]
            row: dict = {"id": doc_id, "score": float(score)}
            if include_text:
                row["text"] = self.doc_texts.get(str(doc_id), "")
            results.append(row)
        return results
