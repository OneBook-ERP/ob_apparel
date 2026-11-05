# TM01: Data Dictionary & Member B Seed Data Guide

> **Module:** TM01 — Textile Setup and Masters  
> **App:** `ob_apparel`  
> **Target Audience:** Member B (Functional Lead & QA Specialist)  
> **Purpose:** Detailed field directory, standard Indian mill seed datasets, and desk testing guidelines.

---

## 1. Seed Data Catalog for Indian Textile Mills

Textile manufacturing hubs in India (Tirupur for knits, Surat for synthetics/viscose, Coimbatore/Erode for weaving and spinning) operate with specific standard counts, blends, and processes.

### 1.1. Standard Fibre Types (`seed_data/fibre_type.csv`)
| Fibre Code | Fibre Name | Category | Density (g/cm³) | Moisture Regain (%) | HSN Code |
|---|---|---|---|---|---|
| `COT` | 100% Shankar-6 Cotton | Natural | 1.54 | 8.5% | 5201 |
| `POLY` | Semi Dull Polyester Staple | Synthetic | 1.38 | 0.4% | 5503 |
| `VIS` | Bright Viscose Rayon | Regenerated | 1.52 | 11.0% | 5504 |
| `MOD` | Micro Modal | Regenerated | 1.51 | 12.5% | 5504 |
| `ELAS` | Spandex / Elastane | Synthetic | 1.20 | 1.5% | 5402 |
| `LIN` | French Flax Linen | Natural | 1.50 | 12.0% | 5301 |
| `RPOLY` | Post-Consumer Recycled Polyester | Synthetic | 1.38 | 0.4% | 5503 |

### 1.2. Standard Indian Yarn Counts (`seed_data/yarn_count_master.csv`)
| Count Code | Count Name | System | Nominal Value | Expected Ne | Expected Denier | Expected Tex |
|---|---|---|---|---|---|---|
| `20S_NE` | 20s Ne Carded Weft | Ne | 20.0 | 20.00 | 265.75 | 29.53 |
| `24S_NE` | 24s Ne Combed Hosiery | Ne | 24.0 | 24.00 | 221.46 | 24.60 |
| `30S_NE` | 30s Ne Combed Hosiery | Ne | 30.0 | 30.00 | 177.17 | 19.68 |
| `34S_NE` | 34s Ne Combed Warp | Ne | 34.0 | 34.00 | 156.32 | 17.37 |
| `40S_NE` | 40s Ne Compact Combed | Ne | 40.0 | 40.00 | 132.88 | 14.76 |
| `60S_NE` | 60s Ne Superfine Combed | Ne | 60.0 | 60.00 | 88.58 | 9.84 |
| `80S_NE` | 80s Ne Giza Compact | Ne | 80.0 | 80.00 | 66.44 | 7.38 |
| `75D_POLY` | 75 Denier / 36 Filament Poly | Denier | 75.0 | 70.87 | 75.00 | 8.33 |
| `150D_POLY` | 150 Denier / 48 Filament Textured | Denier | 150.0 | 35.43 | 150.00 | 16.67 |
| `30D_SPDX` | 30 Denier Bare Spandex | Denier | 30.0 | 177.17 | 30.00 | 3.33 |

### 1.3. Standard Yarn Blends (`seed_data/yarn_blend_master.csv`)
| Blend Code | Blend Name | Component Fibres & Percentages |
|---|---|---|
| `100_COT` | 100% Combed Cotton | `COT`: 100.0% |
| `CP_60_40` | 60/40 Cotton Polyester (CVC) | `COT`: 60.0%, `POLY`: 40.0% |
| `PC_65_35` | 65/35 Polyester Cotton (PC) | `POLY`: 65.0%, `COT`: 35.0% |
| `COT_ELAS_95_5` | 95/5 Cotton Spandex / Lycra | `COT`: 95.0%, `ELAS`: 5.0% |
| `PV_65_35` | 65/35 Polyester Viscose Suitings | `POLY`: 65.0%, `VIS`: 35.0% |
| `MOD_COT_50_50` | 50/50 MicroModal Cotton Luxury | `MOD`: 50.0%, `COT`: 50.0% |

### 1.4. Standard Fabric Types & Relaxation Hours (`seed_data/fabric_type.csv`)
| Code | Name | Category | Min Relaxation (Hours) | Industry Note |
|---|---|---|---|---|
| `SJ` | Single Jersey (T-Shirts) | Knit | 24.0 | Relax on pallets or rolling bins |
| `RIB11` | 1x1 Rib (Collars & Cuffs) | Knit | 24.0 | High elasticity, minimal tension |
| `RIB22` | 2x2 Rib (Heavy Trims) | Knit | 24.0 | Crimp relaxation required |
| `INTL` | Interlock (Polo & Polo Collars) | Knit | 24.0 | Double knit balance |
| `FLC2T` | 2-Thread Fleece (Hoodies) | Knit | 36.0 | Elevated relaxation for brushed loops |
| `FLC3T` | 3-Thread Diagonal Fleece | Knit | 36.0 | Diagonal skew relaxation |
| `LYC_SJ` | Cotton Lycra Jersey (Leggings) | Knit | 48.0 | Spandex recovery requires 48h min |
| `TWILL` | Cotton Twill 2/1 (Chinos) | Woven | 12.0 | Flat loom state unrolling |
| `DENIM` | Indigo Ring Denim 3/1 | Woven | 12.0 | Heavy weight skew balance |

---

## 2. Member B Desk UI Verification Checklist

Whenever Member A pushes code, Member B should log into Frappe Desk (`http://campus-test.localhost:8000`) and execute this 5-point manual acceptance verification:

1. **Textile Settings Test:**
   * Go to **Textile Settings**.
   * Change `Min Relaxation Hours` to `8.0` and click **Save**.
   * *Expected Result:* Pop-up error: `Min Relaxation Hours cannot be less than 12.0`.
2. **Yarn Count Test:**
   * Go to **Yarn Count Master** $\rightarrow$ New.
   * Enter Count Code `30S_TEST`, System `English Cotton Count (Ne)`, Nominal `30.0`.
   * Click **Save**.
   * *Expected Result:* Denier auto-populates to `177.17`, Tex to `19.68`, Nm to `50.79`.
3. **Yarn Blend Percentage Test:**
   * Go to **Yarn Blend Master** $\rightarrow$ New.
   * Add Cotton `60%`, Poly `35%` (Total = 95%). Click **Save**.
   * *Expected Result:* Form validation throws error: `Total fibre blend percentage must equal exactly 100.0%`.
4. **Shade Master Pantone Test:**
   * Go to **Shade Master** $\rightarrow$ New.
   * Enter Pantone `19-4010 TCX`, Hex `#0A1172`. Click **Save**.
   * *Expected Result:* Saves cleanly and color indicator previews deep navy blue.
5. **Shift Master Overlap Test:**
   * Try creating two active shifts that overlap in time (e.g., Shift A 08:00-16:00 and Shift B 14:00-22:00 without split assignment).
   * *Expected Result:* System warns or rejects direct collision.

