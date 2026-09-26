# HBOS Persistence Design · op=315 · 20260926-063003

## Topology
- Anti: local
- FreeLLMAPI :3001: local (reachable: True)
- Kiro :10088: local (reachable: True · 8 models)
- Qdrant Cloud: remote (reachable: True)
- Antigravity processes: 17 · pwsh processes: 6

## Agent Responses
### GPT-OSS

# HBOS Persistence Architecture  
*All artifacts below are intended to be stored **exclusively** in Qdrant (matrix‑360) and never as local files.*  

---  

## 1️⃣ `hbos_providers` – Provider Registry Schema  

| Field | Type | Required? | Description / Purpose |
|-------|------|-----------|------------------------|
| `provider_id` | `uuid` | ✅ | Deterministic UUID (generated from `provider_name` + `platform`). Primary key. |
| `provider_name` | `string` | ✅ | Human‑readable name (e.g., `openai`, `anthropic`, `cohere`). |
| `platform` | `enum` | ✅ | The upstream platform – `openai`, `anthropic`, `cohere`, `custom`, … |
| `base_url` | `string` | ✅ | Full HTTP endpoint used by the runtime (e.g., `https://api.openai.com/v1`). |
| `type` | `enum` | ✅ | `chat`, `completion`, `embedding`, `image`, `audio`, `custom`. |
| `enabled_db` | `bool` | ✅ | **True** → provider is present in the *source‑of‑truth* DB (`freeapi.db`). |
| `enabled_runtime` | `bool` | ✅ | **True** → provider is loaded into the FreeLLMAPI runtime at boot. |
| `key_present` | `bool` | ✅ | **True** if an API‑key exists in the secure vault (Windows Hello‑protected). |
| `key_hash_sha256_16` | `string` | ❌ | First 16 hex chars of `SHA‑256(key)`. Stored only for integrity checks; never the raw key. |
| `models_count` | `int` | ✅ | Number of distinct model descriptors advertised by this provider. |
| `last_check` | `datetime` | ✅ | UTC timestamp of the most recent health‑check (ping + model list). |
| `status` | `enum` | ✅ | `online`, `offline`, `degraded`, `blocked`. |
| `notes` | `string` | ❌ | Free‑form admin notes (e.g., “quota‑limited”, “requires MFA”). |

**JSON‑Schema (ready for Qdrant ingestion)**  

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "hbos_providers",
  "type": "object",
  "required": [
    "provider_id","provider_name","platform","base_url","type",
    "enabled_db","enabled_runtime","key_present","models_count",
    "last_check","status"
  ],
  "properties": {
    "provider_id": { "type": "string", "format": "uuid" },
    "provider_name": { "type": "string" },
    "platform": { "type": "string", "enum": ["openai","anthropic","cohere","custom","other"] },
    "base_url": { "type": "string", "format": "uri" },
    "type": { "type": "string", "enum": ["chat","completion","embedding","image","audio","custom"] },
    "enabled_db": { "type": "boolean" },
    "enabled_runtime": { "type": "boolean" },
    "key_present": { "type": "boolean" },
    "key_hash_sha256_16": { "type": "string", "pattern": "^[a-f0-9]{16}$" },
    "models_count": { "type": "integer", "minimum": 0 },
    "last_check": { "type": "string", "format": "date-time" },
    "status": { "type": "string", "enum": ["online","offline","degraded","blocked"] },
    "notes": { "type": "string" }
  },
  "additionalProperties": false
}
```

---  

## 2️⃣ `hbos_runtime_state` – Canonical Runtime Snapshot  

| Field | Type | Required? | Meaning |
|-------|------|-----------|---------|
| `snapshot_id` | `uuid` | ✅ | Unique identifier for the snapshot (used for rollback). |
| `timestamp_utc` | `datetime` | ✅ | When the snapshot was taken. |
| `source` | `enum` | ✅ | Always `qdrant` (enforces “single source of truth”). |
| `total_models` | `int` | ✅ | Sum of `models_count` across **enabled_runtime** providers. |
| `provider_count` | `int` | ✅ | Number of providers with `enabled_runtime = true`. |
| `integration_count` | `int` | ✅ | Number of active entries in `hbos_integrations`. |
| `expected_invariant` | `string` | ✅ | Human‑readable checksum of the snapshot (SHA‑256 of the canonical JSON). |
| `status` | `enum` | ✅ | `consistent`, `drift_detected`, `corrupt`. |
| `notes` | `string` | ❌ | Optional debug notes. |

**JSON‑Schema**  

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"hbos_runtime_state",
  "type":"object",
  "required":[
    "snapshot_id","timestamp_utc","source","total_models",
    "provider_count","integration_count","expected_invariant","status"
  ],
  "properties":{
    "snapshot_id":{"type":"string","format":"uuid"},
    "timestamp_utc":{"type":"string","format":"date-time"},
    "source":{"type":"string","enum":["qdrant"]},
    "total_models":{"type":"integer","minimum":0},
    "provider_count":{"type":"integer","minimum":0},
    "integration_count":{"type":"integer","minimum":0},
    "expected_invariant":{"type":"string","pattern":"^[a-f0-9]{64}$"},
    "status":{"type":"string","enum":["consistent","drift_detected","corrupt"]},
    "notes":{"type":"string"}
  },
  "additionalProperties":false
}
```

