# Proximity Evidence Validation

Validated on 2026-06-24 after adding manually verified coordinates for all 5 candidate apartments.

## Apartment Summary

| ID | Apartment | Jurisdiction | Complaints | Permits | Active Permits |
|----|-----------|-------------|:---:|:---:|:---:|
| apt_001 | Verdant Apartments | shoreline | 0 | 2 | 2 |
| apt_002 | Canopy Apartments | shoreline | 0 | 0 | 0 |
| apt_003 | Modera Northgate | seattle | 6 | 4 | 4 |
| apt_004 | Augusta Apartments | seattle | 8 | 2 | 2 |
| apt_005 | Arista Residences | seattle | 8 | 3 | 3 |

## Nearby Complaint Evidence

### Modera Northgate (6 complaints within 500m)

| Record | Address | Open Date | Status | Type | Distance |
|--------|---------|-----------|--------|------|----------|
| 008179-26CP | 11300 5TH AVE NE | 2026-06-12 | Under Investigation | — | 488m |
| 008224-26CP | 525 NE NORTHGATE WAY | 2026-06-12 | Under Investigation | — | 195m |
| 1063266-CT | 401 NE NORTHGATE WAY | 2026-06-10 | Initiated | Noise | 332m |
| 007884-26CP | 10564 5TH AVE NE | 2026-06-09 | Under Investigation | Noise | 101m |
| 007987-26CP | 10212 5TH AVE NE | 2026-06-08 | Under Investigation | Weeds | 428m |

All 5 sampled records are within the 500m radius. Addresses are along 5th Ave NE and Northgate Way — consistent with the Northgate transit area.

### Augusta Apartments (8 complaints within 500m)

| Record | Address | Open Date | Status | Type | Distance |
|--------|---------|-----------|--------|------|----------|
| 008521-26CP | 905 NE 43RD ST | 2026-06-17 | Under Investigation | — | 260m |
| 008231-26CP | 4040 8TH AVE NE | 2026-06-12 | Under Investigation | — | 86m |
| 007649-26CP | 4145 11TH AVE NE | 2026-06-05 | Closed | — | 156m |
| 007657-26CP | 4232 PASADENA PL NE | 2026-06-05 | Under Investigation | — | 282m |
| 007376-26CP | 4303 7TH AVE NE | 2026-06-03 | Under Investigation | — | 365m |

All within 500m. The University District is a dense residential area near UW campus.

### Arista Residences (8 complaints within 500m)

| Record | Address | Open Date | Status | Type | Distance |
|--------|---------|-----------|--------|------|----------|
| 1063319-VI | 4740 21ST AVE NE | 2026-06-17 | Initiated | — | 283m |
| 008421-26CP | 4747 30TH AVE NE | 2026-06-16 | Under Investigation | Noise | 363m |
| 008310-26CP | 4724 22ND AVE NE | 2026-06-15 | Under Investigation | Emergency, Landlord/Tenant | 190m |
| 008246-26CP | 4510 22ND AVE NE | 2026-06-13 | Closed | — | 358m |
| 007818-26CP | 5217 RAVENNA AVE NE | 2026-06-08 | Under Investigation | Landlord/Tenant | 372m |

All within 500m. University Village / Ravenna area — residential with some landlord/tenant and noise complaints.

## Nearby Permit Evidence

### Verdant Apartments (2 permits within 500m — Shoreline boundary case)

| Permit | Address | Issued | Status | Type | Description | Distance |
|--------|---------|--------|--------|------|-------------|----------|
| 7095654-CN | 14050 1ST AVE NE | 2026-06-08 | Issued | Addition/Alteration | Alterations to Lakeside school building | 405m |
| 7080113-CN | 14338 MERIDIAN AVE N | 2026-06-02 | Issued | Addition/Alteration | Alterations and repairs to existing dwelling | 464m |

**Jurisdiction note**: These permits appear in the Seattle building permit dataset because they are within Seattle city limits, near the Seattle/Shoreline boundary. Verdant itself is in Shoreline, but the 500m radius crosses into Seattle territory. This is correct behavior — the platform finds Seattle records near the apartment regardless of which jurisdiction the apartment is in.

### Modera Northgate (4 permits within 500m)

| Permit | Address | Issued | Status | Type | Description | Distance |
|--------|---------|--------|--------|------|-------------|----------|
| 7011643-CN | 10404 ROOSEVELT WAY NE | 2026-06-17 | Issued | Addition/Alteration | Substantial alterations and additions | 400m |
| 7094327-CN | 10701 4TH AVE NE | 2026-06-02 | Issued | Addition/Alteration | Tenant improvements for grocery store (Trader Joe's) | 331m |
| 7040887-CN | 10514 9TH AVE NE | 2026-05-27 | Issued | Addition/Alteration | New one family dwelling | 272m |
| 7037620-CN | 900 NE 105TH ST | 2026-05-20 | Issued | Addition/Alteration | Alteration for two family dwelling | 281m |

Active development around the Northgate transit hub.

### Augusta Apartments (2 permits within 500m)

| Permit | Address | Issued | Status | Type | Description | Distance |
|--------|---------|--------|--------|------|-------------|----------|
| 7106337-CN | 4336 ROOSEVELT WAY NE | 2026-05-27 | Issued | Addition/Alteration | Tenant improvement to existing commercial | 454m |
| 7124768-CN | 1201 NE CAMPUS PKWY | 2026-05-26 | Issued | Addition/Alteration | Alterations to minor telecommunications | 260m |

University District — commercial improvements near campus.

### Arista Residences (3 permits within 500m)

| Permit | Address | Issued | Status | Type | Description | Distance |
|--------|---------|--------|--------|------|-------------|----------|
| 7143772-CN | 4915 25TH AVE NE | 2026-06-17 | Issued | Addition/Alteration | Interior alterations to expand existing | 133m |
| 7138085-CN | 2233 NE 46TH ST | 2026-06-11 | Issued | Addition/Alteration | Repair of site retaining wall | 308m |
| 7142252-CN | 4511 RAVENNA AVE NE | 2026-06-11 | Issued | Addition/Alteration | Repair of site retaining wall | 288m |

Residential area near University Village.

## Suspicious Result Check

- **No records with missing distance**: All evidence records have valid distance calculations.
- **No records exceed 500m**: Maximum observed distance is 488m (Modera complaint 008179-26CP). All within configured radius.
- **Shoreline boundary results**: Verdant's 2 permits are Seattle-jurisdiction records that fall within 500m of the Shoreline apartment. This is expected and correct — the proximity search finds nearby public records regardless of the apartment's jurisdiction.

## Jurisdiction Coverage Summary

| Jurisdiction | Complaints Available | Permits Available | Notes |
|---|---|---|---|
| Seattle | Yes (from Seattle code violations) | Yes (from Seattle building permits) | Subject to 1,000-row sample limit |
| Shoreline | Partial (only if Seattle records exist within 500m of the boundary) | Partial (same boundary caveat) | Shoreline-specific data requires future integration |

- **Canopy** (Shoreline, farther north) shows 0 for both complaints and permits because it is far enough from the Seattle city boundary that no Seattle records fall within 500m.
- **Verdant** (Shoreline, near boundary) shows 2 Seattle permits because the 500m radius crosses into Seattle territory.
- Both results are correct and consistent with the jurisdiction model.
