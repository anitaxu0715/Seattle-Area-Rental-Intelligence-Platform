# Project Story

## The Search That Started This Project

In 2025, I needed to find a one-bedroom apartment in the Seattle area under tight time constraints. Like most renters, I started with Zillow, Apartments.com, and individual property websites. These platforms were good at showing the basics: rent, square footage, photos, and listed availability dates.

But as I dug deeper into each candidate, I realized the information that mattered most for a confident rental decision was scattered across completely separate systems — or wasn't easily accessible at all.

## The Information Gap

Here's what I actually needed to evaluate, but couldn't find on any single listing platform:

**Public record signals:**
- Does this building have a history of code complaints or violations?
- Is there active construction nearby that might mean months of noise?
- Is this property properly registered as a rental with the City of Seattle?

**Practical livability gaps:**
- Does the listed availability actually match reality, or is it a stale listing?
- Is the parking situation as clear as the listing implies?
- What does the pet policy actually look like in practice?
- How responsive is the management company?

**Neighborhood context:**
- What's the complaint density in this area?
- How much permit activity is happening nearby?
- Does this neighborhood match my actual constraints, not just a vibe score?

None of this information was hidden or secret. Most of it existed in public datasets maintained by the City of Seattle. But no rental platform connected these dots for renters.

## Turning a Personal Problem Into a Portfolio Project

I realized this gap was a natural fit for a data engineering project. The core challenge wasn't machine learning or web scraping — it was **data integration**: taking structured data from multiple official public sources, combining it with my own apartment candidate list, and producing a clear view of what public records say about each candidate.

My final search spanned Seattle and nearby cities like Shoreline. Different jurisdictions have different public data availability — Seattle has rich open data through its Socrata portal, while Shoreline records may require separate manual review. The platform tracks these differences explicitly rather than treating all locations the same.

This project demonstrates the skills I want to showcase as a data engineer:

- Building reusable API clients for public data sources
- Designing a layered data warehouse (raw, staging, intermediate, marts)
- Writing clean dbt models with proper testing
- Orchestrating a reproducible pipeline
- Producing a practical data product that answers real questions

## Why This Matters Beyond My Search

The renter information gap isn't unique to me. Anyone moving to a new city runs into the same problem — listing sites are built to show apartments, not to show what public records say about the area around them.

This project is a portfolio demonstration that public data can be structured to fill that gap. The flags it generates aren't legal conclusions. They're a way of saying "here's something worth checking before you sign a lease."
