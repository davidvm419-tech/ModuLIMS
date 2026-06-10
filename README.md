# 🧬 LIMS Architecture Overview (MVP – Microbiology‑Focused)

A modular, scalable Laboratory Information Management System (LIMS) built with a **Sample‑centric core**, surrounded by independent modules connected through **join tables** and a universal **traceability system**.

---

## 🧱 1. Core Architecture Principles

- **Sample is the heart** of the system  
- **Modules are independent** and connect via join tables  
- **Traceability is centralized** (all timestamps + events stored in one place)  
- **Results are dynamic** (assays define their own result structure)  
- **Microbiology is the first active domain**, others can be added later  
- **Backend:** Python (Django + DRF)  
- **Frontend:** React (modular, component‑based)  
- **Database:** PostgreSQL (normalized, modular schema)

---

# 🧩 2. Modules Overview

Below are the modules defined for the MVP, each with a short description.

---

## 🔥 Core Module (Sample Domain)

The heart of the system. Everything revolves around the sample.

### **Tables**
- `samples` — main entity representing each lab sample  
- `clients` — who submitted the sample  
- `sample_status_history` — lifecycle changes (received, in progress, completed)  
- `chain_of_custody` — who handled the sample and when  
- `traceability_events` — universal timeline of all actions (timestamps live here)  
- `sample_metadata` — optional JSON or key‑value metadata  

### **Purpose**
Provides the foundation for all other modules.  
Everything else connects *to* the sample.

---

## 🧪 Assays Module

Defines what tests can be performed on a sample.

### **Tables**
- `assays` — test definitions  
- `assay_parameters` — dynamic fields for results (1, 2, or 20+ values)  
- `methodologies` — standards (ISO, BAM, AOAC, etc.)  
- `sample_assays` — join table linking samples ↔ assays  

### **Purpose**
Allows flexible test definitions and dynamic result structures.

---

## 🧬 Results Module

Handles all result data, independent of assay complexity.

### **Tables**
- `results` — one row per sample‑assay execution  
- `result_values` — one row per parameter (dynamic)  
- `result_attachments` — files, images, chromatograms  
- `result_validations` — approvals, signatures  

### **Purpose**
Supports simple and complex assays with unlimited result fields.

---

## 🔧 Instruments & Equipment Module

### **Tables**
- `instruments` — devices used in testing  
- `instrument_calibrations` — calibration records  
- `sample_instruments` — join table linking samples ↔ instruments  

### **Purpose**
Tracks instrument usage, calibration, and compliance.

---

## 🧴 Reagents & Consumables Module

### **Tables**
- `reagents` — chemicals, media, consumables  
- `reagent_lots` — lot tracking  
- `sample_reagents` — join table linking samples ↔ reagent lots  

### **Purpose**
Supports traceability of materials used in testing.

---

# 🕒 Traceability System (Inside Sample Module)

The universal audit trail.

### **Table: `traceability_events`**
- `sample_id`  
- `event_type`  
- `timestamp`  
- `user_id`  
- `reference_table`  
- `reference_id`  
- `notes`  

### **Purpose**
Stores ALL timestamps and events in one place.  
Modules push events here; UI decides what to show.

---

