import pymongo as pyM
from urllib.parse import quote_plus

escaped_username = quote_plus("")
escaped_password = quote_plus("")
client = pyM.MongoClient(f"")

db = client.test
collections = db.test_collection

histories = db.histories