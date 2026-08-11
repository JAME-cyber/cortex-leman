# fast-flights — Google Flights Scraper (MIT, v3.0.2)

**Repo:** github.com/AWeirdDev/flights
**Install:** `pip install fast-flights`
**License:** MIT
**Deps:** primp, protobuf, selectolax (3 only, no API key)

## Usage

```python
from fast_flights import (
    FlightQuery, Passengers, create_query, get_flights
)

query = create_query(
    flights=[
        FlightQuery(
            date="2026-09-01",
            from_airport="GVA",
            to_airport="PVG",
            max_stops=1,
            airlines=["LX", "CA"],
            earliest_departure_hour=7,
            latest_departure_hour=18,
            max_duration_minutes=720,
        ),
    ],
    seat="economy",
    trip="one-way",
    passengers=Passengers(adults=1),
    currency="CHF",
    max_price=1500,
)

results = get_flights(query)
for flight in results:
    print(f"{flight.price} CHF — {flight.airlines} — {flight.flights[0].duration}min")
```

## Filters Available

**Per-leg (FlightQuery):**
- `max_stops`, `airlines` (codes ou alliances: "JL", "ONEWORLD")
- `earliest_departure_hour` / `latest_departure_hour` (0-23, local airport time)
- `earliest_arrival_hour` / `latest_arrival_hour`
- `max_duration_minutes`
- `connecting_airports` (["HND", "NRT"])
- `min_layover_minutes` / `max_layover_minutes`
- `less_emissions_only`

**Per-search (create_query):**
- `currency`, `max_price`
- `carry_on_bags`, `checked_bags`
- `hide_separate_and_self_transfer`
- `exclude_basic_economy`

## Output Dataclasses

```python
@dataclass
class Flights:
    type: str           # "multi" or flight type
    price: int          # total price in selected currency
    airlines: list[str] # airline codes
    flights: list[SingleFlight]  # each leg
    carbon: CarbonEmission       # CO2 grams

@dataclass
class SingleFlight:
    from_airport: Airport
    to_airport: Airport
    departure: SimpleDatetime
    arrival: SimpleDatetime
    duration: int       # minutes
    plane_type: str
```

## Use Cases in Import-Export

1. **Air freight estimation** — Pour samples urgentes (DHL alternative) ou petit volume:
   Comparer prix vols cargo vs courier pour estimer le coût de transport sample.
2. **Travel cost in dossier** — Inclure le coût du déplacement sourcing (GVA→PVG/CAN/HKG)
   dans le calcul de rentabilité du projet import.
3. **Price monitoring** — Suivre les variations de prix vols pour identifier
   les fenêtres optimales de déplacement sourcing (saison haute/basse).
4. **Sample shipping alternative** — Pour petits colis, un "courrier accompagné"
   via vol pas cher peut battre DHL (~CHF 150-300).

## Anti-Bot Approach

Le scraper utilise `primp` (client HTTP qui impersonne Chrome 145 + macOS via TLS fingerprinting).
Pas besoin de Playwright/Selenium par défaut. Support proxy optionnel.

**Risque:** Google peut changer le format HTML ou bloquer les requêtes à tout moment.
Ne pas baser un pipeline critique dessus sans monitoring + fallback.

## Related

- Landed cost formula: [landed-cost-formula.md](landed-cost-formula.md)
- Switzerland import rules: [switzerland-import-rules.md](switzerland-import-rules.md)
