import json
import re
import zipfile
import asyncio
from typing import Dict, List
from io import BytesIO

class ZipProcessor:
    """Handles ZIP file processing operations"""
    
    def __init__(self, db_service):
        self.db_service = db_service

    def extract_json_files(self, zip_file: BytesIO) -> Dict[str, dict]:
        """Extract JSON files from ZIP archive"""
        result = {}
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for info in zip_ref.infolist():
                if info.filename.endswith('.json'):
                    content = zip_ref.read(info.filename).decode('utf-8')
                    match_id = info.filename.split('.')[0]
                    result[match_id] = json.loads(content)
        return result

    async def process_zip(self, zip_file: BytesIO) -> List[str]:
        """Process ZIP file and insert matches into database"""
        json_files = self.extract_json_files(zip_file)
        
        # Process matches in batches
        batch_size = 10
        match_ids = list(json_files.keys())
        processed_ids = []

        for i in range(0, len(match_ids), batch_size):
            batch = match_ids[i:i + batch_size]
            results = await asyncio.gather(
                *(self.db_service.insert_match(match_id, json_files[match_id]) 
                  for match_id in batch)
            )
            processed_ids.extend([mid for mid, success in zip(batch, results) if success])

        return processed_ids
