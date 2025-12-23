# NPPES Provider Lookup Tool

## 📋 Overview

**Business Problem:** Provider NPIs in eligibility files weren't syncing to CRM because they were missing from reference tables. Manual lookup was time-consuming.

**Solution:** Python script querying the CMS NPPES Registry API to automatically retrieve provider demographics.

**Impact:** Reduced data enrichment from 2+ hours to under 2 minutes for 34 NPIs.

---

## 🛠️ Technologies

- Python 3.x
- requests, pandas, openpyxl
- CMS NPPES Registry API v2.1

---

## 📊 Key Features

1. **Batch NPI Lookup** - Process multiple NPIs
2. **Rate Limiting** - Respects API limits
3. **Error Handling** - Graceful failure handling
4. **Excel Output** - CRM-ready format

---

## 🚀 Usage

```bash
pip install requests pandas openpyxl
python nppes_lookup.py
```

---

## 📁 Files

| File | Description |
|------|-------------|
| `python/nppes_lookup.py` | Main script |
| `python/requirements.txt` | Dependencies |
