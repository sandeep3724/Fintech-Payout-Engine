# Fintech Payout Engine - Explainer

## Overview
This project is a simplified fintech payout system inspired by platforms like Razorpay and Paytm. It allows merchants to request payouts, manages balances using a ledger system, and ensures safe transaction handling using idempotency and concurrency control.

---

## Core Features

### 1. Merchant Dashboard
- Displays available balance
- Shows held balance (funds locked for payouts)
- Lists payout history
- Shows recent ledger entries

---

### 2. Ledger-Based Accounting (Important Concept)
Instead of storing balance directly, the system uses a **ledger-based model**:

- CREDIT → Adds money  
- DEBIT → Deducts money  

Balance is calculated dynamically:


This approach ensures:
- Accuracy
- Auditability
- No direct balance manipulation

---

### 3. Payout Flow


Steps:
1. Merchant requests payout
2. System checks available balance
3. Funds are locked (held balance)
4. Ledger entry is created
5. Payout is processed asynchronously
6. Status is updated

---

### 4. Idempotency (Critical Fintech Concept)

Each payout request includes:


If the same request is sent multiple times:
- Only one payout is created
- Duplicate requests return the same response

This prevents:
- Double payouts
- Duplicate transactions

---

### 5. Payout Lifecycle


- **pending** → payout created  
- **processing** → payout being processed  
- **success** → payout completed  
- **failed** → payout failed  

---

### 6. Concurrency Handling

To avoid race conditions, the system uses:


This locks the merchant row during payout creation, ensuring:
- No double spending
- Correct balance calculation

---

### 7. Background Processing

Payout processing is handled using:
- Celery (design)
- Direct execution fallback (for deployment)

Simulated behavior:
- Processing delay
- Random success/failure outcome

---

## Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL (Render)

### Frontend
- React (Vite)
- Axios

### Deployment
- Backend → Render
- Frontend → Vercel

---

## API Endpoints

### Get Merchant Dashboard

### Create Payout

---

## Key Learnings

- Idempotency in financial systems
- Ledger-based balance management
- Concurrency control using database locks
- Full-stack deployment (React + Django)
- Debugging real-world API issues

---

## Future Improvements

- Retry mechanism for failed payouts
- Full Celery + Redis worker setup
- Authentication (JWT / API keys)
- Webhooks for payout updates
- Real bank API integration simulation

---

## Conclusion

This project demonstrates core fintech backend principles such as:

- Safe transaction handling  
- Accurate balance management  
- Prevention of duplicate transactions  
- Scalable payout processing design  

It simulates real-world payout systems used in fintech platforms like Razorpay and Paytm.
