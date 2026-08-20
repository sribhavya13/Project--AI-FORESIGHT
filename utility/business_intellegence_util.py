from datetime import timedelta
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def calculate_bi_metrics(df):
    """Calculate BI metrics"""
    if df.empty:
        return {}

    # Filter last 30 days
    last_30 = df[df['date'] >= df['date'].max() - timedelta(days=30)]

    metrics = {
        'total_revenue': df['revenue'].sum(),
        'total_units': df['units_sold'].sum(),
        'total_orders': df['receipt_id'].nunique() if 'receipt_id' in df.columns else len(df),
        'avg_order_value': df['revenue'].mean() if 'revenue' in df.columns else 0,
        'unique_skus': df['sku_id'].nunique(),
        'unique_customers': df['customer_id'].nunique() if 'customer_id' in df.columns else 0,
        'revenue_last_30': last_30['revenue'].sum() if not last_30.empty else 0,
        'units_last_30': last_30['units_sold'].sum() if not last_30.empty else 0,
        'avg_daily_revenue': last_30['revenue'].mean() if not last_30.empty else 0,
        'avg_daily_units': last_30['units_sold'].mean() if not last_30.empty else 0,
    }
    return metrics


def create_revenue_trend(df, period='Daily'):
    """Revenue trend chart"""
    if df.empty:
        return go.Figure()

    # Make sure date is datetime
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # Aggregate by period
    if period == 'Daily':
        trend = df.groupby('date', as_index=False)['revenue'].sum()
        x_col = 'date'

    elif period == 'Weekly':
        # Use ISO year + ISO week together
        iso = df['date'].dt.isocalendar()

        df['iso_year'] = iso.year
        df['week'] = iso.week

        trend = (
            df.groupby(['iso_year', 'week'], as_index=False)['revenue']
            .sum()
        )

        # Convert ISO year/week to the Monday of that week
        trend['date'] = pd.to_datetime(
            trend['iso_year'].astype(str)
            + '-W'
            + trend['week'].astype(str).str.zfill(2)
            + '-1',
            format='%G-W%V-%u'
        )

        x_col = 'date'

    else:  # Monthly
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        trend = (
            df.groupby(['year', 'month'], as_index=False)['revenue']
            .sum()
        )

        trend['date'] = pd.to_datetime(
            trend['year'].astype(str)
            + '-'
            + trend['month'].astype(str).str.zfill(2)
            + '-01'
        )

        x_col = 'date'

    # Sort chronologically
    trend = trend.sort_values('date')

    # Create chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=trend[x_col],
        y=trend['revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#6366F1', width=3),
        marker=dict(size=6, color='#6366F1'),
        fill='tozeroy',
        fillcolor='rgba(99,102,241,0.15)',
        hovertemplate=(
            '<b>%{x|%d %b %Y}</b><br>'
            'Revenue: ₹%{y:,.0f}'
            '<extra></extra>'
        )
    ))

    fig.update_layout(
        title='Revenue Trend',
        xaxis_title='Date',
        yaxis_title='Revenue (₹)',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350,
        hovermode='x unified'
    )

    return fig



def create_sales_by_category(df):
    """Sales by category chart"""
    if df.empty or 'category' not in df.columns:
        return go.Figure()

    category_sales = df.groupby('category')['revenue'].sum().sort_values(ascending=True).reset_index()
    category_sales = category_sales.tail(10)  # Top 10

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=category_sales['revenue'],
        y=category_sales['category'],
        orientation='h',
        marker=dict(
            color=category_sales['revenue'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Revenue')
        ),
        text=category_sales['revenue'].apply(lambda x: f'₹{x:,.0f}'),
        textposition='outside',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Top 10 Categories by Revenue',
        xaxis_title='Revenue (₹)',
        yaxis_title='Category',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350,
        margin=dict(l=100, r=50, t=50, b=50)
    )

    return fig


def create_top_products(df):
    """Top products chart"""
    if df.empty:
        return go.Figure()

    # Get SKU names from the data
    if 'sku_name' in df.columns:
        top_products = df.groupby('sku_name')['revenue'].sum().sort_values(ascending=True).reset_index().tail(10)
        label_col = 'sku_name'
    else:
        top_products = df.groupby('sku_id')['revenue'].sum().sort_values(ascending=True).reset_index().tail(10)
        label_col = 'sku_id'

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=top_products['revenue'],
        y=top_products[label_col],
        orientation='h',
        marker=dict(
            color=top_products['revenue'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title='Revenue')
        ),
        text=top_products['revenue'].apply(lambda x: f'₹{x:,.0f}'),
        textposition='outside',
        textfont=dict(color='white', size=10),
        hovertemplate='<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Top 10 Products by Revenue',
        xaxis_title='Revenue (₹)',
        yaxis_title='Product',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350,
        margin=dict(l=120, r=50, t=50, b=50)
    )

    return fig


def create_daily_sales_distribution(df):
    """Daily sales distribution heatmap"""
    if df.empty:
        return go.Figure()

    # Create pivot table
    df['day_of_week'] = df['date'].dt.dayofweek
    df['hour'] = df['date'].dt.hour if 'hour' in df.columns else 12

    pivot = df.pivot_table(
        values='units_sold',
        index=df['date'].dt.hour if 'hour' in df.columns else df['date'].dt.day,
        columns='day_of_week',
        aggfunc='mean',
        fill_value=0
    )

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y=pivot.index,
        colorscale='Viridis',
        hovertemplate='Day: %{x}<br>Hour: %{y}<br>Units: %{z:.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Sales Distribution Heatmap',
        xaxis_title='Day of Week',
        yaxis_title='Hour of Day',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350
    )

    return fig


def create_monthly_trend(df):
    """Monthly trend chart"""
    if df.empty:
        return go.Figure()

    monthly = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum().reset_index()
    monthly['date'] = monthly['date'].astype(str)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly['date'],
        y=monthly['revenue'],
        marker=dict(
            color=monthly['revenue'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title='Revenue')
        ),
        text=monthly['revenue'].apply(lambda x: f'₹{x:,.0f}'),
        textposition='outside',
        textfont=dict(color='white', size=9),
        hovertemplate='<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Monthly Revenue Trend',
        xaxis_title='Month',
        yaxis_title='Revenue (₹)',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350
    )

    return fig


def create_channel_distribution(df):
    """Channel distribution chart"""
    if df.empty or 'channel' not in df.columns:
        return go.Figure()

    channel_data = df.groupby('channel')['revenue'].sum().reset_index()

    colors = ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981']

    fig = go.Figure(data=[go.Pie(
        labels=channel_data['channel'],
        values=channel_data['revenue'],
        hole=0.4,
        marker=dict(colors=colors[:len(channel_data)]),
        textinfo='label+percent',
        textposition='auto',
        textfont=dict(color='white', size=12),
        hovertemplate='<b>%{label}</b><br>Revenue: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title='Revenue by Channel',
        template='plotly_dark',
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        font=dict(color='white'),
        height=350,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5
        )
    )

    return fig


def create_kpi_card(label, value, delta=None, delta_color='normal', icon='📊'):
    """Create a KPI card with consistent styling"""

    if delta:
        if delta_color == 'inverse':
            delta_color = 'inverse'
        else:
            delta_color = 'normal'

    return st.metric(
        label=f"{icon} {label}",
        value=value,
        delta=delta,
        delta_color=delta_color
    )
