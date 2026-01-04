# 🏗️ System Architecture

## Overview

The Hospital Inventory Management System is built on Snowflake's Data Cloud platform, leveraging native features for automation, computation, and visualization.

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                    DATA INGESTION LAYER                  │
├─────────────────────────────────────────────────────────┤
│  • Daily Stock Data (CSV/API)                           │
│  • Manual Entry via Streamlit                            │
│  • Automated Feeds from Hospital Systems                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Master     │  │ Transactional│  │   Alert      │ │
│  │   Tables     │  │    Tables    │  │   Tables     │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ • Hospitals  │  │ • Daily Stock│  │ • Alerts     │ │
│  │ • Departments│  │   Movements  │  │ • Action Log │ │
│  │ • Items      │  │              │  │              │ │
│  │ • Suppliers  │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                 COMPUTATION LAYER                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐  │
│  │         STOCK_METRICS (Dynamic Table)            │  │
│  │  • Auto-refreshes every hour                     │  │
│  │  • Calculates 7-day consumption trends           │  │
│  │  • Computes days of stock remaining              │  │
│  │  • Assigns health status                         │  │
│  │  • Suggests reorder quantities                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │              12+ Analytical Views                │  │
│  │  • Pre-computed aggregations                     │  │
│  │  • Department summaries                          │  │
│  │  • Alert prioritization                          │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  AUTOMATION LAYER                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌────────────────────┐   │
│  │  Stream          │────────▶│  Task              │   │
│  │  (Change Data    │         │  (Scheduled        │   │
│  │   Capture)       │         │   Alert Gen)       │   │
│  └──────────────────┘         └────────────────────┘   │
│                                         │               │
│                                         ▼               │
│                                ┌────────────────────┐   │
│                                │  Stored Procedures │   │
│                                │  • Generate Alerts │   │
│                                │  • Acknowledge     │   │
│                                │  • Mark Ordered    │   │
│                                └────────────────────┘   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────┤
│                  Streamlit Dashboard                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Overview   │  │   Heatmap    │  │   Alerts     │ │
│  │   Page       │  │   Page       │  │   Page       │ │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤ │
│  │ • KPIs       │  │ • Color Grid │  │ • Priority   │ │
│  │ • Dept Table │  │ • Filters    │  │ • Actions    │ │
│  │ • Exports    │  │ • Export     │  │ • Export     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer

#### Master Tables
- **HOSPITALS**: Hospital metadata (1 record)
- **DEPARTMENTS**: 5 departments (ICU, Emergency, Surgery, General Ward, Pharmacy)
- **ITEMS_MASTER**: 40 medical items with criticality levels
- **SUPPLIERS**: 6 suppliers with lead times

#### Transactional Tables
- **HOSPITAL_STOCK_DAILY**: Daily stock movements (~8,500 records for 90 days)
  - Tracks: opening stock, received, consumed, expired, closing stock
  - Includes: expiry dates, batch numbers, supplier info

#### Alert Tables
- **STOCK_ALERTS**: Generated alerts with priorities
- **ALERT_ACTION_LOG**: Audit trail of user actions

### 2. Intelligence Layer

#### Dynamic Table: STOCK_METRICS
- **Refresh Frequency**: Every 1 hour (TARGET_LAG)
- **Calculations**:
  - 7-day rolling average consumption
  - Days of stock remaining = current_stock / avg_consumption
  - Stock status classification (STOCKOUT, CRITICAL, LOW, OK, EXCESS)
  - Reorder flags and suggested quantities
  - Priority scores based on criticality + department

#### Views (12+)
- V_LATEST_STOCK_METRICS
- V_ACTIVE_ALERTS
- V_ALERT_SUMMARY
- V_DEPARTMENT_ALERT_SUMMARY
- V_CRITICAL_ALERTS
- V_EXPIRY_RISK_DASHBOARD
- V_DEPARTMENT_SUMMARY
- V_ITEM_PERFORMANCE_SUMMARY
- V_STOCK_HEATMAP_DATA
- V_KPI_SUMMARY
- V_ALERT_ACTION_HISTORY
- V_RECENT_CONSUMPTION_TRENDS

### 3. Automation Layer

#### Stream: HOSPITAL_STOCK_STREAM
- Captures INSERT/UPDATE/DELETE on HOSPITAL_STOCK_DAILY
- Enables incremental processing

#### Task: TASK_GENERATE_STOCK_ALERTS
- **Schedule**: Runs every 60 minutes
- **Function**: Calls GENERATE_STOCK_ALERTS() procedure
- **Alert Types Generated**:
  - STOCKOUT (priority: URGENT)
  - STOCKOUT_RISK (priority: HIGH/URGENT)
  - EXPIRY_RISK (priority: HIGH/MEDIUM)
  - OVERSTOCK (priority: LOW)

#### Stored Procedures (5)
1. **GENERATE_STOCK_ALERTS()**: Main alert generation logic
2. **ACKNOWLEDGE_ALERT(alert_id, user, notes)**: Mark alert as seen
3. **MARK_ORDER_PLACED(alert_id, user, order_ref, ...)**: Log purchase order
4. **RESOLVE_ALERT(alert_id, user, notes)**: Close alert
5. **ACKNOWLEDGE_DEPT_ALERTS(dept, user, notes)**: Bulk acknowledge

### 4. Presentation Layer

#### Streamlit Dashboard (3 Pages)

**Page 1: Overview**
- 5 KPI cards (Total, Urgent, High, Medium, Low alerts)
- 4 Alert type metrics (Stockouts, Stockout Risk, Expiry Risk, Healthy)
- 3 Financial metrics (Inventory Value, Reorder Cost, Waste Risk)
- Department summary table
- Export options (3 CSV downloads)

**Page 2: Stock Heatmap**
- Filters: Department, Category, Status
- Color-coded table (Red → Green based on days remaining)
- Summary statistics
- CSV export

**Page 3: Active Alerts**
- Filters: Severity, Type, Department
- Expandable alert cards
- Action buttons: Acknowledge, Mark as Ordered, Resolve
- Individual and bulk export

## Data Flow
```
Raw Stock Data → HOSPITAL_STOCK_DAILY
                        ↓
                 (Stream captures changes)
                        ↓
                 STOCK_METRICS (auto-refresh)
                        ↓
                 (Task runs every hour)
                        ↓
                 GENERATE_STOCK_ALERTS()
                        ↓
                 STOCK_ALERTS + ALERT_ACTION_LOG
                        ↓
                 Streamlit Dashboard
                        ↓
                 User Actions → Logged back to DB
```

## Performance Optimization

1. **Clustering**: Applied on STOCK_ALERTS and ALERT_ACTION_LOG for faster queries
2. **Dynamic Tables**: Auto-refresh eliminates manual metric calculation
3. **Views**: Pre-computed joins reduce dashboard query complexity
4. **Streams**: Efficient change detection vs full table scans
5. **Warehouse Auto-Suspend**: Cost optimization (suspends after 1 min)

## Scalability

- **Horizontal**: Add more hospitals by inserting rows in HOSPITALS table
- **Vertical**: Add more items/departments without schema changes
- **Temporal**: Partitioning strategy for multi-year data
- **Concurrent Users**: Snowflake handles multiple dashboard users automatically

## Security

- Role-based access control (ACCOUNTADMIN, SYSADMIN)
- API Integration for Git access
- Secrets management for credentials
- Audit trail via ALERT_ACTION_LOG

## Monitoring

- Task execution history via INFORMATION_SCHEMA.TASK_HISTORY
- Dynamic table refresh status
- Warehouse usage and cost tracking
- Alert generation metrics
