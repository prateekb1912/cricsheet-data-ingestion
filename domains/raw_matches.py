from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

from domains.base import Base

class RawMatch(Base):
    __tablename__ = 'raw_matches'
    __license__ = """
    This data is provided under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license.

    You are free to:
    - Share: copy and redistribute the material in any medium or format
    - Adapt: remix, transform, and build upon the material

    Under the following terms:
    - Attribution: You must give appropriate credit to Cricsheet (https://cricsheet.org/), 
      provide a link to the license, and indicate if changes were made.
    - NonCommercial: You may not use the material for commercial purposes.
    - ShareAlike: If you remix, transform, or build upon the material, you must distribute 
      your contributions under the same license as the original.

    For more details, please visit: https://creativecommons.org/licenses/by-nc-sa/4.0/
    """

    __table_args__ = {
        'info': {'sort_order': ('created_at', 'desc')}
    }

    match_id = Column(Integer, primary_key=True)
    match_data = Column(JSONB)
    deliveries = Column(JSONB)
    created_at = Column(DateTime, default=datetime.now())

    def __init__(self, match_id, match_data, deliveries):
        self.match_id = match_id
        self.match_data = match_data
        self.deliveries = deliveries

    def __repr__(self):
        return f'<RawMatch(match_id={self.match_id}, created_at={self.created_at})>'