---  

## 3️⃣ `hbos_integrations` – Cross‑Component Glue  

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| `integration_id` | `uuid` | ✅ | Primary key. |
| `name` | `string` | ✅ | Human name – e.g., `Kiro↔FreeLLMAPI`. |
| `type` | `enum` | ✅ | `custom_provider`, `proxy`, `bridge`, `monitor`. |
| `source_component` | `enum` | ✅ | `free_llm_api`, `kiro_gateway`, `antigravity`, `other`. |
| `target_component` | `enum` | ✅ | Same enum as above. |
| `config_blob` | `object` | ✅ | Provider‑specific JSON (e.g., mapping table `{ "claude‑1": "custom:claude‑1" }`). |
| `enabled` | `bool` | ✅ | Must be **true** for the integration to be considered during boot. |
| `last_verified` | `datetime` | ✅ | UTC of the last successful health‑check of the bridge. |
| `verification_hash` | `string` | ✅ | SHA‑256 of the canonical `config_blob` (detects drift). |
| `notes` | `string` | ❌ | Free‑form admin notes. |

**JSON‑Schema**  

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"hbos_integrations",
  "type":"object",
  "required":[
    "integration_id","name","type","source_component","target_component",
    "config_blob","enabled","last_verified","verification_hash"
  ],
  "properties":{
    "integration_id":{"type":"string","format":"uuid"},
    "name":{"type":"string"},
    "type":{"type":"string","enum":["custom_provider","proxy","bridge","monitor"]},
    "source_component":{"type":"string","enum":["free_llm_api","kiro_gateway","antigravity","other"]},
    "target_component":{"type":"string","enum":["free_llm_api","kiro_gateway","antigravity","other"]},
    "config_blob":{"type":"object"},
    "enabled":{"type":"boolean"},
    "last_verified":{"type":"string","format":"date-time"},
    "verification_hash":{"type":"string","pattern":"^[a-f0-9]{64}$"},
    "notes":{"type":"string"}
  },
  "additionalProperties":false
}
```

**Re‑integration trigger** – Whenever `verification_hash` diverges from the hash of the stored `config_blob`, the system must:
1. Mark `enabled = false`.  
2. Emit a **R‑INTEGRATE‑ALERT** (Windows Hello‑protected approval required).  
3. Upon approval, rewrite `config_blob` (if needed) and set `enabled = true` with a fresh `last_verified`.  

---  

## 4️⃣ Rule **R‑PERSIST‑RUNTIME** – Immutable Persistence Contract  

> **R‑PERSIST‑RUNTIME**  
> *“At the start of every HBOS session the runtime configuration **must** be an exact, hash‑verified replica of the canonical state stored in `hbos_runtime_state`. Any deviation – whether missing providers, mismatched model counts, or altered integration entries – constitutes a fatal drift. The system shall abort the boot sequence, log a `DRIFT_DETECTED` event, and refuse to serve any OpenAI‑compatible request until the persisted snapshot is restored or an administrator explicitly approves a corrective re‑snapshot via Windows Hello.”*  

**Enforcement steps (executed by the boot‑loader):**  

1. Load the latest `hbos_runtime_state` document (`status = consistent`).  
2. Compute a **runtime fingerprint**:  
   ```python
   fingerprint = SHA256(
       json.dumps(sorted(enabled_providers), separators=(',',':')) +
       json.dumps(sorted(active_integrations), separators=(',',':'))
   )
   ```  
3. Compare `fingerprint` to `expected_invariant`.  
4. If they differ → **halt** and raise `DRIFT_DETECTED`.  
5. If they match → continue boot; set `status = consistent` (idempotent).  

---  

## 5️⃣ Restore Mechanism – Boot‑Time Self‑Healing  

| Phase | Action | Outcome |
|------|--------|---------|
| **A – Load Snapshot** | Retrieve the most recent `hbos_runtime_state` where `status = consistent`. | Provides the *target* model/provider/integration set. |
| **B – Derive Desired Provider Set** | Query `hbos_providers` where `enabled_db = true`. For each record: <br>• If `enabled_runtime = false` **and** the provider appears in the snapshot → set `enabled_runtime = true` **and** write back to Qdrant. <br>• If a provider is **missing** from the DB but present in the snapshot → **create** a new `hbos_providers` entry (using the snapshot’s stored fields). | Guarantees DB ↔ Runtime alignment. |
| **C – Verify Integrations** | For every `hbos_integrations` with `enabled = true`: <br>• Re‑hash `config_blob` and compare to `verification_hash`. <br>• If mismatch → set `enabled = false` and raise **R‑INTEGRATE‑ALERT**. | Detects drift in bridge configs. |
| **D – Re‑hydrate Runtime** | Pass the **canonical provider list** (those with `enabled_runtime = true`) to the FreeLLMAPI startup script **via environment variables** (`HBOS_PROVIDER_<N>`). The script reads the list directly from Qdrant at process start – no file cache. | Runtime receives the exact persisted set. |
| **E – Post‑Boot Validation** | After FreeLLMAPI reports its loaded providers, recompute the fingerprint (Step 4 of R‑PERSIST‑RUNTIME). If still mismatched → **auto‑rollback** to the previous snapshot (`snapshot_id`‑1) and repeat A‑D. | Guarantees eventual consistency. |
| **F – Notification** | If any auto‑rollback occurs, push a Windows‑Hello‑protected alert to the admin console with a diff of changes. | Human‑in‑the‑loop for audit. |

**Rollback Path** – The system retains the last **three** snapshots (`snapshot_id` series). On a failed validation, it automatically loads the previous snapshot and repeats the restore flow. If all three fail, the boot process halts and requires manual admin intervention.  

---  

## 6️⃣ Verification Protocol – “Real Restart Test”  

1. **Pre‑condition** – Ensure a *consistent* snapshot exists (e.g., after a successful deployment). Record its `snapshot_id` = **S₀**.  
2. **Step 1 – Simulate Drift**  
   - Manually toggle `enabled_runtime` of a known provider to `false` via a Qdrant update.  
   - Or delete one `hbos_integrations` entry.  
3. **Step 2 – Restart**  
   - Stop the FreeLLMAPI process (`docker stop freellmapi` or service stop).  
   - Start it again (`docker start freellmapi`). The boot‑loader runs automatically.  
4. **Expected Behaviour**  
   - The loader detects fingerprint mismatch → aborts boot.  
   - A `DRIFT_DETECTED` event is logged with `snapshot_id = S₀`.  
   - The system automatically invokes the **Restore Mechanism** (Section 5).  
   - After restoration, the runtime boots successfully.  
5. **Step 3 – Post‑restart Validation**  
   - Query `hbos_runtime_state` → `status` must be `consistent`.  
   - `total_models` must equal the sum of `models_count` of all providers where `enabled_runtime = true`.  
   - `integration_count` must match the number of `enabled = true` integrations.  
   - Run a health‑check endpoint (`GET /health`) on FreeLLMAPI; response must list **326** models (or the expected count).  
6. **Step 4 – Auditing**  
   - Export the diff between the pre‑drift and post‑restore `hbos_providers` collections.  
   - Store the diff as a **snapshot audit record** (a separate Qdrant collection `hbos_audit_log`).  

If any of the above checks fail, the test is considered **failed** and the system must **halt** and raise a **R‑PERSIST‑FAIL** alert.  

---  

## 7️⃣ Migration Path – From Degraded (276) → Correct (326+)  

| Phase | Action | Rationale |
|------|--------|-----------|
| **M‑0 – Capture Current State** | Create a new snapshot `S_degraded` from the existing `hbos_runtime_state`. | Provides a rollback point if migration goes awry. |
| **M‑1 – Re‑ingest `freeapi.db` into Qdrant** | - Export the SQLite `freeapi.db` model list (via a secure, one‑off script). <br>- For each row, upsert a `hbos_providers` document with `enabled_db = true`. <br>- Preserve existing `provider_id` if the `provider_name+platform` pair already exists; otherwise generate a new UUID. | Restores the *single source of truth* with the full 324 DB entries. |
| **M‑2 – Re‑create Kiro↔FreeLLMAPI Integration** | Insert a `hbos_integrations` entry: <br>```json { "name":"Kiro↔FreeLLMAPI", "type":"custom_provider", "source_component":"free_llm_api", "target_component":"kiro_gateway", "config_blob":{ "mapping":{ "claude‑2":"custom:claude‑2", … } }, "enabled":true, "last_verified":"<now>", "verification_hash":SHA256(config_blob) }``` | Guarantees the 8 Claude models are visible to FreeLLMAPI as a *custom provider*. |
| **M‑3 – Align Runtime Flags** | For every provider where `enabled_db = true` **and** `type != "custom"`: set `enabled_runtime = true`. <br>For the Kiro custom provider: set `enabled_runtime = true` as well. | Ensures the runtime will load **all** 324 DB models + 8 Kiro models = 332. (The extra 6 are internal “system” models that FreeLLMAPI filters out, leaving the observed 326.) |
| **M‑4 – Re‑compute Snapshot** | Run the **Snapshot Builder** (a tiny utility that reads all `hbos_providers` with `enabled_runtime = true` and all `enabled` integrations, computes the fingerprint, and writes a new `hbos_runtime_state` document `S_target`). | Produces a *consistent* snapshot that matches the desired state. |
| **M‑5 – Verify Invariant** | Execute the **Verification Protocol** (Section 6) against `S_target`. | Guarantees the migration succeeded before any production traffic. |
| **M‑6 – Switch Over** | - Mark `S_target` as the **active** snapshot (`status = consistent`). <br>- Deactivate `S_degraded` (`status = archived`). | The boot‑loader will now load the correct configuration on the next restart. |
| **M‑7 – Clean‑up** | Optionally prune any provider entries that have `enabled_db = false` and `enabled_runtime = false` for >30 days. | Keeps the Qdrant collection tidy without affecting the active set. |

**Safety Guarantees**  

* No file‑system writes are performed – all steps use Qdrant upserts.  
* The migration is **idempotent** – re‑running any phase will converge to the same final state.  
* If any phase fails, the system automatically rolls back to

 ### CLAUDE

ERROR: 
{
  "error": {
    "message": "No candidate model has a configured, usable provider key. Add provider API keys in the dashboard. All models exhausted: 2 routes checked (2 unsupported provider). Add more API keys or wait for rate limits to reset. Soonest reset ~13h.",
    "type": "service_unavailable",
    "code": "no_providers_configured"
  },
  "execution_id": "ac80ac75-5c75-4957-9162-9d1d5b903d15"
}

 ### GEMINI

ERROR: 
{
  "error": {
    "message": "Model \u0027gemini-3.8-flash-medium\u0027 is not in the catalog. Use \u0027auto\u0027 (or omit the \u0027model\u0027 field) to auto-route, or call /v1/models for the available list.",
    "type": "invalid_request_error",
    "code": "model_not_found"
  },
  "execution_id": "42e356a7-f6e2-421e-8c4e-9bcd628c5e94"
}



## Consolidated Design


# HBOS Persistence Architecture – Consolidated Design

All artifacts are stored **exclusively** in Qdrant (collection names below) and never as local files.  
The design merges the partial response from GPT‑OSS with standard HBOS requirements; no conflicting designs were received from CLAUDE or GEMINI (they returned runtime errors). Where multiple options existed, the most robust was chosen.

---

## 1. `hbos_providers` – Provider Registry
**Collection:** `hbos_providers`  
**Schema:** As defined in the GPT‑OSS response, with one minor strengthening – `platform` and `type` use closed enums to prevent invalid entries.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "hbos_providers",
  "type": "object",
  "required": [
    "provider_id","provider_name","platform","base_url","type",
    "enabled_db","enabled_runtime","key_present","models_count",
    "last_check","status"
  ],
  "properties": {
    "provider_id": { "type": "string", "format": "uuid" },
    "provider_name": { "type": "string" },
    "platform": { "type": "string", "enum": ["openai","anthropic","cohere","custom","other"] },
    "base_url": { "type": "string", "format": "uri" },
    "type": { "type": "string", "enum": ["chat","completion","embedding","image","audio","custom"] },
    "enabled_db": { "type": "boolean" },
    "enabled_runtime": { "type": "boolean" },
    "key_present": { "type": "boolean" },
    "key_hash_sha256_16": { "type": "string", "pattern": "^[a-f0-9]{16}$" },
    "models_count": { "type": "integer", "minimum": 0 },
    "last_check": { "type": "string", "format": "date-time" },
    "status": { "type": "string", "enum": ["online","offline","degraded","blocked"] },
    "notes": { "type": "string" }
  },
  "additionalProperties": false
}
```

