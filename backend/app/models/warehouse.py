from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


job_posting_skill = Table(
    "job_posting_skill",
    Base.metadata,
    Column("job_posting_id", ForeignKey("fact_job_posting.id"), primary_key=True),
    Column("skill_id", ForeignKey("dim_skill.id"), primary_key=True),
)


class DimCompany(Base):
    __tablename__ = "dim_company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    postings: Mapped[list["FactJobPosting"]] = relationship(back_populates="company")


class DimSkill(Base):
    __tablename__ = "dim_skill"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str | None] = mapped_column(String(120))

    postings: Mapped[list["FactJobPosting"]] = relationship(
        secondary=job_posting_skill,
        back_populates="skills",
    )


class DimLocation(Base):
    __tablename__ = "dim_location"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str | None] = mapped_column(String(120))
    region: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    remote_type: Mapped[str] = mapped_column(String(80), default="unspecified")

    postings: Mapped[list["FactJobPosting"]] = relationship(back_populates="location")

    __table_args__ = (
        UniqueConstraint("country", "region", "city", "remote_type", name="uq_location_grain"),
    )


class DimJobRole(Base):
    __tablename__ = "dim_job_role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title_normalized: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role_family: Mapped[str | None] = mapped_column(String(120))
    seniority: Mapped[str | None] = mapped_column(String(80))

    postings: Mapped[list["FactJobPosting"]] = relationship(back_populates="job_role")


class DimDate(Base):
    __tablename__ = "dim_date"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    year: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)
    week: Mapped[int] = mapped_column(Integer)

    postings: Mapped[list["FactJobPosting"]] = relationship(back_populates="posted_date")


class FactJobPosting(Base):
    __tablename__ = "fact_job_posting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(120), index=True)
    source_job_id: Mapped[str] = mapped_column(String(255), index=True)
    url: Mapped[str | None] = mapped_column(String(1000))
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_currency: Mapped[str | None] = mapped_column(String(12))
    company_id: Mapped[int] = mapped_column(ForeignKey("dim_company.id"))
    location_id: Mapped[int | None] = mapped_column(ForeignKey("dim_location.id"))
    job_role_id: Mapped[int | None] = mapped_column(ForeignKey("dim_job_role.id"))
    posted_date_id: Mapped[int | None] = mapped_column(ForeignKey("dim_date.id"))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    company: Mapped[DimCompany] = relationship(back_populates="postings")
    location: Mapped[DimLocation | None] = relationship(back_populates="postings")
    job_role: Mapped[DimJobRole | None] = relationship(back_populates="postings")
    posted_date: Mapped[DimDate | None] = relationship(back_populates="postings")
    skills: Mapped[list[DimSkill]] = relationship(
        secondary=job_posting_skill,
        back_populates="postings",
    )
    matches: Mapped[list["FactResumeMatch"]] = relationship(back_populates="job_posting")

    __table_args__ = (
        UniqueConstraint("source", "source_job_id", name="uq_job_source_identity"),
    )


class FactResumeMatch(Base):
    __tablename__ = "fact_resume_match"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("fact_job_posting.id"))
    candidate_name: Mapped[str | None] = mapped_column(String(255))
    match_score: Mapped[float] = mapped_column(Float)
    strengths: Mapped[str] = mapped_column(Text, default="[]")
    missing_skills: Mapped[str] = mapped_column(Text, default="[]")
    recommendation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job_posting: Mapped[FactJobPosting] = relationship(back_populates="matches")
