"""
Ground Station V2 - Uses Backend Ingestion Service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ingestion_service import IngestionService

if __name__ == "__main__":
    service = IngestionService(port=5005)
    service.start()
