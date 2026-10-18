import logging
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from backend.config import Config

logger = logging.getLogger("krushisetu.database")

class Database:
    _instance = None
    _client = None
    _db = None
    _is_connected = False
    _mock_collections = {}

    COLLECTIONS = [
        "users",
        "products",
        "orders",
        "reviews",
        "messages",
        "market_data",
        "weather_data",
        "soil_data",
        "disease_results",
        "predictions",
        "price_predictions",
        "transport_estimates",
        "admin_logs",
        "system_events"
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize MongoDB connection and set up indices."""
        for col in self.COLLECTIONS:
            self._mock_collections[col] = []

        try:
            self._client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=2500,
                connectTimeoutMS=2500
            )
            # Test connection with ping
            self._client.admin.command('ping')
            self._db = self._client[Config.DB_NAME]
            self._is_connected = True
            self._create_indexes()
            logger.info("MongoDB connection established successfully.")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self._is_connected = False
            self._db = None
            logger.warning(f"MongoDB not reachable ({e}). Operating in resilient fallback mode.")

    def _create_indexes(self):
        """Create unique and search indexes for collections."""
        if self._is_connected and self._db is not None:
            try:
                # Unique indexes for user authentication
                self._db.users.create_index([("email", ASCENDING)], unique=True, sparse=True)
                self._db.users.create_index([("phone", ASCENDING)], unique=True, sparse=True)
                # Performance indexes for products and orders
                self._db.products.create_index([("category", ASCENDING)])
                self._db.products.create_index([("farmer_id", ASCENDING)])
                self._db.orders.create_index([("farmer_id", ASCENDING)])
                self._db.orders.create_index([("buyer_id", ASCENDING)])
                # Index for administrative audit logs
                self._db.admin_logs.create_index([("created_at", ASCENDING)])
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")

    @property
    def is_connected(self):
        return self._is_connected

    def check_health(self) -> dict:
        """Check active connectivity to MongoDB without exposing secrets."""
        if not self._is_connected or self._client is None:
            return {"connected": False, "status": "disconnected"}
        try:
            self._client.admin.command('ping')
            return {"connected": True, "status": "connected"}
        except Exception:
            return {"connected": False, "status": "unreachable"}

    def get_collection(self, name: str):
        """Return collection object or safe collection wrapper."""
        if name not in self.COLLECTIONS:
            raise ValueError(f"Collection '{name}' is not registered in KrushiSetu architecture.")
        
        if self._is_connected and self._db is not None:
            return self._db[name]
        return MockCollection(name, self._mock_collections[name])

class MockCollection:
    """In-memory resilient mock collection with MongoDB-compatible query interface."""
    def __init__(self, name: str, store: list):
        self.name = name
        self.store = store

    def _matches(self, doc, query):
        if not query:
            return True
        for k, v in query.items():
            if k == "$or" and isinstance(v, list):
                if not any(self._matches(doc, sub_q) for sub_q in v):
                    return False
            elif k == "_id" or k == "id":
                doc_id = str(doc.get("_id") or doc.get("id") or "")
                target_id = str(v)
                if doc_id != target_id:
                    return False
            elif doc.get(k) != v:
                return False
        return True

    def insert_one(self, doc: dict):
        import uuid
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        if "id" not in doc:
            doc["id"] = str(doc["_id"])
        new_doc = doc.copy()
        self.store.append(new_doc)
        class InsertResult:
            inserted_id = new_doc["_id"]
        return InsertResult()

    def find_one(self, query: dict = None, projection: dict = None):
        for doc in self.store:
            if self._matches(doc, query):
                res = doc.copy()
                if projection:
                    if projection.get("password_hash") == 0:
                        res.pop("password_hash", None)
                    if projection.get("password") == 0:
                        res.pop("password", None)
                return res
        return None

    def find(self, query: dict = None, projection: dict = None):
        results = []
        for doc in self.store:
            if self._matches(doc, query):
                res = doc.copy()
                if projection:
                    if projection.get("password_hash") == 0:
                        res.pop("password_hash", None)
                results.append(res)
        return results

    def update_one(self, query: dict, update: dict):
        for idx, doc in enumerate(self.store):
            if self._matches(doc, query):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        self.store[idx][k] = v
                class UpdateResult:
                    matched_count = 1
                    modified_count = 1
                return UpdateResult()
        class UpdateResultZero:
            matched_count = 0
            modified_count = 0
        return UpdateResultZero()

    def delete_one(self, query: dict):
        for idx, doc in enumerate(self.store):
            if self._matches(doc, query):
                self.store.pop(idx)
                class DeleteResult:
                    deleted_count = 1
                return DeleteResult()
        class DeleteResultZero:
            deleted_count = 0
        return DeleteResultZero()

    def count_documents(self, query: dict = None):
        if not query:
            return len(self.store)
        return sum(1 for doc in self.store if self._matches(doc, query))

    def drop(self):
        self.store.clear()

def make_id_query(doc_id: str) -> dict:
    """Build a query matching id whether stored as ObjectId, string _id, or id field."""
    if not doc_id:
        return {"_id": None}
    str_id = str(doc_id)
    queries = [{"id": str_id}, {"_id": str_id}]
    try:
        from bson import ObjectId
        if ObjectId.is_valid(str_id):
            queries.append({"_id": ObjectId(str_id)})
    except Exception:
        pass
    return {"$or": queries}

db_instance = Database()

def get_db():
    return db_instance
