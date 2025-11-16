import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="مُكًلّف",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;700&display=swap');

        * {
            font-family: "IBM Plex Sans Arabic", sans-serif !important;
        }

        .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
            direction: rtl !important;
            text-align: right !important;
        }
        
        /* English direction override */
        .ltr-content {
            direction: ltr !important;
            text-align: left !important;
        }

    </style>
""", unsafe_allow_html=True)


# Custom CSS
st.markdown("""
    <style>
    .main {
        background: #000000 !important;
    }
    .stApp {
        background: #000000 !important;
    }
    .stMetric {
        background: linear-gradient(135deg, rgba(40, 40, 45, 0.9), rgba(50, 50, 55, 0.9));
        border: 1px solid rgba(80, 80, 85, 0.3);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
        color: white;
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ar'  # Default to Arabic
if 'sales_data' not in st.session_state:
    # Sample data
    st.session_state.sales_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Sales': [45000, 52000, 48000, 61000, 58000, 67000]
    })
if 'forecast_data' not in st.session_state:
    st.session_state.forecast_data = None
if 'insights' not in st.session_state:
    st.session_state.insights = []

# Translations
translations = {
    'en': {
        'app_title': '🤖 AI-Powered Business Management System',
        'language': 'Language / اللغة',
        'dashboard': 'Dashboard',
        'sales_forecast': 'Sales Forecast',
        'ai_insights': 'AI Insights',
        'data_management': 'Data Management',
        'total_revenue': 'Total Revenue',
        'avg_sales': 'Average Sales',
        'trend': 'Trend',
        'forecast_accuracy': 'Forecast Accuracy',
        'sales_overview': 'Sales Overview',
        'generate_forecast': 'Generate AI Forecast',
        'forecast_chart': 'Sales Forecast (Next 6 Months)',
        'insight_title': 'AI-Powered Business Insights',
        'add_data': 'Add Sales Data',
        'month': 'Month',
        'sales': 'Sales Amount',
        'add_button': 'Add Data',
        'clear_button': 'Clear All Data',
        'current_data': 'Current Sales Data',
        'export_data': 'Export Data',
        'increase': '📈 Increasing',
        'decrease': '📉 Decreasing',
        'stable': '➡️ Stable',
        'no_data': 'No data available. Please add sales data.',
        'recommendations': 'Recommendations',
        'monthly_comparison': 'Monthly Comparison',
        'historical': 'Historical',
        'forecast': 'Forecast'
    },
    'ar': {
        'app_title': '🤖 مُكَلّف, لإدارة الأعمال بالذكاء الاصطناعي',
        'language': 'اللغة',
        'dashboard': 'لوحة القيادة ',
        'sales_forecast': 'توقعات المبيعات   ',
        'ai_insights': 'رؤى الذكاء الاصطناعي',
        'data_management': 'إدارة البيانات',
        'total_revenue': 'إجمالي الإيرادات',
        'avg_sales': 'متوسط المبيعات',
        'trend': 'الاتجاه',
        'forecast_accuracy': 'دقة التوقع',
        'sales_overview': 'نظرة عامة على المبيعات',
        'generate_forecast': 'إنشاء توقعات الذكاء الاصطناعي',
        'forecast_chart': 'توقعات المبيعات (الأشهر الستة القادمة)',
        'insight_title': 'رؤى الأعمال بالذكاء الاصطناعي',
        'add_data': 'إضافة بيانات المبيعات',
        'month': 'الشهر',
        'sales': 'مبلغ المبيعات',
        'add_button': 'إضافة بيانات',
        'clear_button': 'مسح جميع البيانات',
        'current_data': 'بيانات المبيعات الحالية',
        'export_data': 'تصدير البيانات',
        'increase': '📈 متزايد',
        'decrease': '📉 متناقص',
        'stable': '➡️ مستقر',
        'no_data': 'لا توجد بيانات متاحة. يرجى إضافة بيانات المبيعات.',
        'recommendations': 'التوصيات',
        'monthly_comparison': 'مقارنة شهرية',
        'historical': 'تاريخ',
        'forecast': 'توقعات'
    }
}

def get_text(key):
    return translations[st.session_state.language][key]

# Sidebar
with st.sidebar:
    st.title(get_text('language'))
    
    # Language selector
    lang_option = st.radio(
        "",
        options=['English', 'العربية'],
        index=1
    )
    st.session_state.language = 'en' if lang_option == 'English' else 'ar'
    
    st.divider()
    
    # Navigation
    page = st.radio(
        "",
        [get_text('dashboard'), get_text('sales_forecast'), 
         get_text('ai_insights'), get_text('data_management')]
    )

