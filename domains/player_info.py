from sqlalchemy import Column, String, DateTime, Boolean, ARRAY

from domains.base import Base


class PlayerInfo(Base):
    __tablename__ = 'player_info'

    player_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)
    batting_styles = Column(ARRAY(String), nullable=True)
    bowling_styles = Column(ARRAY(String), nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    national_team = Column(String, nullable=True)
    playing_role = Column(String, nullable=True)
