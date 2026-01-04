# 🏥 Hospital Inventory Management System

**AI for Good - Stock-Out Prevention Prototype**

## 📋 Overview

An intelligent hospital inventory management system built on Snowflake that predicts stock-outs

## 🎯 Key Features

- ✅ Real-time inventory tracking across 5 hospital departments
- ✅ Predictive alerts 3-7 days before stock-outs  
- ✅ Automated alert generation (runs hourly)
- ✅ Interactive Streamlit dashboard with heatmaps
- ✅ Priority-based reorder recommendations
- ✅ Expiry risk tracking to minimize waste
- ✅ Complete audit trail of all actions

## 🏗️ Architecture

### Data Layer
- **7 Core Tables**: Hospitals
- **1 Dynamic Table**: Auto-refreshing metrics with 7-day consumption trends
- **12+ Views**: Pre-computed analytics for dashboard
- **Sample Data**: 90 days of realistic hospital stock data (~8

### Intelligence Layer
- **Stream**: Captures stock data changes
- **Task**: Scheduled alert generation (every 60 minutes)
- **Stored Procedures**: Alert management and action logging

### Presentation Layer
- **Streamlit Dashboard**: 3-page interactive UI
  - KPI Overview
  - Stock Heatmap  
  - Active Alerts Management

## 📊 Tech Stack

- **Data Platform**: Snowflake
- **Dashboard**: Streamlit (Python)
- **Automation**: Snowflake Tasks
- **Data Volume**: 40 items × 5 departments × 90 days

## 📈 Sample Metrics

Based on 90-day simulation:
- **Total Alerts Generated**: ~45
- **Critical Items**: 8-12 (requiring immediate action)
- **Expiry Risks**: 3-5 items
- **Total Inventory Value**: ₹300
- **Potential Waste Prevented**: ₹70

## 🎯 AI for Good Impact

### Problem Solved
- Prevents life-threatening medicine shortages in ICU and Emergency departments
- Reduces waste from expired medicines (₹70
- Optimizes procurement costs through predictive ordering

### Scalability
- Easily extends to multiple hospitals
- Adaptable to food banks
- Framework supports 100+ items across 20+ departments

## 👥 Author

Shreshtha Kadam
AI for Good - Stock-Out Prevention Challenge

## 📄 License

MIT License - Educational purposes# 🏥 Hospital Inventory Management System

**AI for Good - Stock-Out Prevention Prototype**

## 📋 Overview

An intelligent hospital inventory management system built on Snowflake that predicts stock-outs

## 🎯 Key Features

- ✅ Real-time inventory tracking across 5 hospital departments
- ✅ Predictive alerts 3-7 days before stock-outs  
- ✅ Automated alert generation (runs hourly)
- ✅ Interactive Streamlit dashboard with heatmaps
- ✅ Priority-based reorder recommendations
- ✅ Expiry risk tracking to minimize waste
- ✅ Complete audit trail of all actions

## 🏗️ Architecture

### Data Layer
- **7 Core Tables**: Hospitals
- **1 Dynamic Table**: Auto-refreshing metrics with 7-day consumption trends
- **12+ Views**: Pre-computed analytics for dashboard
- **Sample Data**: 90 days of realistic hospital stock data (~8

### Intelligence Layer
- **Stream**: Captures stock data changes
- **Task**: Scheduled alert generation (every 60 minutes)
- **Stored Procedures**: Alert management and action logging

### Presentation Layer
- **Streamlit Dashboard**: 3-page interactive UI
  - KPI Overview
  - Stock Heatmap  
  - Active Alerts Management

## 📊 Tech Stack

- **Data Platform**: Snowflake
- **Dashboard**: Streamlit (Python)
- **Automation**: Snowflake Tasks
- **Data Volume**: 40 items × 5 departments × 90 days

## 📈 Sample Metrics

Based on 90-day simulation:
- **Total Alerts Generated**: ~45
- **Critical Items**: 8-12 (requiring immediate action)
- **Expiry Risks**: 3-5 items
- **Total Inventory Value**: ₹300
- **Potential Waste Prevented**: ₹70

## 🎯 AI for Good Impact

### Problem Solved
- Prevents life-threatening medicine shortages in ICU and Emergency departments
- Reduces waste from expired medicines (₹70
- Optimizes procurement costs through predictive ordering

### Scalability
- Easily extends to multiple hospitals
- Adaptable to food banks
- Framework supports 100+ items across 20+ departments

## 👥 Author

Shreshtha Kadam
AI for Good - Stock-Out Prevention Challenge

## 📄 License

MIT License - Educational purposes
