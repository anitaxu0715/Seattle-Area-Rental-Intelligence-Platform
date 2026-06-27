"""Database connection and query helpers for the Streamlit dashboard."""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def _get_engine():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "seattle_rental")
    user = os.getenv("POSTGRES_USER", "rental_user")
    pw = os.getenv("POSTGRES_PASSWORD", "change_me_in_production")
    return create_engine(f"postgresql://{user}:{pw}@{host}:{port}/{db}")


@st.cache_data(ttl=300)
def load_due_diligence_mart() -> pd.DataFrame:
    engine = _get_engine()
    return pd.read_sql("SELECT * FROM marts.mart_apartment_due_diligence ORDER BY apartment_id", engine)


@st.cache_data(ttl=300)
def load_complaint_evidence() -> pd.DataFrame:
    engine = _get_engine()
    return pd.read_sql(
        "SELECT * FROM marts.mart_nearby_complaint_evidence ORDER BY apartment_id, estimated_distance_meters",
        engine,
    )


@st.cache_data(ttl=300)
def load_permit_evidence() -> pd.DataFrame:
    engine = _get_engine()
    return pd.read_sql(
        "SELECT * FROM marts.mart_nearby_permit_evidence ORDER BY apartment_id, estimated_distance_meters",
        engine,
    )
