from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Date, String, Boolean, ARRAY

from app.models.base import Base


class PlayerInfo(Base):
    __tablename__ = 'player_info'

    player_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=True)
    birth_place = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    batting_styles = Column(ARRAY(String), nullable=True)
    bowling_styles = Column(ARRAY(String), nullable=True)
    fielding_position = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    national_team = Column(String, nullable=True)
    playing_role = Column(String, nullable=True)


class PlayerInfoResponse(BaseModel):
    name: str = Field(description="The player's name")
    image_url: str = Field(description="The player's image URL")
    national_team: str = Field(description="The player's country")
    dob: str = Field(description="The player's birth date as a string (e.g., '1992-04-18')")
    birth_place: str = Field(description="The player's birth place")
    gender: str = Field(description="The player's gender")
    batting_styles: list[str] = Field(description="The player's batting style (e.g., Right-hand bat)")
    bowling_styles: Optional[list[str]] = Field(default=None, description="The player's bowling style (e.g., Right-arm medium)")
    fielding_position: Optional[str] = Field(default=None, description="The player's fielding position (e.g., Wicket-keeper)")
    playing_role: str = Field(description="The player's role in the team (e.g., Wicket-keeper batsman)")
    is_active: bool = Field(description="Whether the player is active in cricket (e.g., true or false)")