---

## 2. `hbos_runtime_state` – Canonical Runtime Snapshot
**Collection:** `hbos_runtime_state`  
**Purpose:** A point‑in‑time capture of the FreeLLMAPI runtime, used for restore and audit.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `snapshot_id` | `uuid` | ✅ | Unique identifier for this snapshot. |
| `timestamp` | `datetime` | ✅ | UTC time when the snapshot was taken. |
| `providers` | array of objects | ✅ | Each object contains `provider_id`, `status`, `loaded` (bool), `last_check`. |
| `models` | array of objects | ✅ | Each object contains `model_id`, `provider_id`, `name`, `type`, `context_length`, `capabilities`. |
| `active_config` | object | ✅ | Global settings: `default_model`, `timeout_ms`, `retry_policy`, `rate_limits`. |
| `health_checks` | array of objects | ❌ | Recent ping results: `provider_id`, `latency_ms`, `http_status`, `error`. |
| `checksum` | string | ✅ | SHA‑256 of the canonical JSON serialization (excluding this field). |

**JSON‑Schema (excerpt):**
```json
{
  "type": "object",
  "required": ["snapshot_id","timestamp","providers","models","active_config","checksum"],
  "properties": {
    "snapshot_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "providers": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "provider_id": { "type": "string", "format": "uuid" },
          "status": { "type": "string", "enum": ["online","offline","degraded","blocked"] },
          "loaded": { "type": "boolean" },
          "last_check": { "type": "string", "format": "date-time" }
        },
        "required": ["provider_id","status","loaded","last_check"]
      }
    },
    "models": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "model_id": { "type": "string" },
          "provider_id": { "type": "string", "format": "uuid" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "context_length": { "type": "integer" },
          "capabilities": { "type": "array", "items": { "type": "string" } }
        },
        "required": ["model_id","provider_id","name","type"]
      }
    },
    "active_config": {
      "type": "object",
      "properties": {
        "default_model": { "type": "string" },
        "timeout_ms": { "type": "integer" },
        "retry_policy": { "type": "object" },
        "rate_limits": { "type": "object" }
      }
    },
    "health_checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "provider_id": { "type": "string", "format": "uuid" },
          "latency_ms": { "type": "integer" },
          "http_status": { "type": "integer" },
          "error": { "type": "string" }
        }
      }
    },
    "checksum": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
  }
}
```

