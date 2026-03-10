Below is a **clean PRD-style document** following the structure you requested:

* **Business Idea**
* **User Cases (with flow + business logic)**
* **Payload Required**
* **Table Data Required**

I kept it **structured and concise**, like a document a **product manager would give to engineering**.

---

# Claim Insurance System PRD

# 1. Business Idea

The Claim Insurance system allows users to submit insurance claims that go through a **controlled verification and approval process**.

The system ensures:

* Claims are created as **drafts first**
* Users can **edit drafts before submission**
* Once submitted, claims become **read-only**
* A **Verifier** reviews the claim and writes a summary
* An **Approver** decides whether the claim is **approved or rejected**

To prevent duplicate claims, the system enforces a rule that:

> A user can only create **one claim per process**.

---

# 2. User Cases

---

# User Case 1 — User Create Claim Insurance

### Flow

1. User initiates **Create Claim Insurance**.
2. System generates a **claim number**.
3. System creates a new claim with status `draft` and auto generate number
4. User can update claim fields while the claim is still a draft.
```
// patch user info 
{
    "first_name" : string,
    "last_name" : string
    "email": string, 
    "phone_number" : digits,
    "user_id_number" string, 
}
//patch insurance info
{
    policy_number : id 
    policy_holder_number: string
    coverage_start_date: date, 
    coverage_end_date: date
}
```
5. When ready, the user **submits the claim**.
6. After submission, the claim becomes **read-only**.

---

### Business Logic

* When a user initiates a claim:

  * System generates `claim_number`.
  * Claim status is set to:

```
draft
```

* While status is `draft`:

  * User can update claim fields.

* When user submits the claim:

```
status → submitted
```

* After submission:

  * Claim **cannot be updated**
  * Claim becomes **view only**

* A user can only have **one claim per process**.

System validation:

If a user already has a claim with status:

```
draft
submitted
```

Then the system **must reject creation of a new claim**.

---

### Payload Required

#### Create Claim (Initiate Draft)

```
POST /claim-insurances
```

Payload

| Field      | Type   | Required |
| ---------- | ------ | -------- |
| process_id | number | yes      |

---

#### Update Draft Claim

```
PATCH /claim-insurances/{id}
```

Payload

| Field        | Type   | Required |
| ------------ | ------ | -------- |
| claim_date   | date   | no       |
| claim_type   | string | no       |
| description  | string | no       |
| claim_amount | number | no       |
| documents    | array  | no       |

---

#### Submit Claim

```
POST /claim-insurances/{id}/submit
```

Payload

```
(no body required)
```

---

### Table Data Required

#### claim_insurances

| Field        | Type      | Description                                        |
| ------------ | --------- | -------------------------------------------------- |
| id           | bigint    | primary key                                        |
| claim_number | varchar   | generated claim number                             |
| user_id      | bigint    | claim owner                                        |
| process_id   | bigint    | claim process                                      |
| status       | enum      | draft / submitted / reviewed / approved / rejected |
| claim_date   | date      | claim date                                         |
| claim_type   | varchar   | claim category                                     |
| description  | text      | claim description                                  |
| claim_amount | decimal   | claim value                                        |
| created_at   | timestamp | creation time                                      |
| updated_at   | timestamp | last update                                        |

---

# User Case 2 — Verifier Review Claim

### Flow

1. Verifier opens a **submitted claim**.
2. Verifier reviews the grouped claim data.
3. Verifier writes a **summary of the claim**.
4. Verifier verifies the claim.

---

### Business Logic

Verifier can only review claims with status:

```
submitted
```

Before verifying the claim, the verifier **must provide a summary**.

Validation rule:

```
review_summary must not be empty
```

After verification:

```
status → reviewed
```

After being reviewed:

* Claim becomes **read-only**
* No updates are allowed.

---

### Payload Required

#### Verify Claim

```
POST /claim-insurances/{id}/verify
```

Payload

| Field          | Type   | Required |
| -------------- | ------ | -------- |
| review_summary | string | yes      |

---

### Table Data Required

#### claim_reviews

| Field          | Type      | Description                 |
| -------------- | --------- | --------------------------- |
| id             | bigint    | primary key                 |
| claim_id       | bigint    | reference claim             |
| verifier_id    | bigint    | verifier user               |
| review_summary | text      | summary written by verifier |
| reviewed_at    | timestamp | review time                 |

---

# User Case 3 — Approver Decision

### Flow

1. Approver opens the **reviewed claim**.
2. Approver decides whether to:

   * Approve the claim
   * Reject the claim

---

### Business Logic

Approver can only make a decision when claim status is:

```
reviewed
```

If approved:

```
status → approved
```

If rejected:

```
status → rejected
```

Rejection may include a reason.

---

### Payload Required

#### Approve Claim

```
POST /claim-insurances/{id}/approve
```

Payload

```
(no body required)
```

---

#### Reject Claim

```
POST /claim-insurances/{id}/reject
```

Payload

| Field  | Type   | Required |
| ------ | ------ | -------- |
| reason | string | optional |

---

### Table Data Required

#### claim_approvals

| Field       | Type      | Description         |
| ----------- | --------- | ------------------- |
| id          | bigint    | primary key         |
| claim_id    | bigint    | claim reference     |
| approver_id | bigint    | approver            |
| decision    | enum      | approved / rejected |
| reason      | text      | rejection reason    |
| decided_at  | timestamp | decision time       |

---

✅ This format is typically used in **real product requirement documents for backend teams** because it clearly shows:

* **Business idea**
* **User flows**
* **Business rules**
* **API payloads**
* **Database structure**

---

If you want, I can also show you a **much stronger version of this PRD used in real fintech systems**, including:

* **state machine design**
* **API contract structure**
* **audit trail requirements**
* **event timeline**

which would make your system look **very senior-level in interviews or real projects**.


===========


make me a insurances table it will contain 
{
  number: string // the insurance number ex "INSR-ABC-001".
  title: string, 
  description: string, 
  priority: number // 1 to 5 
  amount: float // big number
}

then make the seeder if it, at lest make a 10 real word example of insurance product


then update the flow of create the claim_insurance, the user need to select what insurance product it want to claim. the user need to submit the insurance number to crete the claim

then on the claim_insurance no need to provide the amount, user do not need to specify the amount, it's already on the insurance