import os
from pymongo import MongoClient
from django.conf import settings
import logging

# Setup logger
logger = logging.getLogger(__name__)

# MongoDB Client initialization (using environment variables for flexibility)
def get_mongo_client():
    try:
        # Retrieve MongoDB URI from environment variables or settings
        mongo_uri = os.getenv('MONGO_URI', settings.MONGO_URI)
        
        # Initialize MongoDB client with the URI and connection pooling settings
        client = MongoClient(mongo_uri, maxPoolSize=50, minPoolSize=10)
        
        # Ensure the connection is successful
        client.admin.command('ping')
        logger.info("MongoDB connection established successfully.")
        return client
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

# Establish the connection to the database and access the 'Clusters' database
client = get_mongo_client()
db = client['Clusters']

# Define the helper function to access collections dynamically
def get_collection(collection_name):
    """Get a collection dynamically based on the name."""
    try:
        collection = db[collection_name]
        return collection
    except Exception as e:
        logger.error(f"Error accessing collection {collection_name}: {e}")
        raise
