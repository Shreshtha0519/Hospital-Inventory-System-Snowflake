# 🚀 Deployment Guide

Complete step-by-step guide to deploy the Hospital Inventory Management System in your Snowflake environment.

---

## Prerequisites

- Snowflake account (Trial, Standard, or Enterprise edition)
- ACCOUNTADMIN or SYSADMIN role access
- Access to Snowflake Worksheets and Streamlit

---

## Phase 0: Environment Setup (5 minutes)

### Step 1: Create Database and Schema
```sql
-- Create main database
CREATE DATABASE IF NOT EXISTS HOSPITAL_INVENTORY_DB
    COMMENT = 'Hospital Inventory Management System';

-- Create schema
CREATE SCHEMA IF NOT EXISTS HOSPITAL_INVENTORY_DB.STOCK_MGMT
    COMMENT = 'Stock management schema';

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS INVENTORY_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    COMMENT = 'Warehouse for inventory operations';

-- Set context
USE DATABASE HOSPITAL_INVENTORY_DB;
USE SCHEMA STOCK_MGMT;
USE WAREHOUSE INVENTORY_WH;
```

### Step 2: Verify Setup
```sql
SELECT CURRENT_DATABASE() AS database_name,
       CURRENT_SCHEMA() AS schema_name,
       CURRENT_WAREHOUSE() AS warehouse_name;
```

**Expected Output:**
- Database: HOSPITAL_INVENTORY_DB
- Schema: STOCK_MGMT
- Warehouse: INVENTORY_WH

---

## Phase 1: Create Master Tables (10 minutes)

### Step 1: Create HOSPITALS Table
```sql
CREATE OR REPLACE TABLE HOSPITALS (
    hospital_id INT PRIMARY KEY,
    hospital_name VARCHAR(200) NOT NULL,
    location VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100),
    hospital_type VARCHAR(50),
    bed_capacity INT,
    established_year INT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample hospital
INSERT INTO HOSPITALS VALUES (
    1, 'City General Hospital', 'Andheri West', 'Mumbai', 
    'Maharashtra', 'Multi-Specialty Teaching Hospital', 500, 1985,
    CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);
```

### Step 2: Create DEPARTMENTS Table
```sql
CREATE OR REPLACE TABLE DEPARTMENTS (
    department_id INT PRIMARY KEY,
    hospital_id INT NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    department_code VARCHAR(20),
    criticality_level VARCHAR(20),
    description VARCHAR(500),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (hospital_id) REFERENCES HOSPITALS(hospital_id)
);

-- Insert 5 departments
-- (Refer to sql/setup_instructions.sql for complete INSERT statements)
```

### Step 3: Create ITEMS_MASTER and SUPPLIERS Tables

Refer to `sql/setup_instructions.sql` for:
- Complete CREATE TABLE statements
- INSERT statements for 40 medical items
- INSERT statements for 6 suppliers

---

## Phase 2: Generate Historical Data (15 minutes)

### Step 1: Create Main Transactional Table
```sql
CREATE OR REPLACE TABLE HOSPITAL_STOCK_DAILY (
    record_id INT AUTOINCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    hospital_id INT NOT NULL,
    department_id INT NOT NULL,
    item_id INT NOT NULL,
    opening_stock INT NOT NULL,
    received INT DEFAULT 0,
    consumed INT DEFAULT 0,
    expired INT DEFAULT 0,
    closing_stock INT NOT NULL,
    expiry_date DATE,
    batch_number VARCHAR(50),
    supplier_id INT,
    lead_time_days INT,
    stock_status VARCHAR(20),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (hospital_id) REFERENCES HOSPITALS(hospital_id),
    FOREIGN KEY (department_id) REFERENCES DEPARTMENTS(department_id),
    FOREIGN KEY (item_id) REFERENCES ITEMS_MASTER(item_id),
    FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id)
);

-- Add clustering
ALTER TABLE HOSPITAL_STOCK_DAILY 
CLUSTER BY (transaction_date, department_id);
```

### Step 2: Generate 90 Days of Data

Use the data generation procedures from your original Phase 2 setup.

**Verification:**
```sql
SELECT 
    COUNT(*) as total_records,
    MIN(transaction_date) as start_date,
    MAX(transaction_date) as end_date,
    COUNT(DISTINCT department_id) as departments,
    COUNT(DISTINCT item_id) as items
FROM HOSPITAL_STOCK_DAILY;
```

**Expected:** ~8,000-10,000 records across 90 days

---

## Phase 3: Create Metrics Layer (20 minutes)

