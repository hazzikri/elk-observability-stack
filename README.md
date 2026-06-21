# Centralized Log Aggregation with ELK Stack

[![Elasticsearch](https://img.shields.io/badge/Storage-Elasticsearch%208.13-005571?style=for-the-badge&logo=elasticsearch)](https://www.elastic.co/elasticsearch/)
[![Logstash](https://img.shields.io/badge/Pipeline-Logstash%208.13-005571?style=for-the-badge&logo=logstash)](https://www.elastic.co/logstash/)
[![Kibana](https://img.shields.io/badge/Visualization-Kibana%208.13-005571?style=for-the-badge&logo=kibana)](https://www.elastic.co/kibana/)
[![Docker Compose](https://img.shields.io/badge/Deployment-Docker%20Compose-2496ED?style=for-the-badge&logo=docker)](https://docs.docker.com/compose/)

A production-representative **ELK Stack** observability deployment built with Docker Compose, demonstrating centralized log aggregation, parsing pipeline design, and real-time Kibana dashboarding — the same pattern used in the production environment at **PT Link Net Tbk** to reduce Mean Time to Detection (MTTD) for production incidents.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          Applications                            │
│  ┌─────────────┐   ┌───────────────┐   ┌────────────────────┐   │
│  │ App Service │   │  Nginx Access │   │  System / Syslog   │   │
│  │ (JSON logs) │   │  Logs         │   │  Events            │   │
│  └──────┬──────┘   └───────┬───────┘   └────────┬───────────┘   │
│         └──────────────────┴────────────────────┘               │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        LOGSTASH :5044/:5000                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  INPUT (Beats/TCP/File) → FILTER (Grok/GeoIP/Mutate)      │  │
│  │  → OUTPUT (Elasticsearch index: app-logs-YYYY.MM.dd)      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              ELASTICSEARCH :9200 (Search & Storage)             │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │  Time-series index per day: app-logs-2025.01.15        │  │
│    │  Full-text search, aggregations, field mappings         │  │
│    └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     KIBANA :5601 (UI)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Discover    │ │  Dashboards  │ │  Alerts      │            │
│  │  (raw logs)  │ │  (charts)    │ │  (anomalies) │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
* Docker Engine + Docker Compose
* Minimum **4GB RAM** allocated to Docker

### Start the Stack
```bash
git clone https://github.com/hazzikri/elk-observability-stack.git
cd elk-observability-stack
docker-compose up -d
```

### Access Points
| Service | URL | Default Credentials |
|---|---|---|
| **Kibana** | http://localhost:5601 | No auth (dev mode) |
| **Elasticsearch** | http://localhost:9200 | No auth (dev mode) |
| **Logstash Metrics** | http://localhost:9600 | N/A |

### Verify Elasticsearch is Healthy
```bash
curl http://localhost:9200/_cluster/health?pretty
```

### Check Log Indices are Being Created
```bash
curl http://localhost:9200/_cat/indices?v
```

### Explore Logs in Kibana
1. Open `http://localhost:5601`
2. Go to **Stack Management → Index Patterns → Create**
3. Enter pattern: `app-logs-*`
4. Select `@timestamp` as the time field
5. Go to **Discover** to start exploring logs

---

## 📄 Logstash Pipeline (`logstash.conf`)

The Logstash pipeline demonstrates 3 core capabilities:

### 1. Multi-format Input
- **Port 5044 (Beats):** Accepts structured input from Filebeat agents (typical production setup).
- **Port 5000 (TCP):** Accepts direct JSON log shipping from microservices.
- **File input:** Reads from mounted log volume (simulated via `log-generator` container).

### 2. Log Enrichment Filter Chain
- **Grok:** Parses raw Nginx access log text format into structured fields.
- **Date:** Normalizes timestamps to `@timestamp` for proper Kibana timeline sorting.
- **GeoIP:** Enriches client IP addresses with geographic metadata (country, city, coordinates).
- **Mutate:** Adds computed fields (e.g., `log_level` based on HTTP status code).

### 3. Daily Index Output
Logs are indexed into Elasticsearch with daily rolling indices: `app-logs-YYYY.MM.dd`, enabling efficient data lifecycle management and retention policies.

---

## 🔧 Production Hardening Notes

For production use at enterprise scale (as applied at PT Link Net Tbk):
- Enable **X-Pack Security** (`xpack.security.enabled: true`) with TLS and username/password auth.
- Deploy Elasticsearch as a **3-node cluster** for high availability.
- Add **Elasticsearch Curator** or **ILM (Index Lifecycle Management)** policies to auto-delete old indices.
- Use **Filebeat** on each application host for reliable log shipping (handles backpressure and restarts).
- Set up **Kibana Alerts** for anomaly detection (e.g., spike in HTTP 5xx errors triggers PagerDuty).
