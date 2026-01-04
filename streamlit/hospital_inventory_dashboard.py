# =====================================================
# HOSPITAL INVENTORY MANAGEMENT DASHBOARD
# =====================================================

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from datetime import datetime

# Get Snowflake session
session = get_active_session()

# Page configuration
st.set_page_config(
    page_title="Hospital Inventory Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏥 Hospital Inventory Management System</p>', unsafe_allow_html=True)
st.markdown("**AI for Good - Stock-Out Prevention Dashboard**")
st.markdown("---")
# System Health Indicator
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    pass  # Keep empty for spacing

with col2:
    # Check if task is running
    task_status_query = """
    SELECT state 
    FROM INFORMATION_SCHEMA.TASKS 
    WHERE task_name = 'TASK_GENERATE_STOCK_ALERTS' 
    AND task_schema = 'STOCK_MGMT'
    """
    try:
        task_status = session.sql(task_status_query).to_pandas()
        if len(task_status) > 0 and task_status['STATE'][0] == 'started':
            st.success("✅ Automation: Active")
        else:
            st.warning("⚠️ Automation: Suspended")
    except:
        st.info("ℹ️ Automation: Unknown")

with col3:
    # Last alert generation
    last_alert_query = """
    SELECT MAX(created_at) as last_alert 
    FROM STOCK_ALERTS
    """
    try:
        last_alert = session.sql(last_alert_query).to_pandas()
        if len(last_alert) > 0 and last_alert['LAST_ALERT'][0]:
            hours_ago = (datetime.now() - pd.to_datetime(last_alert['LAST_ALERT'][0])).total_seconds() / 3600
            if hours_ago < 2:
                st.success(f"🔄 Last Alert: {hours_ago:.0f}h ago")
            else:
                st.info(f"🔄 Last Alert: {hours_ago:.0f}h ago")
    except:
        st.info("🔄 Last Alert: N/A")

st.markdown("---")

# Sidebar
st.sidebar.title("📋 Navigation")
st.sidebar.markdown("### Dashboard Sections")
page = st.sidebar.radio("Go to:", ["📊 Overview", "🗺️ Stock Heatmap", "🚨 Active Alerts"])
# Demo Mode Toggle
st.sidebar.markdown("### 🎬 Display Mode")
demo_mode = st.sidebar.checkbox(
    "Demo Mode",
    value=False,
    help="Enable demo mode for presentations (hides real timestamps)"
)

if demo_mode:
    st.sidebar.info("📹 Demo mode active - optimized for presentations")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Dashboard Sections")
try:
    # =====================================================
    # FETCH KPI DATA
    # =====================================================
    
    kpi_query = """
    SELECT 
        total_active_alerts,
        urgent_count,
        high_count,
        medium_count,
        low_count,
        stockout_alerts,
        stockout_risk_alerts,
        expiry_risk_alerts,
        total_reorder_cost_INR,
        total_waste_risk_INR
    FROM V_ALERT_SUMMARY
    """
    
    kpi_df = session.sql(kpi_query).to_pandas()
    
    stock_query = """
    SELECT 
        COUNT(DISTINCT item_id) as total_items,
        COUNT(CASE WHEN stock_status = 'STOCKOUT' THEN 1 END) as stockout_items,
        COUNT(CASE WHEN stock_status = 'CRITICAL' THEN 1 END) as critical_items,
        COUNT(CASE WHEN stock_status = 'LOW' THEN 1 END) as low_items,
        COUNT(CASE WHEN stock_status = 'OK' THEN 1 END) as ok_items,
        ROUND(SUM(inventory_value_INR), 2) as total_inventory_value
    FROM V_LATEST_STOCK_METRICS
    """
    
    stock_df = session.sql(stock_query).to_pandas()
    
    # =====================================================
    # KPI CARDS (Always visible at top)
    # =====================================================
    
    st.subheader("📊 Key Performance Indicators")
    
    # Row 1: Alert Summary
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🚨 Total Active Alerts", int(kpi_df['TOTAL_ACTIVE_ALERTS'][0]))
    
    with col2:
        urgent_count = int(kpi_df['URGENT_COUNT'][0])
        st.metric("🔴 URGENT Alerts", urgent_count, 
                 delta=f"{urgent_count} need action" if urgent_count > 0 else "None",
                 delta_color="inverse")
    
    with col3:
        st.metric("🟠 HIGH Priority", int(kpi_df['HIGH_COUNT'][0]))
    
    with col4:
        st.metric("🟡 MEDIUM Priority", int(kpi_df['MEDIUM_COUNT'][0]))
    
    with col5:
        st.metric("🟢 LOW Priority", int(kpi_df['LOW_COUNT'][0]))
    
    st.markdown("---")
    
    # =====================================================
    # PAGE ROUTING
    # =====================================================
    # Welcome Banner (Show only on first load or when on Overview)
    if page == "📊 Overview":
        st.markdown("---")
        
        # Quick Action Cards
        st.subheader("⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚨 View Critical Alerts", use_container_width=True):
                st.session_state['page'] = "🚨 Active Alerts"
                st.rerun()
        
        with col2:
            if st.button("🗺️ View Stock Heatmap", use_container_width=True):
                st.session_state['page'] = "🗺️ Stock Heatmap"
                st.rerun()
        
        with col3:
            # Generate purchase order list
            po_query = """
            SELECT 
                department_name as "Department",
                item_name as "Item",
                suggested_reorder_qty as "Order Quantity",
                supplier_name as "Supplier",
                ROUND(suggested_reorder_cost, 2) as "Cost (INR)"
            FROM V_ACTIVE_ALERTS
            WHERE alert_type IN ('STOCKOUT', 'STOCKOUT_RISK')
            ORDER BY priority_score DESC
            """
            po_df = session.sql(po_query).to_pandas()
            po_csv = po_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📋 Generate Purchase Order List",
                data=po_csv,
                file_name=f'purchase_order_list_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True,
                help="Download prioritized list of items needing reorder"
            )
        
        with col4:
            if st.button("📊 Run Alert Generation", use_container_width=True):
                with st.spinner("Generating new alerts..."):
                    try:
                        session.sql("CALL GENERATE_STOCK_ALERTS()").collect()
                        st.success("✅ Alerts regenerated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("---")
    
    if page == "📊 Overview":
        # Row 2: Alert Types
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⚫ Complete Stockouts", int(kpi_df['STOCKOUT_ALERTS'][0]))
        
        with col2:
            st.metric("⚠️ Stockout Risk", int(kpi_df['STOCKOUT_RISK_ALERTS'][0]))
        
        with col3:
            st.metric("📅 Expiry Risk", int(kpi_df['EXPIRY_RISK_ALERTS'][0]))
        
        with col4:
            total_items = int(stock_df['TOTAL_ITEMS'][0])
            ok_items = int(stock_df['OK_ITEMS'][0])
            healthy_pct = round((ok_items / total_items * 100), 1) if total_items > 0 else 0
            st.metric("✅ Healthy Items", f"{ok_items} ({healthy_pct}%)")
        
        st.markdown("---")
        
        # Row 3: Financial Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_value = float(stock_df['TOTAL_INVENTORY_VALUE'][0])
            st.metric("💰 Total Inventory Value", f"₹{total_value:,.2f}")
        
        with col2:
            reorder_cost = float(kpi_df['TOTAL_REORDER_COST_INR'][0]) if kpi_df['TOTAL_REORDER_COST_INR'][0] else 0
            st.metric("📦 Estimated Reorder Cost", f"₹{reorder_cost:,.2f}")
        
        with col3:
            waste_risk = float(kpi_df['TOTAL_WASTE_RISK_INR'][0]) if kpi_df['TOTAL_WASTE_RISK_INR'][0] else 0
            st.metric("⚠️ Potential Waste Value", f"₹{waste_risk:,.2f}",
                     delta="Risk from expiry" if waste_risk > 0 else "None",
                     delta_color="inverse")
        
        st.markdown("---")
        
        # Department Summary
        st.subheader("🏢 Department Summary")
        
        dept_query = """
        SELECT 
            department_name as "Department",
            total_alerts as "Total Alerts",
            urgent_alerts as "🔴 Urgent",
            high_alerts as "🟠 High",
            stockouts as "⚫ Stockouts",
            expiry_risks as "📅 Expiry Risk",
            CONCAT('₹', TO_CHAR(est_reorder_cost_INR, '999,999.00')) as "Est. Reorder Cost"
        FROM V_DEPARTMENT_ALERT_SUMMARY
        ORDER BY urgent_alerts DESC, total_alerts DESC
        """
        
        dept_df = session.sql(dept_query).to_pandas()
        st.dataframe(dept_df, use_container_width=True, hide_index=True)
        # Export Options
        st.markdown("---")
        st.subheader("📥 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export Department Summary
            dept_csv = dept_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Department Summary (CSV)",
                data=dept_csv,
                file_name=f'department_summary_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download department alert summary"
            )
        
        with col2:
            # Export All Alerts
            all_alerts_query = """
            SELECT 
                alert_id,
                alert_type,
                alert_severity,
                department_name,
                item_name,
                current_stock,
                days_of_stock_remaining,
                suggested_action,
                suggested_reorder_qty,
                suggested_reorder_cost,
                created_at
            FROM V_ACTIVE_ALERTS
            ORDER BY priority_score DESC
            """
            all_alerts_df = session.sql(all_alerts_query).to_pandas()
            all_alerts_csv = all_alerts_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download All Active Alerts (CSV)",
                data=all_alerts_csv,
                file_name=f'active_alerts_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download complete list of active alerts"
            )
        
        with col3:
            # Export Current Stock Status
            stock_export_query = """
            SELECT 
                department_name,
                item_name,
                category,
                item_criticality,
                current_stock,
                reorder_level,
                days_of_stock_remaining,
                stock_status,
                expiry_date
            FROM V_LATEST_STOCK_METRICS
            ORDER BY department_name, item_criticality DESC
            """
            stock_export_df = session.sql(stock_export_query).to_pandas()
            stock_csv = stock_export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Current Stock Status (CSV)",
                data=stock_csv,
                file_name=f'current_stock_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download complete current stock status"
            )
        
        # Quick Stats
        st.markdown("---")
        st.subheader("📊 Quick Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📋 Total Data Points",
                f"{len(stock_export_df):,}",
                help="Total number of department-item combinations"
            )
        
        with col2:
            avg_days = stock_export_df[stock_export_df['DAYS_OF_STOCK_REMAINING'] < 999]['DAYS_OF_STOCK_REMAINING'].mean()
            st.metric(
                "⏱️ Avg Days of Stock",
                f"{avg_days:.1f} days",
                help="Average days of stock remaining across all items"
            )
        
        with col3:
            problematic = len(stock_export_df[stock_export_df['STOCK_STATUS'].isin(['STOCKOUT', 'CRITICAL', 'LOW'])])
            st.metric(
                "⚠️ Items Needing Attention",
                problematic,
                help="Items with stockout, critical, or low status"
            )
        
        with col4:
            expiring_soon = len(stock_export_df[
                (stock_export_df['EXPIRY_DATE'].notna()) & 
                (pd.to_datetime(stock_export_df['EXPIRY_DATE']) <= pd.Timestamp.now() + pd.Timedelta(days=30))
            ])
            st.metric(
                "📅 Expiring in 30 Days",
                expiring_soon,
                help="Items expiring within the next 30 days"
            )
            # Stock Status Distribution Chart
        st.markdown("---")
        st.subheader("📊 Stock Status Distribution")
        
        # Get status distribution
        status_dist_query = """
        SELECT 
            stock_status,
            COUNT(*) as item_count
        FROM V_LATEST_STOCK_METRICS
        GROUP BY stock_status
        ORDER BY 
            CASE stock_status
                WHEN 'STOCKOUT' THEN 1
                WHEN 'CRITICAL' THEN 2
                WHEN 'LOW' THEN 3
                WHEN 'OK' THEN 4
                WHEN 'HIGH' THEN 5
                WHEN 'EXCESS' THEN 6
            END
        """
        
        status_dist_df = session.sql(status_dist_query).to_pandas()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Bar chart using st.bar_chart
            st.bar_chart(
                status_dist_df.set_index('STOCK_STATUS'),
                height=300,
                use_container_width=True
            )
        
        with col2:
            st.markdown("### Status Legend")
            for idx, row in status_dist_df.iterrows():
                status = row['STOCK_STATUS']
                count = row['ITEM_COUNT']
                
                if status == 'STOCKOUT':
                    st.markdown(f"🔴 **{status}**: {count} items")
                elif status == 'CRITICAL':
                    st.markdown(f"🟠 **{status}**: {count} items")
                elif status == 'LOW':
                    st.markdown(f"🟡 **{status}**: {count} items")
                elif status == 'OK':
                    st.markdown(f"🟢 **{status}**: {count} items")
                else:
                    st.markdown(f"⚪ **{status}**: {count} items")
        
        # Alert Trend (Last 24 hours simulation)
        st.markdown("---")
        st.subheader("📈 Alert Activity")
        
        alert_activity_query = """
        SELECT 
            DATE_TRUNC('hour', created_at) as hour,
            alert_severity,
            COUNT(*) as alert_count
        FROM STOCK_ALERTS
        WHERE created_at >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
        GROUP BY DATE_TRUNC('hour', created_at), alert_severity
        ORDER BY hour DESC
        LIMIT 50
        """
        
        try:
            alert_activity_df = session.sql(alert_activity_query).to_pandas()
            
            if len(alert_activity_df) > 0:
                # Pivot for better visualization
                alert_pivot = alert_activity_df.pivot_table(
                    index='HOUR',
                    columns='ALERT_SEVERITY',
                    values='ALERT_COUNT',
                    fill_value=0
                )
                
                st.line_chart(alert_pivot, height=300)
                st.caption("Alert generation activity over the last 24 hours")
            else:
                st.info("No alert activity in the last 24 hours")
        except:
            st.info("Alert activity tracking - data will populate over time")
    # =====================================================
    # STOCK HEATMAP PAGE
    # =====================================================
    
    elif page == "🗺️ Stock Heatmap":
        st.subheader("🗺️ Department × Item Stock Status Heatmap")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get departments
            dept_filter_query = "SELECT DISTINCT department_name FROM V_LATEST_STOCK_METRICS ORDER BY department_name"
            dept_options = session.sql(dept_filter_query).to_pandas()['DEPARTMENT_NAME'].tolist()
            selected_depts = st.multiselect(
                "Filter by Department",
                options=dept_options,
                default=dept_options,
                help="Select departments to display"
            )
        
        with col2:
            # Get categories
            cat_filter_query = "SELECT DISTINCT category FROM V_LATEST_STOCK_METRICS ORDER BY category"
            cat_options = session.sql(cat_filter_query).to_pandas()['CATEGORY'].tolist()
            selected_cats = st.multiselect(
                "Filter by Category",
                options=cat_options,
                default=cat_options,
                help="Select item categories to display"
            )
        
        with col3:
            # Get actual status values from data
            status_query = "SELECT DISTINCT stock_status FROM V_LATEST_STOCK_METRICS WHERE stock_status IS NOT NULL ORDER BY stock_status"
            actual_statuses = session.sql(status_query).to_pandas()['STOCK_STATUS'].tolist()
            
            status_options = ['All'] + actual_statuses
            status_filter = st.selectbox(
                "Filter by Status",
                options=status_options,
                help="Filter items by stock status"
            )
        
        st.markdown("---")

        # Quick filter buttons
        st.markdown("**🔍 Quick Filters:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔴 Show Critical Only (≤3 days)", use_container_width=True):
                status_filter = 'All'  # Override to show based on days
                quick_filter = 'critical'
        
        with col2:
            if st.button("⚫ Show Stockouts Only", use_container_width=True):
                quick_filter = 'stockout'
        
        with col3:
            if st.button("⚠️ Show All Problems", use_container_width=True):
                quick_filter = 'problems'
        
        with col4:
            if st.button("🟢 Show Healthy Only", use_container_width=True):
                quick_filter = 'healthy'
        
        # Fetch heatmap data
        heatmap_base_query = """
        SELECT 
            department_name as "Department",
            item_name as "Item",
            category as "Category",
            item_criticality as "Criticality",
            current_stock as "Current Stock",
            reorder_level as "Reorder Level",
            ROUND(days_of_stock_remaining, 1) as "Days Remaining",
            stock_status as "Status",
            CASE 
                WHEN stock_status = 'STOCKOUT' THEN '🔴'
                WHEN days_of_stock_remaining <= 2 THEN '🔴'
                WHEN days_of_stock_remaining <= 5 THEN '🟠'
                WHEN days_of_stock_remaining <= 7 THEN '🟡'
                WHEN days_of_stock_remaining <= 14 THEN '🟢'
                ELSE '🟢'
            END as "Health"
        FROM V_LATEST_STOCK_METRICS
        WHERE 1=1
        """
        
        # Apply filters
        if selected_depts:
            dept_list = "', '".join(selected_depts)
            heatmap_base_query += f" AND department_name IN ('{dept_list}')"
        
        if selected_cats:
            cat_list = "', '".join(selected_cats)
            heatmap_base_query += f" AND category IN ('{cat_list}')"
        
        if status_filter != 'All':
            if status_filter == 'CRITICAL':
                # If someone selects CRITICAL, show items with ≤3 days OR status = CRITICAL
                heatmap_base_query += f" AND (stock_status = 'CRITICAL' OR days_of_stock_remaining <= 3)"
            else:
                heatmap_base_query += f" AND stock_status = '{status_filter}'"
        
        heatmap_base_query += " ORDER BY department_name, item_criticality DESC, days_of_stock_remaining ASC"
        
        heatmap_df = session.sql(heatmap_base_query).to_pandas()
        
        if len(heatmap_df) > 0:
            
            # Color legend
            st.markdown("### 📊 Color Legend")
            legend_cols = st.columns(5)
            
            with legend_cols[0]:
                st.markdown("🔴 **Critical** (≤2 days or Stockout)")
            with legend_cols[1]:
                st.markdown("🟠 **Low** (3-5 days)")
            with legend_cols[2]:
                st.markdown("🟡 **Watch** (6-7 days)")
            with legend_cols[3]:
                st.markdown("🟢 **Good** (8-14 days)")
            with legend_cols[4]:
                st.markdown("🟢 **Excellent** (>14 days)")
            
            st.markdown("---")
            
            # Display as styled dataframe
            st.subheader("📋 Stock Status by Department & Item")
            
            # Style function
            def highlight_status(row):
                if row['Status'] == 'STOCKOUT':
                    return ['background-color: #8B0000; color: white'] * len(row)
                elif row['Days Remaining'] <= 2:
                    return ['background-color: #DC143C; color: white'] * len(row)
                elif row['Days Remaining'] <= 5:
                    return ['background-color: #FFA500; color: black'] * len(row)
                elif row['Days Remaining'] <= 7:
                    return ['background-color: #FFD700; color: black'] * len(row)
                elif row['Days Remaining'] <= 14:
                    return ['background-color: #90EE90; color: black'] * len(row)
                else:
                    return ['background-color: #228B22; color: white'] * len(row)
            
            # Display styled dataframe
            st.dataframe(
                heatmap_df.style.apply(highlight_status, axis=1),
                use_container_width=True,
                height=600,
                hide_index=True
            )
            
            # Summary stats
            st.markdown("---")
            st.subheader("📈 Heatmap Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Items Displayed", len(heatmap_df))
            with col2:
                critical_count = len(heatmap_df[heatmap_df['Days Remaining'] <= 3])
                st.metric("Critical Items (≤3 days)", critical_count)
            with col3:
                stockouts = len(heatmap_df[heatmap_df['Status'] == 'STOCKOUT'])
                st.metric("Stockouts", stockouts)
            with col4:
                healthy = len(heatmap_df[heatmap_df['Days Remaining'] > 14])
                st.metric("Healthy Items (>14 days)", healthy)
            
            # Export option
            st.markdown("---")
            st.download_button(
                label="📥 Download Heatmap Data as CSV",
                data=heatmap_df.to_csv(index=False).encode('utf-8'),
                file_name='hospital_stock_heatmap.csv',
                mime='text/csv',
                help="Download the current heatmap data as CSV file"
            )
            
        else:
            st.info("No data matches the selected filters. Please adjust your filters.")
    
    # =====================================================
    # ALERTS PAGE
    # =====================================================
    
    elif page == "🚨 Active Alerts":
        st.subheader("🚨 Active Alerts Management")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity",
                options=['All', 'URGENT', 'HIGH', 'MEDIUM', 'LOW'],
                help="Filter alerts by severity level"
            )
        
        with col2:
            alert_type_filter = st.selectbox(
                "Filter by Type",
                options=['All', 'STOCKOUT', 'STOCKOUT_RISK', 'EXPIRY_RISK', 'OVERSTOCK'],
                help="Filter alerts by type"
            )
        
        with col3:
            dept_alert_query = "SELECT DISTINCT department_name FROM V_ACTIVE_ALERTS ORDER BY department_name"
            dept_alert_options = ['All'] + session.sql(dept_alert_query).to_pandas()['DEPARTMENT_NAME'].tolist()
            dept_alert_filter = st.selectbox(
                "Filter by Department",
                options=dept_alert_options,
                help="Filter alerts by department"
            )
        
        st.markdown("---")
        
        # Fetch active alerts
        alerts_base_query = """
        SELECT 
            alert_id,
            alert_type,
            alert_severity,
            department_name,
            item_name,
            category,
            criticality,
            current_stock,
            reorder_level,
            ROUND(days_of_stock_remaining, 1) as days_remaining,
            suggested_action,
            suggested_reorder_qty,
            ROUND(suggested_reorder_cost, 2) as reorder_cost,
            supplier_name,
            lead_time_days,
            priority_score,
            expiry_date,
            days_until_expiry,
            ROUND(potential_waste_value, 2) as waste_value,
            hours_since_created
        FROM V_ACTIVE_ALERTS
        WHERE 1=1
        """
        
        # Apply filters
        if severity_filter != 'All':
            alerts_base_query += f" AND alert_severity = '{severity_filter}'"
        
        if alert_type_filter != 'All':
            alerts_base_query += f" AND alert_type = '{alert_type_filter}'"
        
        if dept_alert_filter != 'All':
            alerts_base_query += f" AND department_name = '{dept_alert_filter}'"
        
        alerts_base_query += " ORDER BY priority_score DESC, hours_since_created ASC LIMIT 50"
        
        alerts_df = session.sql(alerts_base_query).to_pandas()
        
        if len(alerts_df) > 0:
            st.info(f"📋 Showing {len(alerts_df)} active alerts (Top 50 by priority)")
            
            # Display alerts as expandable cards
            for idx, row in alerts_df.iterrows():
                
                # Severity emoji and color
                if row['ALERT_SEVERITY'] == 'URGENT':
                    severity_color = "🔴"
                    card_class = "alert-urgent"
                elif row['ALERT_SEVERITY'] == 'HIGH':
                    severity_color = "🟠"
                    card_class = "alert-high"
                elif row['ALERT_SEVERITY'] == 'MEDIUM':
                    severity_color = "🟡"
                    card_class = ""
                else:
                    severity_color = "🟢"
                    card_class = ""
                
                # Alert type emoji
                if row['ALERT_TYPE'] == 'STOCKOUT':
                    type_emoji = "⚫"
                elif row['ALERT_TYPE'] == 'STOCKOUT_RISK':
                    type_emoji = "⚠️"
                elif row['ALERT_TYPE'] == 'EXPIRY_RISK':
                    type_emoji = "📅"
                else:
                    type_emoji = "📦"
                
                # Create expander for each alert
                with st.expander(
                    f"{severity_color} {type_emoji} **{row['DEPARTMENT_NAME']}** - {row['ITEM_NAME']} "
                    f"({row['ALERT_SEVERITY']}) - Priority: {row['PRIORITY_SCORE']}"
                ):
                    # Alert details
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📍 Location & Item**")
                        st.write(f"**Department:** {row['DEPARTMENT_NAME']}")
                        st.write(f"**Item:** {row['ITEM_NAME']}")
                        st.write(f"**Category:** {row['CATEGORY']}")
                        st.write(f"**Criticality:** {row['CRITICALITY']}")
                    
                    with col2:
                        st.markdown("**📊 Stock Status**")
                        st.write(f"**Current Stock:** {row['CURRENT_STOCK']}")
                        st.write(f"**Reorder Level:** {row['REORDER_LEVEL']}")
                        st.write(f"**Days Remaining:** {row['DAYS_REMAINING']}")
                        if row['EXPIRY_DATE']:
                            st.write(f"**Expiry Date:** {row['EXPIRY_DATE']}")
                            st.write(f"**Days Until Expiry:** {row['DAYS_UNTIL_EXPIRY']}")
                    
                    with col3:
                        st.markdown("**💰 Reorder Info**")
                        st.write(f"**Suggested Qty:** {row['SUGGESTED_REORDER_QTY']}")
                        st.write(f"**Est. Cost:** ₹{row['REORDER_COST']:,.2f}")
                        st.write(f"**Supplier:** {row['SUPPLIER_NAME']}")
                        st.write(f"**Lead Time:** {row['LEAD_TIME_DAYS']} days")
                        if row['WASTE_VALUE'] and row['WASTE_VALUE'] > 0:
                            st.write(f"**⚠️ Waste Risk:** ₹{row['WASTE_VALUE']:,.2f}")
                    
                    # Suggested action
                    st.markdown("---")
                    st.markdown("**📋 Recommended Action:**")
                    st.info(row['SUGGESTED_ACTION'])
                    
                    # Action buttons
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"✅ Acknowledge", key=f"ack_{row['ALERT_ID']}"):
                            try:
                                # Call procedure to acknowledge alert
                                ack_query = f"""
                                CALL ACKNOWLEDGE_ALERT(
                                    {row['ALERT_ID']},
                                    'Dashboard User',
                                    'Acknowledged via Streamlit Dashboard'
                                )
                                """
                                session.sql(ack_query).collect()
                                st.success(f"✅ Alert {row['ALERT_ID']} acknowledged!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col2:
                        if st.button(f"📦 Mark as Ordered", key=f"order_{row['ALERT_ID']}"):
                            with st.form(key=f"order_form_{row['ALERT_ID']}"):
                                order_ref = st.text_input("Order Reference", value=f"PO-{row['ALERT_ID']}")
                                order_qty = st.number_input("Order Quantity", value=int(row['SUGGESTED_REORDER_QTY']))
                                expected_date = st.date_input("Expected Delivery")
                                
                                submitted = st.form_submit_button("Submit Order")
                                if submitted:
                                    try:
                                        order_query = f"""
                                        CALL MARK_ORDER_PLACED(
                                            {row['ALERT_ID']},
                                            'Dashboard User',
                                            '{order_ref}',
                                            {order_qty},
                                            {row['REORDER_COST']},
                                            (SELECT supplier_id FROM STOCK_ALERTS WHERE alert_id = {row['ALERT_ID']}),
                                            '{expected_date}'
                                        )
                                        """
                                        session.sql(order_query).collect()
                                        st.success(f"✅ Order {order_ref} placed!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {str(e)}")
                    
                    with col3:
                        if st.button(f"✔️ Resolve", key=f"resolve_{row['ALERT_ID']}"):
                            try:
                                resolve_query = f"""
                                CALL RESOLVE_ALERT(
                                    {row['ALERT_ID']},
                                    'Dashboard User',
                                    'Resolved via Streamlit Dashboard - Issue addressed'
                                )
                                """
                                session.sql(resolve_query).collect()
                                st.success(f"✅ Alert {row['ALERT_ID']} resolved!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col4:
                        # Export individual alert
                        alert_data = pd.DataFrame([row])
                        csv = alert_data.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Export",
                            data=csv,
                            file_name=f"alert_{row['ALERT_ID']}.csv",
                            mime="text/csv",
                            key=f"export_{row['ALERT_ID']}"
                        )
            
            # Bulk export
            st.markdown("---")
            st.subheader("📥 Bulk Export")
            col1, col2 = st.columns(2)
            
            with col1:
                csv_all = alerts_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download All Alerts as CSV",
                    data=csv_all,
                    file_name='active_alerts.csv',
                    mime='text/csv',
                    help="Download all filtered alerts"
                )
            
            with col2:
                if st.button("🔄 Refresh Alerts"):
                    st.rerun()
        
        else:
            st.success("🎉 No active alerts! All inventory levels are healthy.")
    
    # Success message
    # Success message at bottom
    st.markdown("---")
    st.success("✅ Phase 5 Complete: Full Hospital Inventory Dashboard Ready!")
    
    # Dashboard info
    with st.expander("ℹ️ Dashboard Information"):
        st.markdown("""
        ### 🏥 Hospital Inventory Management System
        **Version:** 1.0  
        **Purpose:** AI for Good - Stock-Out Prevention  
        
        **Features:**
        - 📊 Real-time KPI monitoring
        - 🗺️ Interactive stock heatmap with color-coded status
        - 🚨 Automated alert management with priority-based actions
        - 📥 Export functionality for reports and analysis
        - 💾 Action logging and audit trail
        
        **Data Refresh:**
        - Stock metrics updated hourly via Dynamic Tables
        - Alerts generated automatically every 60 minutes
        - Dashboard data refreshed on page load
        
        **Built with:**
        - Snowflake Data Cloud
        - Streamlit for Python
        - Dynamic Tables & Tasks for automation
        - Streams for change data capture
        """)
    
    # Sidebar
    # Enhanced Sidebar
    st.sidebar.markdown("---")
    st.sidebar.success("✅ Connected to Snowflake")
    
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.metric("Active Alerts", int(kpi_df['TOTAL_ACTIVE_ALERTS'][0]))
    st.sidebar.metric("Urgent Items", int(kpi_df['URGENT_COUNT'][0]))
    st.sidebar.metric("Total Inventory Value", f"₹{float(stock_df['TOTAL_INVENTORY_VALUE'][0]):,.0f}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh All Data"):
        st.rerun()
    
    if st.sidebar.button("📊 Generate Report"):
        # Generate comprehensive report
        report_query = """
        SELECT 
            'Hospital Inventory Report' as report_title,
            CURRENT_TIMESTAMP() as generated_at,
            (SELECT COUNT(*) FROM V_ACTIVE_ALERTS) as total_alerts,
            (SELECT COUNT(*) FROM V_LATEST_STOCK_METRICS WHERE stock_status = 'STOCKOUT') as stockouts,
            (SELECT ROUND(SUM(suggested_reorder_cost_INR), 2) FROM V_ALERT_SUMMARY) as total_reorder_cost
        """
        report_df = session.sql(report_query).to_pandas()
        st.sidebar.success("✅ Report data ready!")
        
        report_csv = report_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Download Report",
            data=report_csv,
            file_name=f'inventory_report_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv'
        )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Last Updated")
    st.sidebar.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.caption("AI for Good Prototype")
    st.sidebar.caption("Stock-Out Prevention System")
    st.sidebar.caption("Built with Snowflake & Streamlit")
    
except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.code(str(e))
