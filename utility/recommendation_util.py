from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

from app_pages.executive_dashboard import create_empty_figure


def generate_recommendations(daily_sales, sku):
    """Generate executive recommendations"""

    recommendations = []

    # ============================================
    # 1. Stockout Risk Recommendations
    # ============================================

    # Calculate stockout risk (simplified)
    if not daily_sales.empty and 'units_sold' in daily_sales.columns:
        last_30_days = daily_sales[daily_sales['date'] >= daily_sales['date'].max() - timedelta(days=30)]
        sku_sales = last_30_days.groupby('sku_id')['units_sold'].sum().reset_index()
        sku_sales.columns = ['sku_id', 'units_sold']

        # Simulate high risk SKUs
        high_risk_skus = sku_sales[sku_sales['units_sold'] > sku_sales['units_sold'].quantile(0.9)].head(10)
        high_risk_skus['stock_value'] = high_risk_skus['units_sold'] * 100
        high_risk_skus['stock_cover'] = np.random.uniform(0.1, 0.3, len(high_risk_skus))

        for _, row in high_risk_skus.iterrows():
            recommendations.append({
                'priority': 1,
                'category': 'Stockout Risk',
                'sku': row['sku_id'],
                'action': 'REORDER NOW',
                'impact': f"₹{row['stock_value']:,.0f} at risk",
                'details': f"Stock cover: {row['stock_cover']:.2f} days"
            })
    else:
        high_risk_skus = pd.DataFrame()

    # ============================================
    # 2. Overstock Recommendations
    # ============================================

    # Simulate overstock SKUs
    if not daily_sales.empty and 'units_sold' in daily_sales.columns:
        sku_avg = daily_sales.groupby('sku_id')['units_sold'].mean().reset_index()
        sku_avg.columns = ['sku_id', 'avg_units']
        high_overstock = sku_avg[sku_avg['avg_units'] > sku_avg['avg_units'].quantile(0.85)].head(10)
        high_overstock['stock_value'] = high_overstock['avg_units'] * 200
        high_overstock['weeks_of_stock'] = np.random.uniform(10, 20, len(high_overstock))

        for _, row in high_overstock.iterrows():
            recommendations.append({
                'priority': 1,
                'category': 'Overstock',
                'sku': row['sku_id'],
                'action': 'MARKDOWN',
                'impact': f"₹{row['stock_value']:,.0f} locked",
                'details': f"{row['weeks_of_stock']:.1f} weeks of stock"
            })
    else:
        high_overstock = pd.DataFrame()

    # ============================================
    # 3. Category Recommendations
    # ============================================

    if not daily_sales.empty and 'category' in daily_sales.columns and 'revenue' in daily_sales.columns:
        top_cat = daily_sales.groupby('category')['revenue'].sum().idxmax()
        top_cat_revenue = daily_sales.groupby('category')['revenue'].sum().max()
        recommendations.append({
            'priority': 2,
            'category': 'Category Strategy',
            'sku': 'All',
            'action': 'FOCUS ON TOP CATEGORIES',
            'impact': f"₹{top_cat_revenue:,.0f} revenue",
            'details': f"Focus on {top_cat} category"
        })
    else:
        top_cat = 'N/A'
        top_cat_revenue = 0

    # ============================================
    # 4. Seasonal Recommendations
    # ============================================

    if not daily_sales.empty and 'season' in daily_sales.columns and 'revenue' in daily_sales.columns:
        peak_season = daily_sales.groupby('season')['revenue'].sum().idxmax()
        peak_revenue = daily_sales[daily_sales['season'] == peak_season]['revenue'].sum()
        recommendations.append({
            'priority': 2,
            'category': 'Seasonal Planning',
            'sku': 'All',
            'action': 'PREPARE FOR PEAK SEASON',
            'impact': f"₹{peak_revenue:,.0f} revenue",
            'details': f"Stock up for {peak_season} season"
        })
    else:
        peak_season = 'N/A'

    # ============================================
    # 5. Customer Recommendations
    # ============================================

    if not daily_sales.empty and 'customer_id' in daily_sales.columns:
        recommendations.append({
            'priority': 2,
            'category': 'Customer Strategy',
            'sku': 'All',
            'action': 'IMPROVE RETENTION',
            'impact': '₹0 at risk',
            'details': 'Focus on repeat customers'
        })

    # ============================================
    # 6. Pricing Recommendations
    # ============================================

    recommendations.append({
        'priority': 3,
        'category': 'Pricing Strategy',
        'sku': 'All',
        'action': 'REVIEW PRICING',
        'impact': '₹0 at risk',
        'details': 'Analyze price elasticity'
    })

    # Convert to DataFrame
    rec_df = pd.DataFrame(recommendations)

    # If empty, create default recommendations
    if rec_df.empty:
        rec_df = pd.DataFrame([
            {'priority': 1, 'category': 'General', 'sku': 'All', 'action': 'REVIEW INVENTORY',
             'impact': '₹0 at risk', 'details': 'No specific risks identified'},
            {'priority': 2, 'category': 'Strategy', 'sku': 'All', 'action': 'MONITOR SALES',
             'impact': '₹0 at risk', 'details': 'Continue monitoring'}
        ])

    rec_df = rec_df.sort_values('priority')

    return rec_df, high_risk_skus, high_overstock, top_cat, peak_season