### Step 1: Create Dynamic Table for Stock Metrics
```sql
CREATE OR REPLACE DYNAMIC TABLE STOCK_METRICS
    TARGET_LAG = '1 hour'
    WAREHOUSE = INVENTORY_WH
AS
SELECT 
    -- [Complete SELECT statement from your Phase 3]
    -- Includes: 7-day consumption trends, days remaining, status classification
FROM HOSPITAL_STOCK_DAILY hsd
JOIN DEPARTMENTS d ON hsd.department_id = d.department_id
JOIN ITEMS_MASTER i ON hsd.item_id = i.item_id
LEFT JOIN SUPPLIERS s ON hsd.supplier_id = s.supplier_id;
```

### Step 2: Create Analytical Views

Create 12+ views for dashboard consumption:
- V_LATEST_STOCK_METRICS
- V_ACTIVE_ALERTS
- V_ALERT_SUMMARY
- V_DEPARTMENT_ALERT_SUMMARY
- V_KPI_SUMMARY
- (Refer to your Phase 3 code for complete view definitions)

**Verification:**
```sql
-- Test key views
SELECT * FROM V_LATEST_STOCK_METRICS LIMIT 10;
SELECT * FROM V_KPI_SUMMARY;
```

---

## Phase 4: Set Up Alert System (25 minutes)

### Step 1: Create Alert Tables
```sql
CREATE OR REPLACE TABLE STOCK_ALERTS (
    alert_id INT AUTOINCREMENT PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    alert_severity VARCHAR(20) NOT NULL,
    -- [Complete column definitions from Phase 4]
);

CREATE OR REPLACE TABLE ALERT_ACTION_LOG (
    action_log_id INT AUTOINCREMENT PRIMARY KEY,
    alert_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    -- [Complete column definitions from Phase 4]
    FOREIGN KEY (alert_id) REFERENCES STOCK_ALERTS(alert_id)
);

-- Add clustering
ALTER TABLE STOCK_ALERTS 
CLUSTER BY (alert_severity, TO_DATE(created_at));

ALTER TABLE ALERT_ACTION_LOG 
CLUSTER BY (action_by, TO_DATE(action_timestamp));
```

### Step 2: Create Stream
```sql
CREATE OR REPLACE STREAM HOSPITAL_STOCK_STREAM 
ON TABLE HOSPITAL_STOCK_DAILY
SHOW_INITIAL_ROWS = FALSE;
```

### Step 3: Create Alert Generation Procedure
```sql
CREATE OR REPLACE PROCEDURE GENERATE_STOCK_ALERTS()
RETURNS STRING
LANGUAGE SQL
AS
$$
-- [Complete procedure definition from Phase 4]
$$;
```

### Step 4: Create Scheduled Task
```sql
CREATE OR REPLACE TASK TASK_GENERATE_STOCK_ALERTS
    WAREHOUSE = INVENTORY_WH
    SCHEDULE = '60 MINUTE'
AS
    CALL GENERATE_STOCK_ALERTS();

-- Activate the task
ALTER TASK TASK_GENERATE_STOCK_ALERTS RESUME;
```

### Step 5: Create Alert Management Procedures

Create 4 additional procedures:
- ACKNOWLEDGE_ALERT()
- MARK_ORDER_PLACED()
- RESOLVE_ALERT()
- ACKNOWLEDGE_DEPT_ALERTS()

**Verification:**
```sql
-- Generate initial alerts
CALL GENERATE_STOCK_ALERTS();

-- Check alerts created
SELECT COUNT(*) as total_alerts,
       COUNT(CASE WHEN alert_severity = 'URGENT' THEN 1 END) as urgent_alerts
FROM STOCK_ALERTS;

-- Verify task is running
SHOW TASKS;
SELECT state FROM INFORMATION_SCHEMA.TASKS 
WHERE task_name = 'TASK_GENERATE_STOCK_ALERTS';
```

---

## Phase 5: Deploy Streamlit Dashboard (15 minutes)

### Step 1: Create Streamlit App

1. In Snowflake UI, navigate to **Streamlit**
2. Click **"+ Streamlit App"**
3. **App name:** `Hospital_Inventory_Dashboard`
4. **Warehouse:** `INVENTORY_WH`
5. **App location:** `HOSPITAL_INVENTORY_DB.STOCK_MGMT`
6. Click **"Create"**

### Step 2: Add Dashboard Code

1. Copy the code from `streamlit/hospital_inventory_dashboard.py`
2. Paste into the Streamlit editor
3. Click **"Run"**

### Step 3: Test Dashboard

Navigate through all 3 pages:
- ✅ Overview: KPIs display correctly
- ✅ Heatmap: Color-coded stock status visible
- ✅ Alerts: Active alerts listed with action buttons

---

## Post-Deployment Checklist