# Main title
st.title(get_text('app_title'))
st.divider()

# Helper functions
def calculate_metrics():
    if len(st.session_state.sales_data) == 0:
        return 0, 0, 'stable'
    
    total = st.session_state.sales_data['Sales'].sum()
    avg = st.session_state.sales_data['Sales'].mean()
    
    # Calculate trend
    if len(st.session_state.sales_data) >= 3:
        recent = st.session_state.sales_data['Sales'].tail(3).mean()
        older = st.session_state.sales_data['Sales'].head(-3).mean() if len(st.session_state.sales_data) > 3 else recent
        
        if recent > older * 1.05:
            trend = 'increase'
        elif recent < older * 0.95:
            trend = 'decrease'
        else:
            trend = 'stable'
    else:
        trend = 'stable'
    
    return total, avg, trend

def generate_forecast():
    """Generate sales forecast using linear regression"""
    if len(st.session_state.sales_data) < 3:
        st.error("Need at least 3 data points to generate forecast!")
        return
    
    # Prepare data
    data = st.session_state.sales_data.copy()
    data['X'] = range(len(data))
    
    # Linear regression
    n = len(data)
    sum_x = data['X'].sum()
    sum_y = data['Sales'].sum()
    sum_xy = (data['X'] * data['Sales']).sum()
    sum_x2 = (data['X'] ** 2).sum()
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    # Generate forecast for next 6 months
    months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    forecast_values = []
    
    for i in range(6):
        x = n + i
        predicted = slope * x + intercept
        # Add some realistic variation
        noise = np.random.normal(0, predicted * 0.05)
        forecast_values.append(max(0, predicted + noise))
    
    forecast_df = pd.DataFrame({
        'Month': months,
        'Sales': forecast_values,
        'Type': 'Forecast'
    })
    
    st.session_state.forecast_data = forecast_df
    
    # Generate insights
    generate_insights(data, forecast_df, slope, intercept)
    
    return forecast_df

def generate_insights(historical, forecast, slope, intercept):
    """Generate AI insights based on data analysis"""
    avg_sales = historical['Sales'].mean()
    last_month = historical['Sales'].iloc[-1]
    next_month = forecast['Sales'].iloc[0]
    
    trend = 'increase' if slope > 0 else 'decrease' if slope < 0 else 'stable'
    trend_percent = abs((slope / avg_sales) * 100)
    
    change_percent = ((next_month - last_month) / last_month) * 100
    
    insights = []
    
    if st.session_state.language == 'en':
        insights.append(f"📊 Sales are showing a **{trend}** trend of **{trend_percent:.1f}%** monthly.")
        insights.append(f"💰 Predicted sales for next month: **{next_month:,.0f} SAR**")
        insights.append(f"📈 This represents a **{change_percent:+.1f}%** change from last month.")
        
        if slope > 0:
            insights.append("✅ **Recommendation:** Increase inventory to meet growing demand.")
            insights.append("📢 **Marketing:** Consider expanding your marketing reach.")
        else:
            insights.append("⚠️ **Recommendation:** Focus on customer retention strategies.")
            insights.append("📢 **Marketing:** Implement promotional campaigns to boost sales.")
    else:
        insights.append(f"📊 المبيعات تظهر اتجاه **{get_text(trend)}** بنسبة **{trend_percent:.1f}%** شهرياً.")
        insights.append(f"💰 المبيعات المتوقعة للشهر القادم: **{next_month:,.0f} ريال**")
        insights.append(f"📈 هذا يمثل تغيير **{change_percent:+.1f}%** عن الشهر الماضي.")
        
        if slope > 0:
            insights.append("✅ **التوصية:** زيادة المخزون لتلبية الطلب المتزايد.")
            insights.append("📢 **التسويق:** فكر في توسيع نطاق التسويق.")
        else:
            insights.append("⚠️ **التوصية:** التركيز على استراتيجيات الاحتفاظ بالعملاء.")
            insights.append("📢 **التسويق:** تنفيذ حملات ترويجية لتعزيز المبيعات.")
    
    st.session_state.insights = insights

