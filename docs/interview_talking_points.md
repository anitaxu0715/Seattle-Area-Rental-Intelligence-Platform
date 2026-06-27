# Interview Talking Points

## 30-Second Pitch

"I was apartment hunting in the Seattle area and kept running into the same problem — listing sites show rent and photos but don't tell you about nearby code complaints, construction permits, or whether the city has the building registered. So I built a pipeline that pulls that public data from Seattle's Open Data API, loads it into PostgreSQL, transforms it with dbt, and shows it in a Streamlit dashboard. The tricky part was that my search included Shoreline, which isn't covered by Seattle's data, so I had to track jurisdiction per apartment."

## 1-Minute Technical Walk-Through

"The pipeline has a Python client that talks to the Socrata API with pagination and retries. Raw responses go into PostgreSQL as JSONB. Then dbt transforms them — staging models pull fields out of JSONB, intermediate models do address matching and proximity search within 500 meters, and marts combine everything into per-apartment profiles. I also built evidence marts so every complaint or permit count links back to the actual records. The dashboard just reads from the marts."

## STAR Format

**Situation**: I was searching for an apartment across Seattle and Shoreline under a deadline. Listing sites didn't show things like nearby code complaints or active construction.

**Task**: Build a data pipeline that brings public records together with my apartment candidates in a way that's honest about what the data does and doesn't cover.

**Action**: I ingested three datasets from Seattle's Socrata API, stored raw JSON in PostgreSQL, built 11 dbt models with 70 tests, added coordinate-based proximity matching, and handled the Seattle/Shoreline jurisdiction split so Shoreline apartments aren't penalized for missing Seattle records. I also built a Streamlit dashboard and kept my real search notes in a gitignored CSV.

**Result**: 5 candidates, 22 nearby complaint records and 11 nearby permit records identified, every count traceable to source records. The dashboard shows it all with jurisdiction context.

## "What was the hardest part?"

"The Seattle/Shoreline boundary. My search included apartments in both cities, but Seattle's Open Data only covers Seattle. One of my Shoreline apartments — Verdant — is close enough to the border that it actually picks up 2 Seattle building permits within 500 meters, while another Shoreline apartment — Canopy — is farther north and gets zero. Both results are correct, but I had to make sure the pipeline explains *why* instead of just showing different numbers."

## "What would you change?"

"PostGIS for distance calculations — the flat-earth math works fine at this latitude but it's not the right long-term approach. And I'd add Shoreline's own public data if I could find a stable API, so Shoreline candidates get the same depth of coverage as Seattle ones."

## "How did you avoid misleading conclusions?"

"Registration non-matches say 'not matched in current sample' instead of 'unregistered.' Shoreline apartments say 'Seattle data is not applicable' instead of 'not found.' And the flag counts are split into three groups — public record, coverage limitation, and renter fit — so a Shoreline coverage flag doesn't get counted as a property problem."

## "Why is this data engineering, not just analysis?"

"Because I built the pipeline, not just the output. There's API client code with retries and pagination, a JSONB raw layer, 11 dbt models with 70 tests, a candidate validation pipeline, coordinate-based proximity joins, evidence traceability, and a privacy-safe local data workflow. The dashboard is the visible part, but the engineering is in the layers underneath."