### Data Verification
```sql
-- Check all tables have data
SELECT 'HOSPITALS' as table_name, COUNT(*) as row_count FROM HOSPITALS
UNION ALL
SELECT 'DEPARTMENTS', COUNT(*) FROM DEPARTMENTS
UNION ALL
SELECT 'ITEMS_MASTER', COUNT(*) FROM ITEMS_MASTER
UNION ALL
SELECT 'SUPPLIERS', COUNT(*) FROM SUPPLIERS
UNION ALL
SELECT 'HOSPITAL_STOCK_DAILY', COUNT(*) FROM HOSPITAL_STOCK_DAILY
UNION ALL
SELECT 'STOCK_ALERTS', COUNT(*) FROM STOCK_ALERTS;
```

### System Health Check
```sql
-- Check dynamic table refresh
SELECT name, refresh_mode, target_lag, last_refresh_time
FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY('STOCK_METRICS'))
ORDER BY last_refresh_time DESC LIMIT 5;

-- Check task execution
SELECT name, state, schedule, next_scheduled_time
FROM INFORMATION_SCHEMA.TASKS
WHERE task_name = 'TASK_GENERATE_STOCK_ALERTS';

-- Check stream has data capture enabled
SHOW STREAMS;
```

### Dashboard Access
```sql
-- Get Streamlit app URL
SHOW STREAMLIT APPS;
```

---

## Troubleshooting

### Issue: Dynamic Table Not Refreshing

**Solution:**
```sql
-- Manually refresh
ALTER DYNAMIC TABLE STOCK_METRICS REFRESH;

-- Check for errors
SELECT * FROM TABLE(INFORMATION_SCHEMA.DYNAMIC_TABLE_REFRESH_HISTORY('STOCK_METRICS'))
WHERE state = 'FAILED'
ORDER BY refresh_start_time DESC;
```

### Issue: Task Not Running

**Solution:**
```sql
-- Resume suspended task
ALTER TASK TASK_GENERATE_STOCK_ALERTS RESUME;

-- Check task history
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE name = 'TASK_GENERATE_STOCK_ALERTS'
ORDER BY scheduled_time DESC LIMIT 10;
```

### Issue: Streamlit App Errors

**Solution:**
- Check warehouse is running: `ALTER WAREHOUSE INVENTORY_WH RESUME;`
- Verify database context in app code
- Check view permissions

---

## Maintenance

### Daily Tasks
- Monitor alert generation (should run hourly automatically)
- Review critical alerts in dashboard

### Weekly Tasks
- Check warehouse usage and costs
- Review resolved vs pending alerts ratio
- Analyze stock-out trends

### Monthly Tasks
- Archive old alerts (>90 days)
- Review and update item reorder levels
- Analyze system performance metrics

---

## Cost Optimization
```sql
-- Set warehouse to auto-suspend aggressively
ALTER WAREHOUSE INVENTORY_WH SET AUTO_SUSPEND = 60;

-- Suspend manually when not in use
ALTER WAREHOUSE INVENTORY_WH SUSPEND;

-- Monitor credit usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name = 'INVENTORY_WH'
AND start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY start_time DESC;
```

**Estimated Monthly Cost (X-Small warehouse):**
- Development: $20-50
- Production: $100-200

---

## Scaling Guidelines

### Adding More Hospitals
```sql
-- Simply insert new hospital
INSERT INTO HOSPITALS VALUES (...);

-- System automatically tracks across all hospitals
```

### Adding More Items
```sql
-- Add new items to master table
INSERT INTO ITEMS_MASTER VALUES (...);

-- Start tracking usage immediately
```

### Increasing Data Volume

- Upgrade warehouse size: `ALTER WAREHOUSE ... SET WAREHOUSE_SIZE = 'SMALL';`
- Adjust dynamic table refresh: `ALTER DYNAMIC TABLE ... SET TARGET_LAG = '30 MINUTE';`
- Add table clustering on high-cardinality columns

---

## Support & Resources

- **Snowflake Documentation**: https://docs.snowflake.com
- **Repository Issues**: https://github.com/Shreshtha0519/Hospital-Inventory-System-Snowflake/issues
- **Streamlit Docs**: https://docs.streamlit.io

---

**Deployment Time:** ~90 minutes total
**Skill Level Required:** Intermediate SQL, Basic Python
**Support:** Community-driven (raise GitHub issues)

---

**Last Updated**: 2026-01-04
```

5. **Commit message:** `Add complete deployment guide`

6. **Click "Commit new file"**

---

## ✅ **Final Repository Structure**

Your repository should now have:
```
```
Hospital-Inventory-System-Snowflake/
├── README.md
├── sql/
│   └── setup_instructions.sql
├── streamlit/
│   └── hospital_inventory_dashboard.py
└── docs/
    ├── ARCHITECTURE.md
    └── DEPLOYMENT.md
