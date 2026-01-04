-- =====================================================
-- HOSPITAL INVENTORY MANAGEMENT SYSTEM
-- Complete Database Setup Script
-- =====================================================

-- PHASE 0: ENVIRONMENT SETUP
CREATE DATABASE IF NOT EXISTS HOSPITAL_INVENTORY_DB;
CREATE SCHEMA IF NOT EXISTS HOSPITAL_INVENTORY_DB.STOCK_MGMT;
CREATE WAREHOUSE IF NOT EXISTS INVENTORY_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE;

USE DATABASE HOSPITAL_INVENTORY_DB;
USE SCHEMA STOCK_MGMT;
USE WAREHOUSE INVENTORY_WH;

-- =====================================================
-- PHASE 1: MASTER TABLES
-- =====================================================

-- Note: Run these CREATE TABLE statements from your Snowflake worksheet
-- to get complete DDL

-- Tables to create in order:
-- 1. HOSPITALS
-- 2. DEPARTMENTS  
-- 3. ITEMS_MASTER
-- 4. SUPPLIERS
-- 5. HOSPITAL_STOCK_DAILY
-- 6. STOCK_ALERTS
-- 7. ALERT_ACTION_LOG

-- =====================================================
-- PHASE 2: DYNAMIC TABLE
-- =====================================================

-- Table: STOCK_METRICS (Dynamic Table)
-- Run: SELECT GET_DDL('TABLE'

-- =====================================================
-- PHASE 3: VIEWS
-- =====================================================

-- All views starting with V_
-- Run this to get list:
-- SELECT table_name FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = 'STOCK_MGMT';

-- =====================================================
-- PHASE 4: STREAM
-- =====================================================

-- Stream: HOSPITAL_STOCK_STREAM
-- Run: SELECT GET_DDL('STREAM'

-- =====================================================
-- PHASE 5: STORED PROCEDURES
-- =====================================================

-- Run: SHOW PROCEDURES IN SCHEMA STOCK_MGMT;
-- Then get DDL for each procedure

-- =====================================================
-- PHASE 6: TASK
-- =====================================================

-- Task: TASK_GENERATE_STOCK_ALERTS
-- Run: SELECT GET_DDL('TASK'

-- =====================================================
-- SETUP INSTRUCTIONS
-- =====================================================

-- 1. Create all tables in the order listed above
-- 2. Insert master data (hospitals
-- 3. Run data generation procedures
-- 4. Create dynamic table for metrics
-- 5. Create all views
-- 6. Set up stream and task for automation
-- 7. Deploy Streamlit dashboard

-- For complete DDL of any object
-- SELECT GET_DDL('object_type'

-- =====================================================
-- END OF SETUP SCRIPT
-- =====================================================