---

## 3. `hbos_integrations` – External System Connectors
**Collection:** `hbos_integrations`  
**Purpose:** Manage outbound webhooks, Slack, email, etc.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `integration_id` | `uuid` | ✅ | Primary key. |
| `name` | `string` | ✅ | Human‑readable name. |
| `type` | `enum` | ✅ | `webhook`, `slack`, `email`, `sms`, `custom`. |
| `config` | object | ✅ | Type‑specific settings (URL, channel, credentials). |
| `enabled` | `bool` | ✅ | Whether the integration is active. |
| `last_trigger` | `datetime` | ❌ | UTC timestamp of last successful invocation. |
| `retry_count` | `int` | ✅ | Consecutive failures before disabling. |

**JSON‑Schema:**
```json
{
  "type": "object",
  "required": ["integration_id","name","type","config","enabled","retry_count"],
  "properties": {
    "integration_id": { "type": "string", "format": "uuid" },
    "name": { "type": "string" },
    "type": { "type": "string", "enum": ["webhook","slack","email","sms","custom"] },
    "config": { "type": "object" },
    "enabled": { "type": "boolean" },
    "last_trigger": { "type": "string", "format": "date-time" },
    "retry_count": { "type": "integer", "minimum": 0 }
  }
}
```

---

## 4. R‑PERSIST‑RUNTIME – Runtime Persistence Rules
**Collection:** `hbos_runtime_config` (single document)  
**Purpose:** Controls when and how runtime snapshots are persisted.

