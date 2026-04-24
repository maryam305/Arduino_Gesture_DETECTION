# 🧠 DeepX — Arabic Aspect-Based Sentiment Analysis System
### Smart Feedback Intelligence for Real-World Arabic Reviews

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Challenge Objectives & Scoring](#2-challenge-objectives--scoring)
3. [Aspect Taxonomy](#3-aspect-taxonomy)
4. [Dataset Deep Dive](#4-dataset-deep-dive)
5. [Data Challenges & Preprocessing](#5-data-challenges--preprocessing)
6. [ML Model Architecture](#6-ml-model-architecture)
7. [Confidence Calibration](#7-confidence-calibration)
8. [Evaluation & Submission Schema](#8-evaluation--submission-schema)
9. [Aggregation & Analytics Pipeline](#9-aggregation--analytics-pipeline)
10. [Trend & Forecasting Module](#10-trend--forecasting-module)
11. [System Architecture](#11-system-architecture)
12. [UI/UX Design — Full Specification](#12-uiux-design--full-specification)
    - [Design Language & Tokens](#121-design-language--tokens)
    - [Color Palette (Light & Dark Modes)](#122-color-palette-light--dark-modes)
    - [Typography](#123-typography)
    - [Animations & Motion System](#124-animations--motion-system)
    - [Dynamic Background Modes](#125-dynamic-background-modes)
    - [Dashboard Page](#126-dashboard-page)
    - [Review Explorer Page](#127-review-explorer-page)
    - [Insights Page](#128-insights-page)
    - [Trends & Forecast Page](#129-trends--forecast-page)
    - [Live Inference Page](#1210-live-inference-page)
13. [API Specification](#13-api-specification)
14. [Team Responsibilities](#14-team-responsibilities)
15. [Repository Structure](#15-repository-structure)
16. [Setup & Running the Project](#16-setup--running-the-project)
17. [Future Extensions](#17-future-extensions)

---

## 1. Project Overview

**DeepX** is a production-grade Arabic Aspect-Based Sentiment Analysis (ABSA) system. It goes beyond simple polarity detection by pinpointing *which* aspect of a product or service a customer is reacting to, and *how* they feel about it — all in one review.

> Traditional sentiment: "This review is negative."
> ABSA: "The **food** sentiment is **neutral**, but the **service** sentiment is **negative** (confidence: 0.94)."

The system handles the full pipeline end-to-end:

- Noisy real-world Arabic text (dialects, slang, emoji, typos, mixed scripts)
- Multi-label aspect detection (one review can mention 1–6 aspects simultaneously)
- Per-aspect sentiment classification
- Calibrated confidence scoring
- Aggregated time-series analytics with forecasting
- A decision-support dashboard UI — not just a model output

**Total dataset size:** 9,518 reviews (1,971 train · 500 validation · 7,047 unlabeled test)

---

## 2. Challenge Objectives & Scoring

| Pillar | Weight | What Is Evaluated |
|---|---|---|
| **Pillar 1 — Model Quality** | 30% | F1 (Micro) on the hidden labeled test set |
| **Pillar 2 — Data Handling** | ~17% | Preprocessing quality, date normalization, noise handling |
| **Pillar 3 — Technical Approach** | ~20% | Architecture clarity, training methodology, confidence calibration |
| **Pillar 4 — Deployment / UI** | ~20% | Dashboard quality, API response time, real-time inference |
| **Pillar 5 — Presentation** | ~13% | Documentation, reasoning clarity, reproducibility |

### Key Metric: F1 Micro

F1 Micro treats each (review, aspect, sentiment) triple as an independent prediction. It is sensitive to class imbalance and penalizes missing minority aspects (e.g., `cleanliness`, `none`).

```
F1 Micro = 2 × (Precision_micro × Recall_micro) / (Precision_micro + Recall_micro)
```

**Implications for our model:**
- Must not ignore rare aspects (`none`, `cleanliness`, `delivery`)
- Neutral sentiment is rare (4.5% of labels) — requires deliberate handling
- Aspect detection and sentiment classification errors both count

---

## 3. Aspect Taxonomy

The system uses exactly these 9 aspect labels. No others are accepted:

| Aspect | Description | Typical Domain |
|---|---|---|
| `food` | Food quality, taste, freshness, portions | Restaurants, cafés |
| `service` | Staff behavior, speed, helpfulness | All domains |
| `price` | Value for money, pricing, fees | All domains |
| `cleanliness` | Hygiene, tidiness of space or product | Restaurants, healthcare, retail |
| `delivery` | Shipping speed, delivery accuracy | Ecommerce, food delivery, transport |
| `ambiance` | Atmosphere, décor, noise level, seating | Restaurants, cafés, entertainment |
| `app_experience` | UI usability, bugs, features, updates | Play Store apps |
| `general` | Overall opinion not tied to a specific aspect | All domains |
| `none` | Review contains no discernible aspect | Edge cases |

**Class distribution in training data:**

| Aspect | Count | % of All Labels |
|---|---|---|
| service | 988 | 29.6% |
| food | 454 | 13.6% |
| app_experience | 453 | 13.6% |
| ambiance | 378 | 11.3% |
| price | 354 | 10.6% |
| general | 303 | 9.1% |
| cleanliness | 185 | 5.5% |
| delivery | 161 | 4.8% |
| none | 57 | 1.7% |

**Sentiment distribution:**

| Sentiment | Count | % |
|---|---|---|
| positive | 1,646 | 49.5% |
| negative | 1,538 | 46.2% |
| neutral | 149 | 4.5% |

> ⚠️ Neutral is severely underrepresented. Weighted loss or oversampling strategies are required.

---

## 4. Dataset Deep Dive

### 4.1 Files

| File | Rows | Labeled? | Purpose |
|---|---|---|---|
| `DeepX_train.xlsx` | 1,971 | ✅ Yes | Model training |
| `DeepX_validation.xlsx` | 500 | ✅ Yes | Hyperparameter tuning, threshold selection |
| `DeepX_unlabeled.xlsx` | 7,047 | ❌ No | Final submission target |

### 4.2 Column Schema

| Column | Type | Notes |
|---|---|---|
| `review_id` | int | Unique identifier |
| `review_text` | str | Raw Arabic review text |
| `star_rating` | int 1–5 | User-provided star rating |
| `date` | str | Mixed absolute/relative formats |
| `business_name` | str | Entity name (Arabic or English) |
| `business_category` | str | Domain category (67 unique values in train) |
| `platform` | str | `google_maps` or `play_store` |
| `aspects` | JSON list str | e.g. `["food", "service"]` |
| `aspect_sentiments` | JSON dict str | e.g. `{"food": "positive", "service": "negative"}` |

> The `unlabeled` file has the same columns **except** `aspects` and `aspect_sentiments` — those are what we must predict.

### 4.3 Key Statistics

- **Average aspects per review:** 1.69
- **Max aspects per review:** 6
- **Reviews with multiple aspects:** 45.9%
- **Platforms:** Google Maps (61.4%) · Play Store (38.6%)
- **Date format split:** 61.4% relative Arabic dates · 38.6% absolute ISO dates

### 4.4 Sample Reviews

```
Review: "لا يوجد الدفع بالبطاقه عند الاستلام"
→ aspects: ["app_experience", "delivery"]
→ sentiments: {"app_experience": "negative", "delivery": "negative"}

Review: "المكان نضيف وجميل وقعدته تحفه والخدمة فوق الممتاز والجو جميل"
→ aspects: ["cleanliness", "ambiance", "service"]
→ sentiments: {"cleanliness": "positive", "ambiance": "positive", "service": "positive"}

Review: "الاكل يعني كويس ولكن كمية قليلة جدا والخدمة بطيئة"
→ aspects: ["food", "service", "delivery"]
→ sentiments: {"food": "neutral", "service": "negative", "delivery": "negative"}
```

---

## 5. Data Challenges & Preprocessing

### 5.1 Noisy Arabic Text

Arabic reviews in the wild contain:

| Issue | Example | Fix |
|---|---|---|
| Letter elongation (تطويل) | `جمييييل` | Regex reduce to `جميل` |
| Dialectal spelling variance | `مش` vs `مو` vs `ما` | Dialect normalization map |
| Mixed Arabic/English | `delivery سريع` | Keep as-is, model handles bilingual |
| Emoji | `❤️❤️❤️` | Either strip or encode as sentiment signal |
| Excessive punctuation | `!!!!` | Normalize to single `!` |
| Hamza variance | `أ` / `إ` / `ا` | Unify to `ا` |
| Ta marbuta | `ه` vs `ة` | Unify |
| Alef maksura | `ى` vs `ي` | Unify |
| Diacritics (tashkeel) | `مَرْحَباً` | Strip diacritics |
| Zero-width chars | invisible chars | Strip ZWNJ, ZWJ |

### 5.2 Date Normalization

Two formats exist and must be unified to a single absolute date.

**Absolute format (38.6%):**
```
2026-03-08 00:00:00  →  2026-03-08
2020-10-28 00:00:00  →  2020-10-28
```

**Relative Arabic format (61.4%) — full mapping table:**

| Arabic Pattern | Interpretation | Example Parsed Output |
|---|---|---|
| `قبل يوم واحد` | 1 day ago | reference_date - 1 day |
| `قبل يومين (2)` | 2 days ago | reference_date - 2 days |
| `قبل 3 أيام` | N days ago | reference_date - N days |
| `قبل أسبوع` | 1 week ago | reference_date - 7 days |
| `قبل أسبوعين` | 2 weeks ago | reference_date - 14 days |
| `قبل 3 أسابيع` | N weeks ago | reference_date - N×7 days |
| `قبل شهر` | 1 month ago | reference_date - 30 days |
| `قبل شهرين` | 2 months ago | reference_date - 60 days |
| `قبل 3 أشهر` | N months ago | reference_date - N×30 days |
| `قبل سنة` | 1 year ago | reference_date - 365 days |
| `قبل سنتين` | 2 years ago | reference_date - 730 days |
| `قبل 7 ساعات` | 7 hours ago | reference_date (same day) |
| `قبل 12 ساعة` | 12 hours ago | reference_date (same day) |

> **Reference date:** Use the scrape date if available in metadata, else use 2026-03-20 as the default anchor for training data, and infer from platform context.

**Implementation:**
```python
import re
from datetime import datetime, timedelta

ARABIC_RELATIVE_MAP = {
    r'قبل يوم واحد': lambda: timedelta(days=1),
    r'قبل يومين': lambda: timedelta(days=2),
    r'قبل (\d+) أيام': lambda m: timedelta(days=int(m.group(1))),
    r'قبل أسبوع': lambda: timedelta(weeks=1),
    r'قبل أسبوعين': lambda: timedelta(weeks=2),
    r'قبل (\d+) أسابيع': lambda m: timedelta(weeks=int(m.group(1))),
    r'قبل شهر': lambda: timedelta(days=30),
    r'قبل شهرين': lambda: timedelta(days=60),
    r'قبل (\d+) أشهر': lambda m: timedelta(days=int(m.group(1)) * 30),
    r'قبل سنة': lambda: timedelta(days=365),
    r'قبل سنتين': lambda: timedelta(days=730),
    r'قبل (\d+) سنوات': lambda m: timedelta(days=int(m.group(1)) * 365),
    r'قبل \d+ ساعات?': lambda: timedelta(hours=0),
}

REFERENCE_DATE = datetime(2026, 3, 20)

def normalize_date(raw: str) -> str:
    raw = str(raw).strip()
    # Try absolute ISO parse
    try:
        return str(pd.to_datetime(raw).date())
    except: pass
    # Try relative Arabic patterns
    for pattern, delta_fn in ARABIC_RELATIVE_MAP.items():
        m = re.search(pattern, raw)
        if m:
            try:
                delta = delta_fn(m)
            except TypeError:
                delta = delta_fn()
            return str((REFERENCE_DATE - delta).date())
    return None  # flag for manual review
```

### 5.3 Business Category Normalization

The `business_category` column has 67 unique values — many are Arabic strings that map to the same semantic domain:

```
مطعم → restaurant
كافيه → cafe
صالون تجميل → beauty_salon
مركز تسوق → shopping_mall
مستشفى → healthcare
نقل → transport
...
```

Build a normalization dictionary and encode to ~12 canonical categories. This becomes a useful feature for domain-aware models.

### 5.4 Preprocessing Pipeline (Full)

```
Raw text
  ↓ Strip HTML / invisible chars / ZWNJ
  ↓ Normalize Arabic letters (hamza, alef, ta, ya)
  ↓ Remove diacritics (tashkeel)
  ↓ Reduce elongation (جمييييل → جميل)
  ↓ Normalize punctuation (!! → !)
  ↓ Strip/encode emoji
  ↓ Lowercase non-Arabic tokens
  ↓ Tokenize
  ↓ [Optional] remove stopwords
  ↓ Ready for model input
```

---

## 6. ML Model Architecture

### 6.1 Task Formulation

ABSA is treated as **two sub-tasks** run in sequence (pipeline) or jointly (multi-task):

**Sub-task A — Aspect Detection (Multi-label classification)**
- Input: review text
- Output: binary vector of size 9 (one per aspect)
- Example: `[1, 1, 0, 0, 0, 0, 0, 0, 0]` → food + service

**Sub-task B — Sentiment Classification per Aspect**
- Input: review text + detected aspect
- Output: one of {positive, negative, neutral} per detected aspect

### 6.2 Recommended Approach: AraBERT Fine-tuning

**Base Model:** `aubmindlab/bert-base-arabertv02` or `CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment`

AraBERT is pre-trained on ~77GB of Arabic text and natively handles MSA + dialectal Arabic.

**Architecture:**

```
[CLS] review_text [SEP] aspect_name [SEP]
          ↓
    AraBERT Encoder (12 layers, 768-dim)
          ↓
    [CLS] pooled representation
          ↓
   ┌──────────────────────────────┐
   │   Aspect Classifier Head     │  → Multi-label sigmoid (9 outputs)
   │   Sentiment Classifier Head  │  → Softmax over 3 classes per aspect
   └──────────────────────────────┘
```

**Training configuration:**

```yaml
model: aubmindlab/bert-base-arabertv02
max_length: 128
batch_size: 16
learning_rate: 2e-5
warmup_ratio: 0.1
weight_decay: 0.01
epochs: 5
optimizer: AdamW
scheduler: linear_with_warmup

# Loss
aspect_detection_loss: BCEWithLogitsLoss
  pos_weight: [1.0, 1.0, 1.0, 2.0, 2.5, 1.3, 1.2, 3.0, 8.0]  # inverse frequency weights

sentiment_loss: CrossEntropyLoss
  class_weight: [1.0, 1.0, 5.0]  # boost neutral
  
combined_loss: aspect_loss × 0.5 + sentiment_loss × 0.5
```

### 6.3 Aspect Detection Threshold Tuning

Do NOT use 0.5 as the default threshold. Tune per-aspect on the validation set:

```python
from sklearn.metrics import f1_score
import numpy as np

def find_best_thresholds(probs, labels, aspects):
    thresholds = {}
    for i, aspect in enumerate(aspects):
        best_t, best_f1 = 0.5, 0.0
        for t in np.arange(0.2, 0.8, 0.05):
            preds = (probs[:, i] > t).astype(int)
            f1 = f1_score(labels[:, i], preds, zero_division=0)
            if f1 > best_f1:
                best_f1, best_t = f1, t
        thresholds[aspect] = best_t
    return thresholds
```

### 6.4 Alternative / Ensemble Approaches

| Method | Pros | Cons |
|---|---|---|
| AraBERT (recommended) | Strong baseline, dialect-aware | GPU required |
| CAMeL-BERT | Good dialectal coverage | Slower inference |
| Llama-3.1 Arabic fine-tune | State-of-art potential | Very large |
| TF-IDF + XGBoost | Fast, no GPU | Weaker on noisy text |
| Ensemble (AraBERT + XGBoost) | Improved robustness | Complex pipeline |

**Ensemble strategy:** Average logits from AraBERT and a TF-IDF+LogReg model for the final prediction. This often boosts F1 by 1–3%.

---

## 7. Confidence Calibration

Each prediction must include a calibrated confidence score. This is NOT just the raw softmax probability — those are often overconfident.

### 7.1 Why Calibration Matters

| Raw Softmax | True Accuracy |
|---|---|
| 0.95 | ~72% (miscalibrated) |
| 0.80 | ~80% (well-calibrated) |

### 7.2 Calibration Method: Temperature Scaling

```python
from scipy.optimize import minimize
import torch
import torch.nn.functional as F

def temperature_scale(logits, temperature):
    return logits / temperature

def find_temperature(val_logits, val_labels):
    def nll_loss(T):
        scaled = temperature_scale(torch.tensor(val_logits), T[0])
        loss = F.cross_entropy(scaled, torch.tensor(val_labels))
        return loss.item()
    result = minimize(nll_loss, [1.5], method='L-BFGS-B', bounds=[(0.1, 10.0)])
    return result.x[0]
```

### 7.3 Confidence in UI

Confidence drives visual feedback:

| Confidence Range | UI Treatment |
|---|---|
| ≥ 0.90 | Solid color chip, no warning |
| 0.70 – 0.89 | Slightly muted chip, tooltip "High confidence" |
| 0.50 – 0.69 | Dashed border chip, tooltip "Moderate confidence" |
| < 0.50 | Gray chip with `?` icon, tooltip "Low confidence — review manually" |

---

## 8. Evaluation & Submission Schema

### 8.1 Required JSON Format (per review)

```json
{
  "review_id": "7238",
  "aspects": [
    {
      "aspect": "app_experience",
      "sentiment": "negative",
      "confidence": 0.93
    },
    {
      "aspect": "delivery",
      "sentiment": "negative",
      "confidence": 0.87
    }
  ]
}
```

### 8.2 Rules

- Every review in `DeepX_unlabeled.xlsx` must have an entry
- `aspect` must be one of the 9 valid values — no others accepted
- `sentiment` must be exactly `"positive"`, `"negative"`, or `"neutral"` — lowercase
- `confidence` must be a float between 0.0 and 1.0 (3 decimal places recommended)
- If no aspect is detected, submit `[{"aspect": "none", "sentiment": "neutral", "confidence": 0.80}]`
- Do NOT include `review_text` or other fields in the submission

### 8.3 Submission File

```
submission.json
  [ {review_id: ..., aspects: [...]}, ... ]   ← array of 7,047 objects
```

---

## 9. Aggregation & Analytics Pipeline

After ABSA inference, predictions are post-processed into time-based aggregates for the dashboard.

### 9.1 Sentiment Score

Each sentiment is mapped to a numeric score:

```python
SENTIMENT_SCORE = {"positive": +1, "negative": -1, "neutral": 0}
```

Confidence-weighted score:
```python
weighted_score = sentiment_score × confidence
```

### 9.2 Aggregation Levels

| Level | Granularity | Use Case |
|---|---|---|
| daily | per day | Short-term trend charts |
| weekly | per ISO week | Weekly reports |
| monthly | per month | Long-term dashboard |

**Aggregation query (SQL-style pseudocode):**
```sql
SELECT
  aspect,
  date_trunc('week', review_date) AS week,
  AVG(weighted_score) AS avg_sentiment,
  COUNT(*) AS review_count,
  AVG(confidence) AS avg_confidence,
  SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) AS positive_count,
  SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) AS negative_count,
  SUM(CASE WHEN sentiment='neutral' THEN 1 ELSE 0 END) AS neutral_count
FROM aspect_predictions
GROUP BY aspect, week
ORDER BY week DESC
```

### 9.3 Alert Thresholds

The system fires alerts when:
- Average weekly sentiment for any aspect drops by > 0.3 vs previous week
- Negative ratio for any aspect exceeds 60% in the last 7 days
- Review volume spikes > 3× the 30-day average (sudden event detection)

---

## 10. Trend & Forecasting Module

### 10.1 Pipeline

```
ABSA Predictions
      ↓
Date Normalization → Absolute Timestamps
      ↓
Aggregate to Daily Sentiment Scores (per aspect)
      ↓
Smooth with EWM (Exponential Weighted Mean, α=0.3)
      ↓
Forecast Next 7–14 Days
      ↓
Visualize with Confidence Bands
```

### 10.2 Models

**Baseline: Exponential Smoothing (Holt-Winters)**
```python
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model = ExponentialSmoothing(
    series,
    trend='add',
    seasonal=None,
    initialization_method='estimated'
).fit()
forecast = model.forecast(7)
```

**Advanced: Facebook Prophet**
```python
from prophet import Prophet

df = pd.DataFrame({'ds': dates, 'y': sentiment_scores})
m = Prophet(interval_width=0.95, daily_seasonality=False, weekly_seasonality=True)
m.fit(df)
future = m.make_future_dataframe(periods=14)
forecast = m.predict(future)
```

### 10.3 Forecast Output

```json
{
  "aspect": "service",
  "forecast": [
    {"date": "2026-03-21", "predicted_score": 0.42, "lower_bound": 0.28, "upper_bound": 0.56},
    {"date": "2026-03-22", "predicted_score": 0.38, "lower_bound": 0.21, "upper_bound": 0.55}
  ],
  "trend_direction": "declining",
  "alert": true,
  "alert_message": "Service sentiment declining — projected to drop below neutral threshold in 3 days"
}
```

---

## 11. System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Flutter Frontend                           │
│   Dashboard · Review Explorer · Insights · Trends · Inference  │
└────────────────────────┬───────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend (Python)                       │
│   /predict  /reviews  /dashboard  /trends  /alerts             │
└──────┬─────────────────┬─────────────────────┬─────────────────┘
       │                 │                     │
┌──────▼──────┐  ┌───────▼───────┐  ┌──────────▼────────┐
│  ABSA Model │  │  Aggregation  │  │  Forecast Module  │
│  (AraBERT)  │  │  Engine       │  │  (Prophet/Holt)   │
│  + Calib.   │  │  (Pandas/SQL) │  │                   │
└──────┬──────┘  └───────┬───────┘  └──────────┬────────┘
       │                 │                     │
       └─────────────────▼─────────────────────┘
                    ┌────▼─────┐
                    │ Database │
                    │ SQLite / │
                    │ Postgres │
                    └──────────┘
```

### 11.1 API Response Time Budget

| Endpoint | Target Latency | Notes |
|---|---|---|
| `POST /predict` | < 300ms | Single review, cached model |
| `GET /dashboard` | < 500ms | Pre-aggregated on write |
| `GET /trends` | < 800ms | Forecast cached hourly |
| `GET /reviews` | < 400ms | Paginated (20 per page) |

---

## 12. UI/UX Design — Full Specification

### 12.1 Design Language & Tokens

The UI follows a **dark-first, data-rich aesthetic** inspired by intelligence dashboards. The visual language is: precision over decoration, data density with breathing room, subtle depth through layering.

**Core Design Principles:**
- Every element earns its place — no decorative noise
- Arabic text support (RTL) is first-class, not an afterthought
- Confidence scores drive visual weight, not just tooltips
- The dashboard communicates urgency through color intensity, not popups

**Spacing Scale (8px base grid):**
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
--space-8: 64px;
```

**Border Radius:**
```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-pill: 9999px;
```

**Elevation / Shadow System:**
```css
--shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
--shadow-md: 0 4px 16px rgba(0,0,0,0.4);
--shadow-lg: 0 8px 32px rgba(0,0,0,0.5);
--shadow-glow-green: 0 0 20px rgba(52,211,153,0.25);
--shadow-glow-red:   0 0 20px rgba(239,68,68,0.25);
--shadow-glow-blue:  0 0 20px rgba(96,165,250,0.25);
```

---

### 12.2 Color Palette (Light & Dark Modes)

#### Dark Mode (Default)

```css
/* Backgrounds */
--bg-base:       #0A0F1E;   /* deepest navy-black — main background */
--bg-surface:    #111827;   /* card surfaces */
--bg-elevated:   #1F2937;   /* tooltips, modals, dropdowns */
--bg-overlay:    #374151;   /* hover states on elevated surfaces */

/* Borders */
--border-subtle: #1F2937;
--border-default: #374151;
--border-strong:  #4B5563;

/* Text */
--text-primary:   #F9FAFB;  /* headings */
--text-secondary: #9CA3AF;  /* labels, captions */
--text-muted:     #6B7280;  /* timestamps, footnotes */
--text-inverse:   #111827;  /* text on colored backgrounds */

/* Sentiment Colors */
--color-positive:       #34D399;  /* emerald green */
--color-positive-dim:   #065F46;  /* background chip */
--color-positive-glow:  rgba(52,211,153,0.2);

--color-negative:       #F87171;  /* soft red */
--color-negative-dim:   #7F1D1D;
--color-negative-glow:  rgba(248,113,113,0.2);

--color-neutral:        #60A5FA;  /* sky blue */
--color-neutral-dim:    #1E3A5F;
--color-neutral-glow:   rgba(96,165,250,0.2);

/* Accent / Brand */
--accent-primary:   #818CF8;  /* indigo — interactive elements */
--accent-secondary: #C084FC;  /* purple — secondary highlights */
--accent-warning:   #FBBF24;  /* amber — alerts */

/* Confidence */
--conf-high:   #34D399;   /* ≥ 0.90 */
--conf-medium: #FBBF24;   /* 0.70–0.89 */
--conf-low:    #F87171;   /* 0.50–0.69 */
--conf-vlow:   #9CA3AF;   /* < 0.50 */
```

#### Light Mode

```css
--bg-base:       #F8FAFC;
--bg-surface:    #FFFFFF;
--bg-elevated:   #F1F5F9;
--bg-overlay:    #E2E8F0;

--border-subtle:  #E2E8F0;
--border-default: #CBD5E1;
--border-strong:  #94A3B8;

--text-primary:   #0F172A;
--text-secondary: #475569;
--text-muted:     #94A3B8;

--color-positive:       #059669;
--color-positive-dim:   #D1FAE5;

--color-negative:       #DC2626;
--color-negative-dim:   #FEE2E2;

--color-neutral:        #2563EB;
--color-neutral-dim:    #DBEAFE;

--accent-primary:   #4F46E5;
--accent-secondary: #7C3AED;
--accent-warning:   #D97706;
```

**Mode Toggle Behavior:** Toggling between light and dark mode triggers a `200ms ease` CSS transition on `background-color`, `color`, and `border-color` for all elements. SVG chart colors also transition via CSS variable inheritance.

---

### 12.3 Typography

**Font Pairing:**
```css
/* Display / Arabic headings */
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
--font-display: 'Cairo', 'Tajawal', sans-serif;

/* Body / English content */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;500;600&display=swap');
--font-body: 'Sora', 'Noto Sans Arabic', sans-serif;
--font-mono: 'DM Mono', monospace;   /* for JSON previews, review IDs */
```

**Type Scale:**
```css
--text-xs:   11px / 1.4;
--text-sm:   13px / 1.5;
--text-base: 15px / 1.6;
--text-lg:   18px / 1.5;
--text-xl:   22px / 1.4;
--text-2xl:  28px / 1.3;
--text-3xl:  36px / 1.2;
--text-4xl:  48px / 1.1;
```

**RTL Layout:** The entire app uses `dir="rtl"` for Arabic text with `dir="ltr"` override only for code blocks, JSON outputs, and numeric values. Font size for Arabic body text is 1pt larger than the English equivalent (Arabic letters read smaller at the same point size).

---

### 12.4 Animations & Motion System

All animations respect `prefers-reduced-motion`. When the user has reduced motion enabled, all transitions drop to `50ms` and no particle/float animations run.

#### Entrance Animations

**Page Load — Staggered Card Reveal:**
```css
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card {
  animation: fadeSlideUp 400ms cubic-bezier(0.22, 1, 0.36, 1) both;
}

.card:nth-child(1) { animation-delay: 0ms; }
.card:nth-child(2) { animation-delay: 80ms; }
.card:nth-child(3) { animation-delay: 160ms; }
.card:nth-child(4) { animation-delay: 240ms; }
```

**Number Counters (KPI cards):**  
On page load, numeric KPI values animate from `0` to their actual value over `1200ms` using a quadratic ease-out (`easeOutQuad`). This draws attention to key metrics.

```javascript
function animateCounter(el, target, duration = 1200) {
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - (1 - progress) ** 3; // easeOutCubic
    el.textContent = Math.round(eased * target).toLocaleString('ar-EG');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}
```

**Confidence Bar Fill:**  
Progress bars for confidence scores animate from `width: 0%` to their actual value with a `600ms ease-out` delay after page load.

#### Micro-interactions

**Aspect Chip Hover:**
```css
.aspect-chip {
  transition: transform 150ms ease, box-shadow 150ms ease, background-color 150ms ease;
}
.aspect-chip:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-green); /* or red/blue based on sentiment */
}
```

**Card Hover:**
```css
.card {
  transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-strong);
}
```

**Button Press:**
```css
.btn:active {
  transform: scale(0.97);
  transition: transform 80ms ease;
}
```

**Sidebar Nav Item:**  
Active item gets a left accent bar (`3px solid var(--accent-primary)`) that slides in from the left on `150ms ease`. Inactive items have `opacity: 0.6` with hover → `opacity: 1` on `120ms`.

#### Chart Animations

- **Bar charts:** bars grow from `height: 0` upward on `800ms` with staggered `50ms` delays per bar
- **Line charts:** stroke-dashoffset animation reveals the path from left to right over `1000ms ease-in-out`
- **Donut/Pie charts:** segments sweep from 0° clockwise with `600ms ease-out`
- **Forecast confidence band:** fills with `opacity: 0 → 0.2` over `400ms` after the main line renders

#### Alert Animation

When a new alert fires:
1. Alert banner slides down from the top nav (`translateY(-100%) → 0`) over `300ms spring`
2. Background of the relevant aspect card pulses with `box-shadow: 0 0 0 0px rgba(251,191,36,0.6) → 0 0 0 12px transparent` — a ripple effect repeated 3× before settling

#### Loading States

- **Skeleton screens:** Animated gradient shimmer moving left-to-right at `1.5s` intervals (never show spinners for data loads)
- **Inference loading:** 3-dot bounce animation (`200ms` stagger) while awaiting API response
- **Transition between pages:** Shared-element transition — the page fades out at `opacity: 0` then new page fades in, total `200ms`

---

### 12.5 Dynamic Background Modes

The background is the most distinctive UI element. Three modes are available, selectable by the user in Settings:

#### Mode 1: Neural Mesh (Default — Dark)

A slow-moving animated mesh of connected nodes suggesting a neural network, rendered on `<canvas>`.

- **Color:** `rgba(129, 140, 248, 0.08)` nodes on `#0A0F1E` background
- **Nodes:** 60–80 small dots (`radius: 2px`), randomly positioned
- **Connections:** Lines drawn between nodes within `150px` of each other, `opacity` proportional to inverse distance
- **Motion:** Each node moves on a random walk (`vx`, `vy` ≤ 0.4px/frame), bouncing off canvas edges
- **Performance:** `requestAnimationFrame` capped at 30fps, paused when tab not visible

```javascript
class NeuralMesh {
  constructor(canvas) {
    this.nodes = Array.from({length: 70}, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
    }));
  }
  draw(ctx) {
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i+1; j < this.nodes.length; j++) {
        const dx = this.nodes[i].x - this.nodes[j].x;
        const dy = this.nodes[i].y - this.nodes[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 150) {
          ctx.strokeStyle = `rgba(129,140,248,${(1 - dist/150) * 0.15})`;
          ctx.beginPath();
          ctx.moveTo(this.nodes[i].x, this.nodes[i].y);
          ctx.lineTo(this.nodes[j].x, this.nodes[j].y);
          ctx.stroke();
        }
      }
      // Draw node
      ctx.fillStyle = 'rgba(129,140,248,0.4)';
      ctx.beginPath();
      ctx.arc(this.nodes[i].x, this.nodes[i].y, 2, 0, Math.PI * 2);
      ctx.fill();
      // Move
      this.nodes[i].x += this.nodes[i].vx;
      this.nodes[i].y += this.nodes[i].vy;
      if (this.nodes[i].x < 0 || this.nodes[i].x > ctx.canvas.width) this.nodes[i].vx *= -1;
      if (this.nodes[i].y < 0 || this.nodes[i].y > ctx.canvas.height) this.nodes[i].vy *= -1;
    }
  }
}
```

#### Mode 2: Aurora Gradient (Dark — High Visual Impact)

A slow-shifting multi-color gradient blob that breathes and morphs. No canvas — pure CSS.

```css
.aurora-bg {
  background: #0A0F1E;
  overflow: hidden;
}

.aurora-bg::before {
  content: '';
  position: fixed;
  inset: -50%;
  background: conic-gradient(
    from 200deg at 50% 60%,
    transparent 0deg,
    rgba(129,140,248,0.15) 60deg,
    rgba(192,132,252,0.12) 120deg,
    transparent 180deg,
    rgba(52,211,153,0.08) 240deg,
    transparent 300deg
  );
  animation: auroraRotate 20s linear infinite;
  filter: blur(40px);
}

@keyframes auroraRotate {
  from { transform: rotate(0deg) scale(1.5); }
  to   { transform: rotate(360deg) scale(1.5); }
}
```

A second `::after` pseudo-element uses a radial-gradient blob that floats using:
```css
@keyframes auroraFloat {
  0%, 100% { transform: translate(0px, 0px) scale(1); }
  33%       { transform: translate(30px, -40px) scale(1.05); }
  66%       { transform: translate(-20px, 20px) scale(0.98); }
}
```
Animation duration: `12s ease-in-out infinite`.

#### Mode 3: Clean Grain (Light Mode)

A static SVG noise texture overlaid at `opacity: 0.04` gives depth to the otherwise flat light background, without any motion. The texture uses a `<feTurbulence>` SVG filter:

```html
<svg width="0" height="0">
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
</svg>
<style>
  .light-bg::before {
    content: '';
    position: fixed; inset: 0;
    background: url("data:image/svg+xml,...");
    filter: url(#noise);
    opacity: 0.04;
    pointer-events: none;
  }
</style>
```

**Background mode persistence:** The user's chosen mode is saved to `localStorage` and restored on next session. The transition between modes animates over `600ms ease`.

---

### 12.6 Dashboard Page

**Layout:** 2-column grid (sidebar 240px · main content flex-grow)

**Top KPI Row** — 4 cards:
```
[ Total Reviews Analyzed ]  [ Avg Sentiment Score ]  [ Most Problematic Aspect ]  [ Active Alerts ]
        9,518                      +0.31 / 1.0           service (42% neg)              2 active
```
Each KPI card has:
- Large number (`text-4xl bold`)
- Label (`text-sm text-secondary`)
- Trend arrow (↑↓ with color)
- Counter animation on page load

**Aspect Sentiment Breakdown** — Horizontal stacked bar per aspect:
```
food         [██████████░░░░░] 62% pos · 31% neg · 7% neu
service      [████░░░░░░░░░░░] 38% pos · 55% neg · 7% neu
ambiance     [████████████░░░] 73% pos · 22% neg · 5% neu
...
```
- Bar segments colored `--color-positive`, `--color-negative`, `--color-neutral`
- Hover shows exact counts in a tooltip
- Click on a bar navigates to Review Explorer filtered by that aspect

**Sentiment Over Time** — Line chart (last 90 days):
- One line per aspect (toggleable via legend checkboxes)
- X-axis: date · Y-axis: avg sentiment score (-1 to +1)
- Smoothed with 7-day rolling average
- Hover shows tooltip with exact values + review count

**Platform Comparison** — Side-by-side donut charts:
- Left: Google Maps sentiment breakdown
- Right: Play Store sentiment breakdown
- Shows which platform generates more negative feedback

**Recent Alerts Panel** (right sidebar):
```
🔴 Service sentiment dropped 0.35 pts this week
🟡 Delivery negative rate exceeded 60% threshold
✅ Food quality recovering (up 0.18 pts)
```

---

### 12.7 Review Explorer Page

**Purpose:** Browse, search, and filter raw reviews with aspect annotations.

**Filter Bar (RTL layout):**
```
[Search: ابحث في المراجعات...]  [Aspect ▼]  [Sentiment ▼]  [Platform ▼]  [Confidence ▼]  [Date Range]
```

**Review Card:**
```
┌─────────────────────────────────────────────────────────────────┐
│  ⭐⭐⭐⭐⭐  · Google Maps · مطعم · 2026-03-10          #7238  │
│                                                                   │
│  "المكان نضيف وجميل وقعدته تحفه والخدمة فوق الممتاز..."         │
│                                                                   │
│  [cleanliness +] [ambiance +] [service +]                        │
│                                  Confidence: ████████░░ 0.91    │
└─────────────────────────────────────────────────────────────────┘
```

**Aspect text highlighting:**  
When a review card is expanded, the aspect spans in the review text are highlighted with the sentiment color:
- `background: var(--color-positive-dim)` for positive spans
- `background: var(--color-negative-dim)` for negative spans
- Underline: `2px solid var(--color-neutral)` for neutral

**Aspect Chip Design:**
```css
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.03em;
  border: 1px solid transparent;
}

.chip.positive { background: var(--color-positive-dim); color: var(--color-positive); }
.chip.negative { background: var(--color-negative-dim); color: var(--color-negative); }
.chip.neutral  { background: var(--color-neutral-dim);  color: var(--color-neutral);  }
```

**Low-Confidence Review Flag:**  
Reviews with any aspect `confidence < 0.60` get a `⚠ Low Confidence` badge in the card header, and can be filtered into a dedicated review queue.

**Pagination:** 20 reviews per page. "Load more" button triggers a slide-down animation revealing the next batch.

---

### 12.8 Insights Page

**Top Complaints Per Aspect:**  
A ranked list of the most frequent themes in negative reviews, extracted via keyword frequency analysis. Displayed as a horizontal bar chart.

**Keyword Cloud:**  
A weighted word cloud of frequent Arabic words in negative reviews per aspect. Word size proportional to frequency, color coded by sentiment.

**Strengths vs. Weaknesses Matrix:**
```
                POSITIVE          NEGATIVE
  High Volume:  ambiance ✅       service ❌
  Low Volume:   cleanliness ✅    delivery ⚠
```
A 2×2 quadrant chart with aspect bubbles sized by review volume.

**Domain Breakdown Table:**  
Shows which business categories generate the most negative sentiment:

| Category | Reviews | Pos% | Neg% | Score |
|---|---|---|---|---|
| ecommerce | 212 | 44% | 49% | -0.05 |
| transport | 129 | 35% | 61% | -0.26 |
| restaurant | 150 | 68% | 28% | +0.40 |

---

### 12.9 Trends & Forecast Page

**Main Chart — Time Series with Forecast:**
- Historical sentiment line (solid, colored)
- Forecast line (dashed, same color, lighter `opacity: 0.7`)
- Confidence band: shaded area around forecast (`opacity: 0.15`)
- Vertical dashed divider line labeled "Today"

**Aspect Selector:** Tab bar — click to switch between aspects. Active tab gets a bottom border (`3px solid var(--accent-primary)`).

**Trend Direction Indicators:**
```
↗ food     +0.18 (improving, last 14 days)
↘ service  -0.21 (declining, last 14 days)
→ price    +0.03 (stable)
```

**Alert Panel:**  
When a forecast predicts a drop below the neutral threshold (score < -0.2) within 7 days, the system fires a predictive alert shown in an amber card:

```
⚠ Predictive Alert: service sentiment projected to reach -0.35 by 2026-03-28.
   Action: Investigate recent reviews tagged [service · negative].
```

**Forecast Controls:**
- Forecast horizon: `[7 days] [14 days] [30 days]` toggle
- Model selector: `[Holt-Winters] [Prophet]` (switches the underlying forecasting method live)

---

### 12.10 Live Inference Page

**Purpose:** Real-time single-review ABSA prediction.

**Input:** Large `<textarea>` with placeholder "اكتب مراجعتك هنا..." (`dir="rtl"`, `font-family: var(--font-display)`, `font-size: 18px`, min-height `120px`)

**Submit Button:**  
Full-width, `height: 48px`, `background: var(--accent-primary)`, rounded corners `12px`, with loading animation (3-dot bounce) while awaiting response.

**Result Display:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Result                                              0.3s ⚡     │
│                                                                   │
│  "الاكل كان ممتاز بس الخدمة كانت بطيئة شوية"                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 🍕 food        [positive]   ████████████░░░  conf: 0.93  │    │
│  │ 👤 service     [negative]   ██████████████░  conf: 0.88  │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
│  { JSON }  [Copy] [Share]                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Result animation:**  
Each aspect row slides in from the right with `100ms` stagger. The confidence bar fills over `500ms ease-out`.

**JSON preview:**  
Collapsible section below the visual result showing the raw JSON output with syntax highlighting (keys in `--accent-primary`, strings in `--color-positive`, numbers in `--color-neutral`).

---

## 13. API Specification

### POST /predict
```json
Request:  { "text": "الاكل كان ممتاز بس الخدمة بطيئة" }

Response: {
  "review_id": null,
  "processing_time_ms": 187,
  "aspects": [
    { "aspect": "food",    "sentiment": "positive", "confidence": 0.93 },
    { "aspect": "service", "sentiment": "negative", "confidence": 0.88 }
  ]
}
```

### GET /dashboard
```json
Response: {
  "total_reviews": 9518,
  "avg_sentiment": 0.31,
  "aspect_breakdown": {
    "food": { "positive": 0.62, "negative": 0.31, "neutral": 0.07 },
    ...
  },
  "active_alerts": [ { "type": "decline", "aspect": "service", "message": "..." } ]
}
```

### GET /reviews?aspect=food&sentiment=negative&page=1&limit=20
```json
Response: {
  "total": 142,
  "page": 1,
  "results": [ { "review_id": 1234, "review_text": "...", "aspects": [...], ... } ]
}
```

### GET /trends?aspect=service&horizon=14
```json
Response: {
  "historical": [ { "date": "2026-03-01", "score": 0.45 }, ... ],
  "forecast":   [ { "date": "2026-03-21", "score": 0.38, "lower": 0.21, "upper": 0.55 }, ... ],
  "trend_direction": "declining",
  "alert": true
}
```

---

## 14. Team Responsibilities

### ML Engineer
- Data preprocessing pipeline (normalization, date parsing, encoding)
- Model training: AraBERT fine-tuning for multi-label ABSA
- Threshold tuning per aspect on validation set
- Confidence calibration (Temperature Scaling)
- Submission file generation (`submission.json`)
- FastAPI endpoint: `POST /predict`

### Frontend / System Designer
- Flutter app (all 5 pages)
- Canvas-based background animations (Neural Mesh mode)
- Chart components (stacked bar, line, donut, forecast)
- RTL layout and Arabic typography
- API integration for all endpoints
- Alert notification system

### Shared Responsibilities
- Aggregation engine and analytics SQL/Pandas queries
- Forecasting module integration
- Presentation preparation
- README and documentation

---

## 15. Repository Structure

```
deepx-absa/
├── data/
│   ├── raw/
│   │   ├── DeepX_train.xlsx
│   │   ├── DeepX_validation.xlsx
│   │   └── DeepX_unlabeled.xlsx
│   └── processed/
│       ├── train_clean.csv
│       ├── val_clean.csv
│       └── unlabeled_clean.csv
│
├── preprocessing/
│   ├── normalize_arabic.py       # Text cleaning
│   ├── parse_dates.py            # Relative → absolute dates
│   ├── encode_labels.py          # Multi-label binarization
│   └── pipeline.py               # Full preprocessing pipeline
│
├── model/
│   ├── train.py                  # AraBERT fine-tuning
│   ├── evaluate.py               # F1 Micro computation
│   ├── calibrate.py              # Temperature scaling
│   ├── infer.py                  # Single-review inference
│   ├── thresholds.json           # Per-aspect tuned thresholds
│   └── checkpoints/              # Saved model weights
│
├── submission/
│   ├── generate_submission.py    # Batch inference → submission.json
│   └── submission.json           # Final output
│
├── api/
│   ├── main.py                   # FastAPI app
│   ├── routes/
│   │   ├── predict.py
│   │   ├── dashboard.py
│   │   ├── reviews.py
│   │   └── trends.py
│   └── db/
│       ├── schema.sql
│       └── aggregate.py
│
├── forecasting/
│   ├── prophet_model.py
│   ├── holtwinters_model.py
│   └── alert_engine.py
│
├── frontend/                     # Flutter app
│   ├── lib/
│   │   ├── pages/
│   │   │   ├── dashboard.dart
│   │   │   ├── review_explorer.dart
│   │   │   ├── insights.dart
│   │   │   ├── trends.dart
│   │   │   └── inference.dart
│   │   ├── widgets/
│   │   │   ├── aspect_chip.dart
│   │   │   ├── neural_mesh_bg.dart
│   │   │   ├── sentiment_bar.dart
│   │   │   └── confidence_bar.dart
│   │   └── theme/
│   │       ├── colors.dart
│   │       └── typography.dart
│   └── pubspec.yaml
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocessing.ipynb
│   ├── 03_training.ipynb
│   └── 04_evaluation.ipynb
│
├── README.md
├── requirements.txt
└── docker-compose.yml
```

---

## 16. Setup & Running the Project

### Prerequisites

```bash
Python 3.10+
CUDA-capable GPU (recommended: ≥8GB VRAM for AraBERT)
Node.js 18+ (optional, for JS utilities)
Flutter 3.x (for frontend)
```

### Backend Setup

```bash
# Clone repo
git clone https://github.com/your-org/deepx-absa
cd deepx-absa

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Key packages:
# transformers==4.40.0
# torch==2.2.0
# arabert          (Arabic text normalization)
# camel-tools      (Arabic NLP tools)
# scikit-learn
# pandas
# fastapi
# uvicorn
# prophet
# statsmodels
```

### Running Preprocessing

```bash
python preprocessing/pipeline.py \
  --train data/raw/DeepX_train.xlsx \
  --val   data/raw/DeepX_validation.xlsx \
  --test  data/raw/DeepX_unlabeled.xlsx \
  --output data/processed/
```

### Training the Model

```bash
python model/train.py \
  --train_path data/processed/train_clean.csv \
  --val_path   data/processed/val_clean.csv \
  --model_name aubmindlab/bert-base-arabertv02 \
  --epochs 5 \
  --batch_size 16 \
  --lr 2e-5 \
  --output_dir model/checkpoints/
```

### Calibrating Confidence

```bash
python model/calibrate.py \
  --checkpoint model/checkpoints/best_model/ \
  --val_path   data/processed/val_clean.csv
# Saves temperature value to model/checkpoints/temperature.json
```

### Generating Submission

```bash
python submission/generate_submission.py \
  --checkpoint   model/checkpoints/best_model/ \
  --test_path    data/processed/unlabeled_clean.csv \
  --thresholds   model/thresholds.json \
  --output       submission/submission.json
```

### Starting the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs available at `http://localhost:8000/docs`

### Running the Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome  # for web
# or
flutter run             # for connected device
```

---

## 17. Future Extensions

| Feature | Description | Priority |
|---|---|---|
| Domain-specific fine-tuning | Separate models for restaurants vs apps | High |
| Span detection | Highlight exact words in review that triggered each aspect | High |
| Real-time ingestion | Scraper + streaming pipeline for live review monitoring | Medium |
| Cross-lingual support | Handle French/English mixed reviews in the unlabeled set | Medium |
| Active learning | Flag low-confidence predictions for human labeling to improve data | Medium |
| User accounts & saved views | Dashboard personalization | Low |
| Push notifications | Mobile alerts for sentiment drops | Low |
| Exportable reports | PDF/Excel weekly report generation | Low |

---

*Built for the DeepX Arabic ABSA Challenge · 2026*
