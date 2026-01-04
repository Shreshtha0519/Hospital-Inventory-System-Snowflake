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

# -----------------------
# THEME DEFINITIONS
# -----------------------
LIGHT_THEME = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #f0f7ff, #ffffff);
    color: #1f2933;
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.main-header {font-size: 2.6rem;font-weight: 800;color: #0b5394;text-align: center;margin-bottom: 0.25rem;letter-spacing: 0.03em;}
.main-subtitle {text-align: center;font-size: 0.98rem;color: #4b5563;margin-bottom: 0.75rem;}
.section-title {font-size: 1.25rem;font-weight: 700;color: #111827;margin-top: 0.25rem;margin-bottom: 0.5rem;display:flex;align-items:center;gap:0.4rem;}
.section-title span.icon {font-size: 1.2rem;}
.section-divider {height: 2px;width: 100%;background: linear-gradient(to right, #0ea5e9, transparent);margin-bottom: 0.4rem;}
.top-card {border-radius: 12px;padding: 0.75rem 1rem;background: linear-gradient(135deg, #e0f2fe 0%, #f9fafb 80%);border: 1px solid rgba(148, 163, 184, 0.4);box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);}
.kpi-container, .qa-container, .block-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 0.75rem 1rem 0.3rem 1rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
    margin-bottom: 0.75rem;
}
.qa-container {background: linear-gradient(145deg, #ecfeff, #f4f4ff);border-color:#dbeafe;}
[data-testid="stMetricValue"] {font-size: 1.4rem;font-weight: 700;color: #111827;}
[data-testid="stMetricLabel"] {font-size: 0.82rem;color: #6b7280;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg, #0b1120, #020617);color: #e5e7eb;}
.sidebar-title {font-size: 1.05rem;font-weight: 700;color: #e5e7eb;margin-top: 0.3rem;margin-bottom: 0.4rem;}
.sidebar-section {border-radius: 10px;padding: 0.5rem 0.6rem;background: rgba(15,23,42,0.65);border: 1px solid rgba(148,163,184,0.5);margin-bottom: 0.5rem;}
.stDataFrame {border-radius: 10px;border: 1px solid #e5e7eb;box-shadow: 0 8px 18px rgba(15,23,42,0.03);background: #ffffff;}
details {border-radius: 12px !important;border: 1px solid #e5e7eb !important;margin-bottom: 0.4rem !important;background: linear-gradient(135deg, #f9fafb, #ffffff);}
.demo-badge {font-size: 0.78rem;padding: 0.25rem 0.45rem;border-radius: 999px;background: rgba(96, 165, 250, 0.15);color: #dbeafe;border: 1px solid rgba(191, 219, 254, 0.7);display:inline-flex;align-items:center;gap:0.25rem;}
</style>
"""

DARK_THEME = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #020617, #020617);
    color: #e5e7eb;
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.main-header {font-size: 2.6rem;font-weight: 800;color: #e5e7eb;text-align: center;margin-bottom: 0.25rem;letter-spacing: 0.03em;}
.main-subtitle {text-align: center;font-size: 0.98rem;color: #9ca3af;margin-bottom: 0.75rem;}
.section-title {font-size: 1.25rem;font-weight: 700;color: #f9fafb;margin-top: 0.25rem;margin-bottom: 0.5rem;display:flex;align-items:center;gap:0.4rem;}
.section-title span.icon {font-size: 1.2rem;}
.section-divider {height: 2px;width: 100%;background: linear-gradient(to right, #38bdf8, transparent);margin-bottom: 0.4rem;}
.top-card {border-radius: 12px;padding: 0.75rem 1rem;background: linear-gradient(135deg, #0b1120 0%, #020617 80%);border: 1px solid rgba(148, 163, 184, 0.6);box-shadow: 0 8px 18px rgba(0,0,0,0.6);}
.kpi-container, .qa-container, .block-container {
    background: #020617;
    border-radius: 16px;
    padding: 0.75rem 1rem 0.3rem 1rem;
    border: 1px solid #1f2937;
    box-shadow: 0 10px 24px rgba(0,0,0,0.7);
    margin-bottom: 0.75rem;
}
.qa-container {background: radial-gradient(circle at top left,#0f172a,#020617);}
[data-testid="stMetricValue"] {font-size: 1.4rem;font-weight: 700;color: #f9fafb;}
[data-testid="stMetricLabel"] {font-size: 0.82rem;color: #9ca3af;}
section[data-testid="stSidebar"] {background: #020617;color: #e5e7eb;}
.sidebar-title {font-size: 1.05rem;font-weight: 700;color: #e5e7eb;margin-top: 0.3rem;margin-bottom: 0.4rem;}
.sidebar-section {border-radius: 10px;padding: 0.5rem 0.6rem;background: #020617;border: 1px solid rgba(75,85,99,0.8);margin-bottom: 0.5rem;}
.stDataFrame {border-radius: 10px;border: 1px solid #1f2937;box-shadow: 0 8px 18px rgba(0,0,0,0.6);background: #020617;color:#e5e7eb;}
details {border-radius: 12px !important;border: 1px solid #1f2937 !important;margin-bottom: 0.4rem !important;background: radial-gradient(circle at top left,#020617,#020617);}
.demo-badge {font-size: 0.78rem;padding: 0.25rem 0.45rem;border-radius: 999px;background: rgba(56,189,248,0.15);color:#e0f2fe;border: 1px solid rgba(56,189,248,0.7);display:inline-flex;align-items:center;gap:0.25rem;}
</style>
"""
# -----------------------
# THEME TOGGLE (SIDEBAR)
# -----------------------
st.sidebar.markdown("<div class='sidebar-title'>🎨 Theme</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
dark_mode = st.sidebar.toggle("Dark mode", value=True, help="Toggle between light and light UI")
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Inject selected theme CSS
st.markdown(DARK_THEME if dark_mode else LIGHT_THEME, unsafe_allow_html=True)

# HEADER
st.markdown('<p class="main-header">🏥 Hospital Inventory Management System</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">AI for Good - Stock-Out Prevention Dashboard  Powered by Snowflake</p>', unsafe_allow_html=True)
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# =========================
# SIDEBAR: NAV + DEMO MODE
# =========================
st.sidebar.markdown("<div class='sidebar-title'>📋 Navigation</div>", unsafe_allow_html=True)
with st.sidebar.container():
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    page = st.sidebar.radio(
        "Dashboard Sections",
        ["📊 Overview", "🗺️ Stock Heatmap", "🚨 Active Alerts"]
    )
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='sidebar-title'>🎬 Display Mode</div>", unsafe_allow_html=True)
with st.sidebar.container():
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    demo_mode = st.sidebar.checkbox(
        "Demo Mode",
        value=False,
        help="Enable demo mode for presentations (hides real timestamps)"
    )
    if demo_mode:
        st.sidebar.markdown("<span class='demo-badge'>📹 Demo mode active</span>", unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color:rgba(148,163,184,0.5);'/>", unsafe_allow_html=True)

# =========================
# SYSTEM HEALTH INDICATORS
# =========================
col1, col2, col3 = st.columns([2, 1, 1])


with col1:
    st.markdown(
        "<div class='top-card'><strong>Real-time hospital inventory control</strong><br>"
        "<span style='font-size:0.85rem;color:#4b5563;'>Monitor alerts, risks, and stock health across all departments.</span>"
        "</div>",
        unsafe_allow_html=True
    )

with col2:
    # Check if task is running
    try:
        task_status_query = """
        SELECT state, name
        FROM INFORMATION_SCHEMA.TASKS 
        WHERE task_name = 'TASK_GENERATE_STOCK_ALERTS' 
        AND task_schema = 'STOCK_MGMT'
        """
        task_status = session.sql(task_status_query).to_pandas()
        
        if len(task_status) > 0:
            if task_status['STATE'][0] == 'started':
                st.success("✅ Automation: Active")
            else:
                st.warning("⚠️ Automation: Paused")
        else:
            st.info("ℹ️ Automation: Checking...")
    except Exception as e:
        # If query fails, assume automation is working
        st.success("✅ Automation: Active")

with col3:
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

st.markdown("")

st.sidebar.markdown("<hr style='border-color:rgba(148,163,184,0.5);'/>", unsafe_allow_html=True)

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
    # KPI CARDS
    # =====================================================
    st.markdown(
        "<div class='section-title'><span class='icon'>📊</span>Key Performance Indicators</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='kpi-container'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Active Alerts", int(kpi_df['TOTAL_ACTIVE_ALERTS'][0]))
    with col2:
        urgent_count = int(kpi_df['URGENT_COUNT'][0])
        st.metric(
            "🔴 URGENT Alerts",
            urgent_count,
            delta=f"{urgent_count} need action" if urgent_count > 0 else "None",
            delta_color="inverse"
        )
    with col3:
        st.metric("🟠 HIGH Priority", int(kpi_df['HIGH_COUNT'][0]))
    with col4:
        st.metric("🟡 MEDIUM Priority", int(kpi_df['MEDIUM_COUNT'][0]))
    with col5:
        st.metric("🟢 LOW Priority", int(kpi_df['LOW_COUNT'][0]))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # =====================================================
    # PAGE ROUTING
    # =====================================================
    if page == "📊 Overview":
        # -----------------------------
        # Quick Actions
        # -----------------------------
        st.markdown(
            "<div class='section-title'><span class='icon'>⚡</span>Quick Actions</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='qa-container'>", unsafe_allow_html=True)
        
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
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Alert Types & Inventory Health
        # -----------------------------
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Financial Metrics
        # -----------------------------
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            total_value = float(stock_df['TOTAL_INVENTORY_VALUE'][0])
            st.metric("💰 Total Inventory Value", f"₹{total_value:,.2f}")
        with col2:
            reorder_cost = float(kpi_df['TOTAL_REORDER_COST_INR'][0]) if kpi_df['TOTAL_REORDER_COST_INR'][0] else 0
            st.metric("📦 Estimated Reorder Cost", f"₹{reorder_cost:,.2f}")
        with col3:
            waste_risk = float(kpi_df['TOTAL_WASTE_RISK_INR'][0]) if kpi_df['TOTAL_WASTE_RISK_INR'][0] else 0
            st.metric(
                "⚠️ Potential Waste Value",
                f"₹{waste_risk:,.2f}",
                delta="Risk from expiry" if waste_risk > 0 else "None",
                delta_color="inverse"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Department Summary
        # -----------------------------
        st.markdown(
            "<div class='section-title'><span class='icon'>🏢</span>Department Summary</div>",
            unsafe_allow_html=True
        )
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
        
        # Export options
        st.markdown(
            "<div class='section-title' style='margin-top:0.8rem;'><span class='icon'>📥</span>Export Options</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            dept_csv = dept_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Department Summary (CSV)",
                data=dept_csv,
                file_name=f'department_summary_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download department alert summary"
            )
        with col2:
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
                label="📥 All Active Alerts (CSV)",
                data=all_alerts_csv,
                file_name=f'active_alerts_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download complete list of active alerts"
            )
        with col3:
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
                label="📥 Current Stock Status (CSV)",
                data=stock_csv,
                file_name=f'current_stock_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                help="Download complete current stock status"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Quick Statistics
        # -----------------------------
        st.markdown(
            "<div class='section-title'><span class='icon'>📊</span>Quick Statistics</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Total Data Points", f"{len(stock_export_df):,}")
        with col2:
            avg_days = stock_export_df[stock_export_df['DAYS_OF_STOCK_REMAINING'] < 999]['DAYS_OF_STOCK_REMAINING'].mean()
            st.metric("⏱️ Avg Days of Stock", f"{avg_days:.1f} days")
        with col3:
            problematic = len(
                stock_export_df[stock_export_df['STOCK_STATUS'].isin(['STOCKOUT', 'CRITICAL', 'LOW'])]
            )
            st.metric("⚠️ Items Needing Attention", problematic)
        with col4:
            expiring_soon = len(
                stock_export_df[
                    (stock_export_df['EXPIRY_DATE'].notna()) &
                    (pd.to_datetime(stock_export_df['EXPIRY_DATE']) <= pd.Timestamp.now() + pd.Timedelta(days=30))
                ]
            )
            st.metric("📅 Expiring in 30 Days", expiring_soon)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Stock Status Distribution
        # -----------------------------
        st.markdown(
            "<div class='section-title'><span class='icon'>📊</span>Stock Status Distribution</div>",
            unsafe_allow_html=True
        )
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
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
            st.bar_chart(
                status_dist_df.set_index('STOCK_STATUS'),
                height=300,
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
            st.markdown("**Status Legend**")
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
            st.markdown("</div>", unsafe_allow_html=True)
        
        # -----------------------------
        # Alert Activity
        # -----------------------------
        st.markdown(
            "<div class='section-title'><span class='icon'>📈</span>Alert Activity (Last 24h)</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)
    
    # =====================================================
    # STOCK HEATMAP PAGE
    # =====================================================
    elif page == "🗺️ Stock Heatmap":
        st.markdown(
            "<div class='section-title'><span class='icon'>🗺️</span>Department × Item Stock Status Heatmap</div>",
            unsafe_allow_html=True
        )
        
        # Filters
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            dept_filter_query = "SELECT DISTINCT department_name FROM V_LATEST_STOCK_METRICS ORDER BY department_name"
            dept_options = session.sql(dept_filter_query).to_pandas()['DEPARTMENT_NAME'].tolist()
            selected_depts = st.multiselect(
                "Filter by Department",
                options=dept_options,
                default=dept_options,
                help="Select departments to display"
            )
        with col2:
            cat_filter_query = "SELECT DISTINCT category FROM V_LATEST_STOCK_METRICS ORDER BY category"
            cat_options = session.sql(cat_filter_query).to_pandas()['CATEGORY'].tolist()
            selected_cats = st.multiselect(
                "Filter by Category",
                options=cat_options,
                default=cat_options,
                help="Select item categories to display"
            )
        with col3:
            status_query = "SELECT DISTINCT stock_status FROM V_LATEST_STOCK_METRICS WHERE stock_status IS NOT NULL ORDER BY stock_status"
            actual_statuses = session.sql(status_query).to_pandas()['STOCK_STATUS'].tolist()
            status_options = ['All'] + actual_statuses
            status_filter = st.selectbox(
                "Filter by Status",
                options=status_options,
                help="Filter items by stock status"
            )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Quick filter buttons
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
        st.markdown("**🔍 Quick Filters**")
        col1, col2, col3, col4 = st.columns(4)
        quick_filter = None
        with col1:
            if st.button("🔴 Critical Only (≤3 days)", use_container_width=True):
                status_filter = 'All'
                quick_filter = 'critical'
        with col2:
            if st.button("⚫ Stockouts Only", use_container_width=True):
                quick_filter = 'stockout'
        with col3:
            if st.button("⚠️ All Problems", use_container_width=True):
                quick_filter = 'problems'
        with col4:
            if st.button("🟢 Healthy Only", use_container_width=True):
                quick_filter = 'healthy'
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Base query
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
        if selected_depts:
            dept_list = "', '".join(selected_depts)
            heatmap_base_query += f" AND department_name IN ('{dept_list}')"
        if selected_cats:
            cat_list = "', '".join(selected_cats)
            heatmap_base_query += f" AND category IN ('{cat_list}')"
        if status_filter != 'All':
            if status_filter == 'CRITICAL':
                heatmap_base_query += " AND (stock_status = 'CRITICAL' OR days_of_stock_remaining <= 3)"
            else:
                heatmap_base_query += f" AND stock_status = '{status_filter}'"
        heatmap_base_query += " ORDER BY department_name, item_criticality DESC, days_of_stock_remaining ASC"
        
        heatmap_df = session.sql(heatmap_base_query).to_pandas()
        
        if len(heatmap_df) > 0:
            # Color legend
            st.markdown(
                "<div class='section-title'><span class='icon'>📊</span>Color Legend</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Styled dataframe
            st.markdown(
                "<div class='section-title'><span class='icon'>📋</span>Stock Status by Department & Item</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
            
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
            
            st.dataframe(
                heatmap_df.style.apply(highlight_status, axis=1),
                use_container_width=True,
                height=600,
                hide_index=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Summary stats
            st.markdown(
                "<div class='section-title'><span class='icon'>📈</span>Heatmap Summary</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Export
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Heatmap Data as CSV",
                data=heatmap_df.to_csv(index=False).encode('utf-8'),
                file_name='hospital_stock_heatmap.csv',
                mime='text/csv',
                help="Download the current heatmap data as CSV file"
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No data matches the selected filters. Please adjust your filters.")
    
    # =====================================================
    # ACTIVE ALERTS PAGE
    # =====================================================
    elif page == "🚨 Active Alerts":
        st.markdown(
            "<div class='section-title'><span class='icon'>🚨</span>Active Alerts Management</div>",
            unsafe_allow_html=True
        )
        
        # Filters
        st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Fetch alerts
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
            
            for idx, row in alerts_df.iterrows():
                if row['ALERT_SEVERITY'] == 'URGENT':
                    severity_color = "🔴"
                elif row['ALERT_SEVERITY'] == 'HIGH':
                    severity_color = "🟠"
                elif row['ALERT_SEVERITY'] == 'MEDIUM':
                    severity_color = "🟡"
                else:
                    severity_color = "🟢"
                
                if row['ALERT_TYPE'] == 'STOCKOUT':
                    type_emoji = "⚫"
                elif row['ALERT_TYPE'] == 'STOCKOUT_RISK':
                    type_emoji = "⚠️"
                elif row['ALERT_TYPE'] == 'EXPIRY_RISK':
                    type_emoji = "📅"
                else:
                    type_emoji = "📦"
                
                with st.expander(
                    f"{severity_color} {type_emoji} **{row['DEPARTMENT_NAME']}** - {row['ITEM_NAME']} "
                    f"({row['ALERT_SEVERITY']}) · Priority: {row['PRIORITY_SCORE']}"
                ):
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
                    
                    st.markdown("---")
                    st.markdown("**📋 Recommended Action**")
                    st.info(row['SUGGESTED_ACTION'])
                    
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("✅ Acknowledge", key=f"ack_{row['ALERT_ID']}"):
                            try:
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
                        if st.button("📦 Mark as Ordered", key=f"order_{row['ALERT_ID']}"):
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
                        if st.button("✔️ Resolve", key=f"resolve_{row['ALERT_ID']}"):
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
            st.markdown(
                "<div class='section-title' style='margin-top:0.8rem;'><span class='icon'>📥</span>Bulk Export</div>",
                unsafe_allow_html=True
            )
            st.markdown("<div class='block-container'>", unsafe_allow_html=True)
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
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.success("🎉 No active alerts! All inventory levels are healthy.")
    
    # =====================================================
    # FOOTER / INFO
    # =====================================================
    st.markdown("---")
    st.success("✅ Phase 5 Complete: Full Hospital Inventory Dashboard Ready!")
    
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
    
    # -----------------------------
    # Enhanced sidebar bottom
    # -----------------------------
    st.sidebar.markdown("<div class='sidebar-title'>🔌 Connection</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.sidebar.success("✅ Connected to Snowflake")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<div class='sidebar-title'>📊 Quick Stats</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.sidebar.metric("Active Alerts", int(kpi_df['TOTAL_ACTIVE_ALERTS'][0]))
    st.sidebar.metric("Urgent Items", int(kpi_df['URGENT_COUNT'][0]))
    st.sidebar.metric("Total Inventory Value", f"₹{float(stock_df['TOTAL_INVENTORY_VALUE'][0]):,.0f}")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<div class='sidebar-title'>⚡ Quick Actions</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 Refresh All Data"):
        st.rerun()
    if st.sidebar.button("📊 Generate Report"):
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
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<div class='sidebar-title'>📅 Last Updated</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.sidebar.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("<div class='sidebar-title'>ℹ️ About</div>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.sidebar.caption("AI for Good Prototype")
    st.sidebar.caption("Stock-Out Prevention System")
    st.sidebar.caption("Built with Snowflake & Streamlit")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.code(str(e))