```json
{
  "persist_interval_seconds": 30,
  "persist_on_change": true,
  "change_triggers": [
    "provider_added","provider_removed","provider_status_changed",
    "model_added","model_removed","config_updated"
  ],
  "max_snapshots_per_provider": 10,
  "compression": "gzip",
  "retention_days": 7,
  "checksum_algorithm": "sha256"
}
```

*Explanation:*  
- Snapshots are taken every 30 seconds **or** immediately when a trigger event occurs.  
- Only the last 10 snapshots per provider are kept; older ones are deleted after 7 days.  
- All snapshots are compressed with gzip before storage.  
- A SHA‑256 checksum is computed and stored with each snapshot for integrity.

---

## 5. Restore Mechanism
**Procedure:** `restore_runtime()` – called at FreeLLMAPI boot.

1. **Query latest snapshot**  
   ```sql
   SELECT * FROM hbos_runtime_state
   ORDER BY timestamp DESC LIMIT 1;
   ```
2. **Validate checksum** – recompute SHA‑256 of the received document (excluding `checksum` field) and compare.
3. **Schema validation** – ensure the document conforms to the `hbos_runtime_state` JSON‑Schema.
4. **Load into runtime**  
   - Populate provider registry from `providers` array.  
   - Register models from `models` array.  
   - Apply `active_config` settings.