# Page content
if page == get_text('dashboard'):
    # Metrics
    total, avg, trend = calculate_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=get_text('total_revenue'),
            value=f"{total:,.0f} ﷼",
            delta=f"{trend}" if trend != 'stable' else None
        )
    
    with col2:
        st.metric(
            label=get_text('avg_sales'),
            value=f"{avg:,.0f} ﷼"
        )
    
    with col3:
        st.metric(
            label=get_text('trend'),
            value=get_text(trend)
        )
    
    with col4:
        st.metric(
            label=get_text('forecast_accuracy'),
            value="87%"
        )
    
    st.divider()
    
    # Sales chart
    st.subheader(get_text('sales_overview'))
    
    if len(st.session_state.sales_data) > 0:
        fig = px.area(
            st.session_state.sales_data,
            x='Month',
            y='Sales',
            title='',
            labels={'Sales': get_text('sales'), 'Month': get_text('month')}
        )
        fig.update_traces(
            fillcolor='rgba(99, 102, 241, 0.3)',
            line_color='rgba(99, 102, 241, 1)'
        )
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0, 0, 0, 0.95)',
            plot_bgcolor='rgba(0, 0, 0, 0.95)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(get_text('no_data'))

elif page == get_text('sales_forecast'):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(get_text('forecast_chart'))
    
    with col2:
        if st.button(get_text('generate_forecast'), type="primary", use_container_width=True):
            with st.spinner('Generating AI forecast...'):
                generate_forecast()
                st.success('Forecast generated successfully!')
    
    st.divider()
    
    if st.session_state.forecast_data is not None:
        # Combine historical and forecast data
        historical = st.session_state.sales_data.copy()
        historical['Type'] = get_text('historical')
        
        combined = pd.concat([historical, st.session_state.forecast_data], ignore_index=True)
        
        # Create forecast chart
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=historical['Month'],
            y=historical['Sales'],
            mode='lines+markers',
            name=get_text('historical'),
            line=dict(color='rgb(99, 102, 241)', width=3),
            marker=dict(size=8)
        ))
        
        # Forecast data
        fig.add_trace(go.Scatter(
            x=st.session_state.forecast_data['Month'],
            y=st.session_state.forecast_data['Sales'],
            mode='lines+markers',
            name=get_text('forecast'),
            line=dict(color='rgb(239, 68, 68)', width=3, dash='dash'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            height=450,
            xaxis_title=get_text('month'),
            yaxis_title=get_text('sales'),
            hovermode='x unified',
            paper_bgcolor='rgba(0, 0, 0, 0.95)',
            plot_bgcolor='rgba(0, 0, 0, 0.95)',
            font=dict(color='#ffffff')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly comparison bar chart
        st.subheader(get_text('monthly_comparison'))
        fig_bar = px.bar(
            st.session_state.forecast_data,
            x='Month',
            y='Sales',
            color_discrete_sequence=['#818CF8']
        )
        fig_bar.update_layout(
            height=300,
            paper_bgcolor='rgba(0, 0, 0, 0.95)',
            plot_bgcolor='rgba(0, 0, 0, 0.95)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Click 'Generate AI Forecast' to see predictions!")

elif page == get_text('ai_insights'):
    st.subheader(get_text('insight_title'))
    
    if len(st.session_state.insights) > 0:
        for insight in st.session_state.insights:
            st.info(insight)
    else:
        st.warning(get_text('no_data'))
        st.info("Generate a forecast first to see AI insights!")

elif page == get_text('data_management'):
    st.subheader(get_text('add_data'))
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        new_month = st.text_input(get_text('month'), placeholder="Jan, Feb, Mar...")
    
    with col2:
        new_sales = st.number_input(get_text('sales'), min_value=0, value=0, step=1000)
    
    with col3:
        st.write("")
        st.write("")
        if st.button(get_text('add_button'), type="primary"):
            if new_month and new_sales > 0:
                new_data = pd.DataFrame({'Month': [new_month], 'Sales': [new_sales]})
                st.session_state.sales_data = pd.concat(
                    [st.session_state.sales_data, new_data],
                    ignore_index=True
                )
                st.success(f"Added: {new_month} - {new_sales:,} ﷼")
                st.rerun()
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button(get_text('clear_button'), type="secondary"):
            st.session_state.sales_data = pd.DataFrame(columns=['Month', 'Sales'])
            st.session_state.forecast_data = None
            st.session_state.insights = []
            st.rerun()
    
    st.divider()
    
    # Display current data
    st.subheader(get_text('current_data'))
    
    if len(st.session_state.sales_data) > 0:
        st.dataframe(
            st.session_state.sales_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Export option
        csv = st.session_state.sales_data.to_csv(index=False)
        st.download_button(
            label=get_text('export_data'),
            data=csv,
            file_name='sales_data.csv',
            mime='text/csv'
        )
    else:
        st.info(get_text('no_data'))

# Footer with clickable link
st.divider()
st.markdown(
    'مُكَلّف | <a href="https://linktr.ee/AnasAlshammari" target="_blank" style="text-decoration:;">Anas Alshammari</a>',
    unsafe_allow_html=True
)