def create_priority_chart(rec_df):
    """1. Recommendation Priority Chart"""

    if rec_df is None or rec_df.empty or 'priority' not in rec_df.columns:
        return create_empty_figure("No recommendation priority data available")

    priority_counts = (
        rec_df['priority']
        .value_counts()
        .sort_index()
    )

    priority_labels = [
        f'Priority {p}'
        for p in priority_counts.index
    ]

    color_map = {
        1: '#ef4444',
        2: '#f59e0b',
        3: '#fcd34d',
        4: '#60a5fa',
        5: '#34d399'
    }

    colors = [
        color_map.get(priority, '#667eea')
        for priority in priority_counts.index
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=priority_labels,
            y=priority_counts.values,

            marker_color=colors,

            text=priority_counts.values,
            textposition='outside',

            textfont=dict(
                color='white',
                size=12
            ),

            hovertemplate=(
                '<b>%{x}</b><br>'
                'Recommendations: %{y:,}'
                '<extra></extra>'
            )
        )
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Recommendations by Priority',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Priority Level',
        yaxis_title='Number of Recommendations',

        showlegend=False,

        margin=dict(
            l=50,
            r=40,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    return fig


def create_category_chart(rec_df):
    """2. Recommendations by Category Chart"""

    if rec_df is None or rec_df.empty or 'category' not in rec_df.columns:
        return create_empty_figure("No recommendation category data available")

    cat_rec = (
        rec_df['category']
        .value_counts()
        .sort_values(ascending=True)
    )

    fig = px.bar(
        x=cat_rec.values,
        y=cat_rec.index,
        orientation='h',
        labels={
            'x': 'Number of Recommendations',
            'y': 'Category'
        },
        color=cat_rec.values,
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Recommendations by Category',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Number of Recommendations',
        yaxis_title='',

        showlegend=False,
        coloraxis_showscale=False,

        margin=dict(
            l=50,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_traces(
        texttemplate='%{x:,}',
        textposition='outside',

        textfont=dict(
            color='white',
            size=10
        ),

        hovertemplate=(
            '<b>%{y}</b><br>'
            'Recommendations: %{x:,}'
            '<extra></extra>'
        )
    )

    return fig


def create_impact_chart(rec_df):
    """3. Impact Distribution by Category"""

    if rec_df is None or rec_df.empty or 'category' not in rec_df.columns:
        return create_empty_figure("No impact data available")

    impact_cat = (
        rec_df['category']
        .value_counts()
    )

    fig = px.pie(
        values=impact_cat.values,
        names=impact_cat.index,
        hole=0.4,
        color_discrete_sequence=[
            '#667eea',
            '#764ba2',
            '#f59e0b',
            '#34d399',
            '#ef4444',
            '#60a5fa',
            '#f472b6'
        ]
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Impact Distribution by Category',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=70,
            b=30
        ),

        font=dict(
            size=12,
            color='white'
        ),

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,

            font=dict(
                color='white',
                size=10
            )
        )
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',

        textfont=dict(
            color='white',
            size=11
        ),

        marker=dict(
            line=dict(
                color='white',
                width=1
            )
        ),

        hovertemplate=(
            '<b>%{label}</b><br>'
            'Recommendations: %{value:,}<br>'
            'Share: %{percent}'
            '<extra></extra>'
        )
    )

    return fig


def create_action_chart(rec_df):
    """4. Top Actions Recommended"""

    if rec_df is None or rec_df.empty or 'action' not in rec_df.columns:
        return create_empty_figure("No recommendation action data available")

    action_count = (
        rec_df['action']
        .value_counts()
        .head(5)
        .sort_values(ascending=True)
    )

    fig = px.bar(
        x=action_count.values,
        y=action_count.index,
        orientation='h',
        labels={
            'x': 'Number of Recommendations',
            'y': 'Action'
        },
        color=action_count.values,
        color_continuous_scale='Greens'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Top Actions Recommended',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Number of Recommendations',
        yaxis_title='',

        showlegend=False,
        coloraxis_showscale=False,

        margin=dict(
            l=50,
            r=50,
            t=70,
            b=50
        ),

        font=dict(
            size=12,
            color='white'
        )
    )

    fig.update_xaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_yaxes(
        gridcolor='rgba(255,255,255,0.05)',
        tickfont=dict(color='white'),
        title_font=dict(color='white')
    )

    fig.update_traces(
        texttemplate='%{x:,}',
        textposition='outside',

        textfont=dict(
            color='white',
            size=10
        ),

        hovertemplate=(
            '<b>%{y}</b><br>'
            'Recommendations: %{x:,}'
            '<extra></extra>'
        )
    )

    return fig