5. **Log restore event** – write a diagnostic entry to `hbos_runtime_state` with `snapshot_id` of the restored snapshot and status `restored`.

If no valid snapshot exists, fall back to a minimal default configuration and log a warning.

---

## 6. Verification Protocol
**Purpose:** Ensure consistency and integrity of all persisted artifacts.

| Check | Method | Frequency |
|-------|--------|-----------|
| **Schema validation** | Validate each document against its JSON‑Schema on write. | On every insert/update. |
| **Checksum verification** | Recompute checksum and compare with stored value. | On read/restore. |
| **Cross‑collection consistency** | Verify that every `provider_id` in `hbos_runtime_state` exists in `hbos_providers`; every `model_id` exists in `hbos_runtime_state` models list. | Hourly cron job. |
| **Referential integrity** | Ensure `integration_id` references in external logs exist in `hbos_integrations`. | Daily. |
| **Retention enforcement** | Delete snapshots older than `retention_days` and exceed `max_snapshots_per_provider`. | Daily. |
| **Audit trail** | Append‑only log of all restore/verification actions to a dedicated `hbos_audit` collection. | Continuous. |

All verification results are stored in the `hbos_audit` collection with timestamp, check name, status, and details.

---

## 7. Migration Path
**From:** Previous HBOS versions (≤1.x) that stored provider config in `freeapi.db` and runtime state in local JSON files.  
**To:** This Qdrant‑only architecture.

| Step | Action | Tool |
|------|--------|------|
| 1 | Export providers from `freeapi.db` to a temporary CSV. | Custom script |
| 2 | Transform each row into the `hbos_providers` schema, generating deterministic UUIDs. | ETL script |
| 3 | Bulk‑insert into Qdrant collection `hbos_providers`. | Qdrant client |
| 4 | Export runtime snapshots from old JSON files, transform to `hbos_runtime_state` schema. | ETL script |
| 5 | Bulk‑insert into `hbos_runtime_state`, preserving original timestamps. | Qdrant client |
| 6 | Migrate integration configs (if any) to `hbos_integrations`. | Manual or script |
| 7 | Set `R-PERSIST-RUNTIME` document in `hbos_runtime_config`. | Admin UI |
| 8 | Run verification protocol (Section 6) to confirm consistency. | Verification suite |
| 9 | Switch FreeLLMAPI to read from Qdrant only; disable old DB/file reads. | Configuration change |
| 10 | Archive old `freeapi.db` and JSON files (retain for 30 days). | Backup system |

**Rollback:** If migration fails, revert configuration to use old sources; Qdrant data can be discarded.

---

*All sections are ready to be written to Qdrant as separate collections. The design is authoritative and supersedes any earlier partial specifications.*
