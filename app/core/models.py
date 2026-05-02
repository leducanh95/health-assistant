from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Date, DateTime, Float, ForeignKey, Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    babies: Mapped[list["Baby"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Baby(Base):
    __tablename__ = "babies"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sex: Mapped[str] = mapped_column(String(1), nullable=False)  # 'M' or 'F'
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="babies")
    measurements: Mapped[list["GrowthMeasurement"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    milestones: Mapped[list["MilestoneRecord"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    vaccinations: Mapped[list["Vaccination"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )
    feeding_logs: Mapped[list["FeedingLog"]] = relationship(
        back_populates="baby", cascade="all, delete-orphan"
    )


class GrowthMeasurement(Base):
    __tablename__ = "growth_measurements"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    measured_at: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    length_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    head_circ_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby: Mapped[Baby] = relationship(back_populates="measurements")


class MilestoneRecord(Base):
    __tablename__ = "milestone_records"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    milestone_key: Mapped[str] = mapped_column(String(64), nullable=False)
    achieved_at: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby: Mapped[Baby] = relationship(back_populates="milestones")


class Vaccination(Base):
    __tablename__ = "vaccinations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vaccine_code: Mapped[str] = mapped_column(String(32), nullable=False)
    dose_number: Mapped[int] = mapped_column(Integer, nullable=False)
    given_at: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby: Mapped[Baby] = relationship(back_populates="vaccinations")


class FeedingLog(Base):
    __tablename__ = "feeding_logs"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    baby_id: Mapped[int] = mapped_column(
        ForeignKey("babies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    feeding_type: Mapped[str] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby: Mapped[Baby] = relationship(back_populates="feeding_logs")
