# Landed Cost Formula — Complete Reference

## The Full Chain

### Definitions

| Term | Meaning |
|---|---|
| **FOB** | Free On Board — price at supplier's port, loaded onto ship |
| **CIF** | Cost + Insurance + Freight — price delivered to destination port |
| **Landed Cost** | CIF + all duties, taxes, fees, and transport to final warehouse |
| **Landed Cost Net** | Landed Cost minus recoverable VAT |

### Step-by-step

```
1. PRODUCT FOB
   = unit_price × quantity
   
2. + FREIGHT (maritime container or air)
   Container 40HQ (Shenzhen→Basel): ~$4,770-$5,830 (Aug 2026 rate)
   Source: sino-shipping.com (verify current rates)
   
3. + ORIGIN CHARGES
   THC (Terminal Handling Charge): ~$150-200
   Doc fee + BL fee: ~$100-150
   Total: ~$300
   
4. + INSURANCE
   = (FOB + Freight) × 1.10 × 0.003  (all-risk, 110% CIF value)
   
5. = CIF (Cost + Insurance + Freight)

6. + CUSTOMS DUTY
   = CIF_CHF × tariff_rate
   For CH-CN FTA (mobilier): 0% with Form F certificate
   Without origin cert: MFN rate applies (varies by HS code)
   
7. + IMPORT VAT
   Switzerland: (CIF_CHF + duty) × 8.1%
   EU: (CIF_EUR + duty) × 19% (Germany) or country-specific
   This VAT is RECOVERABLE if VAT-registered
   
8. + DESTINATION PORT CHARGES
   THC unloading Basel: ~CHF 350-450
   
9. + CUSTOMS BROKER / TRANSITARY
   ~CHF 200-350 per shipment
   
10. + INLAND TRANSPORT
    Basel→Geneva (200km truck): ~CHF 500-800
    Basel→Lausanne (180km truck): ~CHF 450-700
    
11. = LANDED COST TOTAL (TTC)

12. − RECOVERABLE VAT (if VAT-registered)
    = LANDED COST NET (ex-VAT)
```

### Additional Operational Costs (not in landed cost, but affect margin)

| Cost | Typical % of revenue | Notes |
|---|---|---|
| Marketing | 3-5% | Direct sales, visits, samples |
| Warehouse/storage | CHF 500-1500/month | Depends on volume and duration |
| Sales commission | 2-3% | If using reps |
| Defects/returns | 1-2% | Quality issues, shipping damage |
| Quality inspection | ~$300 flat | SGS/Tetra pre-shipment (amortized over units) |

## Worked Example: Mobilier Restaurant (Foshan → Geneva, Aug 2026)

```
Product: 200 chairs ($25/pc) + 100 tables ($45/pc)
FOB total: $9,500 = CHF 8,360
Volume: 50 m³ (75% of 40HQ container)
Weight: 2,400 kg

Freight:         $5,830 = CHF 5,130
Origin charges:  $300   = CHF 264
Insurance:       $51    = CHF 45
CIF Basel:              CHF 13,535

Duty (ALE CH-CN, 0%):  CHF 0
VAT (8.1% of CIF):     CHF 1,096
Destination charges:   CHF 450
Customs broker:        CHF 250
Inland transport:      CHF 650

LANDED COST TOTAL:     CHF 15,981
− VAT (recoverable):   CHF 1,096
LANDED COST NET:       CHF 14,885

Per unit avg:          CHF 49.6
```

**Key ratio:** Logistics (freight + duty + VAT + transit) = CHF 7,341 = **88% of FOB cost**.

## Margin Reality Check

| FOB price | Landed cost/unit | Sell price (mid) | Sell price (premium) |
|---|---|---|---|
| $25 (CHF 22) | CHF 49.6 | CHF 55 | CHF 75 |
| Gross margin (mid) | | 10% | — |
| Gross margin (premium) | | — | 34% |
| After marketing + storage + defects | | 4% | 24% |

**Lesson:** The "100% markup from FOB" is an illusion. Real margin requires premium positioning or massive volume efficiency.
