import os
from src.domain.ports import MemoryPort

COLLECTION = os.environ.get("DATA_BASE", "aurora_conversations")
MAX_HISTORY = 20


class FirestoreMemory(MemoryPort):
    def __init__(self):
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        self._db = None
        if project:
            from google.cloud import firestore

            self._db = firestore.Client(project=project)

    def get_history(self, user_id: str) -> list[dict]:
        if not self._db:
            return []
        try:
            doc = self._db.collection(COLLECTION).document(user_id).get()
            if doc.exists:
                return doc.to_dict().get("history", [])[-MAX_HISTORY:]
            return []
        except Exception:
            return []

    def save_exchange(self, user_id: str, role: str, content: str):
        if not self._db:
            return
        try:
            ref = self._db.collection(COLLECTION).document(user_id)
            doc = ref.get()
            data = doc.to_dict() if doc.exists else {}
            history = data.get("history", [])
            history.append({"role": role, "content": content})
            history = history[-MAX_HISTORY:]
            data["history"] = history
            ref.set(data)
        except Exception:
            pass

    def get_profile(self, user_id: str) -> dict:
        if not self._db:
            return {}
        try:
            doc = self._db.collection(COLLECTION).document(user_id).get()
            if doc.exists:
                data = doc.to_dict()
                return {
                    "name": data.get("name"),
                    "facts": data.get("facts", []),
                    "preferences": data.get("preferences", {}),
                }
            return {}
        except Exception:
            return {}

    def save_profile(self, user_id: str, data: dict):
        if not self._db:
            return
        try:
            ref = self._db.collection(COLLECTION).document(user_id)
            doc = ref.get()
            existing = doc.to_dict() if doc.exists else {}
            existing.update(data)
            ref.set(existing)
        except Exception:
            pass
