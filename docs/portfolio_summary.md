# Portfolio Summary

## What This Project Is

A Python + PostgreSQL + dbt + Streamlit pipeline that pulls public records from Seattle's Open Data API and compares them against a small set of apartment candidates from a real apartment search. The goal: answer questions that listing sites don't — like whether there are code complaints nearby, active construction permits, or rental registration issues.

## The Problem

Apartment listing websites are good at showing rent, photos, and amenities. They're not good at showing whether a building has a history of code violations, whether there's a construction project starting next door, or whether the city even has the property registered as a rental. During a real search across Seattle and Shoreline, I found myself checking these things manually and decided to build a pipeline for it.

## How It Works

The pipeline ingests three datasets from Seattle's Socrata API (building permits, code violations, rental registration), stores raw JSON responses in PostgreSQL, and transforms them through dbt into staging, intermediate, and mart layers. Candidate apartments come from a local CSV — the real search notes stay gitignored, while a demo file is committed so the project runs for anyone.

The interesting part is proximity matching: for each apartment with coordinates, the pipeline finds all complaints and permits within 500 meters and creates evidence marts so every count is traceable to specific records.

Shoreline created a useful challenge. It was in my real search area, but Seattle's datasets don't cover it. The pipeline tracks jurisdiction explicitly — Shoreline candidates get a "partial coverage" flag instead of being penalized for missing Seattle records.

## By the Numbers

- 5 apartment candidates (3 Seattle, 2 Shoreline)
- 3 public data sources from Seattle Open Data
- 22 nearby complaint records and 11 nearby permit records found within 500m
- 11 dbt models, 70 dbt tests, 56 Python tests
- Every proximity count traced to individual source records with distances

## What's Missing (Honestly)

- Ingestion is capped at 1,000 rows per dataset — counts are lower bounds
- Distance calculation is flat-earth approximation (fine at this scale, but PostGIS would be better)
- Address matching is exact string comparison — abbreviation differences cause misses
- Shoreline has no local public data integration yet
- No Airflow or cloud deployment yet (Makefile-based orchestration; Airflow is planned future work)
