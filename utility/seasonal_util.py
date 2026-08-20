import pandas as pd
import plotly.graph_objects as pgo
import plotly.express as px
import streamlit as st

from app_pages.executive_dashboard import create_empty_figure


def calculate_seasonality_metrics(daily_sales):
    """Calculate seasonality metrics"""

    # Month order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    # Monthly metrics
    monthly_metrics = daily_sales.groupby('month_name').agg({
        'revenue': 'sum',
        'units_sold': 'sum'
    }).reset_index()
    monthly_metrics['month_order'] = monthly_metrics['month_name'].map(
        {m: i for i, m in enumerate(month_order)}
    )
    monthly_metrics = monthly_metrics.sort_values('month_order')

    # Seasonal metrics
    seasonal_metrics = daily_sales.groupby('season').agg({
        'revenue': 'sum',
        'units_sold': 'sum'
    }).reset_index()

    # Day of week metrics
    dow_metrics = daily_sales.groupby('day_name')['revenue'].sum().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    )

    # Category by season
    season_cat = daily_sales.groupby(['season', 'category'])['revenue'].sum().unstack()

    # Peak metrics
    peak_month = monthly_metrics.loc[monthly_metrics['revenue'].idxmax(), 'month_name']
    peak_season = seasonal_metrics.loc[seasonal_metrics['revenue'].idxmax(), 'season']
    best_day = dow_metrics.idxmax()
    worst_day = dow_metrics.idxmin()

    return {
        'monthly_metrics': monthly_metrics,
        'seasonal_metrics': seasonal_metrics,
        'dow_metrics': dow_metrics,
        'season_cat': season_cat,
        'peak_month': peak_month,
        'peak_season': peak_season,
        'best_day': best_day,
        'worst_day': worst_day,
        'total_revenue': daily_sales['revenue'].sum(),
        'total_units': daily_sales['units_sold'].sum(),
        'avg_monthly_revenue': monthly_metrics['revenue'].mean(),
        'avg_monthly_units': monthly_metrics['units_sold'].mean()
    }


def create_monthly_revenue_chart(monthly_metrics):
    """1. Monthly Revenue Bar Chart"""

    if monthly_metrics is None or monthly_metrics.empty:
        return create_empty_figure("No monthly revenue data available")

    fig = px.bar(
        monthly_metrics,
        x='month_name',
        y='revenue',
        labels={
            'revenue': 'Revenue (₹)',
            'month_name': 'Month'
        },
        color='revenue',
        color_continuous_scale='Blues'
    )

    # Find peak month
    peak_idx = monthly_metrics['revenue'].idxmax()
    peak_month = monthly_metrics.loc[peak_idx, 'month_name']
    peak_revenue = monthly_metrics.loc[peak_idx, 'revenue']

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Monthly Revenue Pattern',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Month',
        yaxis_title='Revenue (₹)',

        showlegend=False,
        coloraxis_showscale=False,

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
        title_font=dict(color='white'),
        tickprefix='₹',
        tickformat=',.0f'
    )

    fig.update_traces(
        texttemplate='₹%{y:,.0f}',
        textposition='outside',
        textfont=dict(
            color='white',
            size=10
        ),
        marker_line_color='white',
        marker_line_width=0.5,
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Revenue: ₹%{y:,.0f}'
            '<extra></extra>'
        )
    )

    # Peak annotation
    fig.add_annotation(
        x=peak_month,
        y=peak_revenue,
        text="🏆 Peak",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(
            color='#f59e0b',
            size=12
        )
    )

    return fig


def create_monthly_units_chart(monthly_metrics):
    """2. Monthly Units Sold Bar Chart"""

    if monthly_metrics is None or monthly_metrics.empty:
        return create_empty_figure("No monthly units data available")

    fig = px.bar(
        monthly_metrics,
        x='month_name',
        y='units_sold',
        labels={
            'units_sold': 'Units Sold',
            'month_name': 'Month'
        },
        color='units_sold',
        color_continuous_scale='Oranges'
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Monthly Units Sold Pattern',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Month',
        yaxis_title='Units Sold',

        showlegend=False,
        coloraxis_showscale=False,

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
        title_font=dict(color='white'),
        tickformat=',.0f'
    )

    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside',
        textfont=dict(
            color='white',
            size=10
        ),
        marker_line_color='white',
        marker_line_width=0.5,
        hovertemplate=(
            '<b>%{x}</b><br>'
            'Units Sold: %{y:,.0f}'
            '<extra></extra>'
        )
    )

    return fig


def create_seasonal_pie_chart(seasonal_metrics):
    """3. Seasonal Revenue Distribution Pie Chart"""

    if seasonal_metrics is None or seasonal_metrics.empty:
        return create_empty_figure("No seasonal revenue data available")

    fig = px.pie(
        seasonal_metrics,
        values='revenue',
        names='season',
        hole=0.4,
        color_discrete_sequence=[
            '#667eea',
            '#f59e0b',
            '#34d399',
            '#ef4444'
        ]
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Revenue by Season',
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
            size=12
        ),

        hovertemplate=(
            '<b>%{label}</b><br>'
            'Revenue: ₹%{value:,.0f}<br>'
            'Share: %{percent}'
            '<extra></extra>'
        ),

        marker=dict(
            line=dict(
                color='white',
                width=1
            )
        )
    )

    return fig


def create_dow_chart(dow_metrics):
    """4. Day of Week Pattern Bar Chart"""

    if dow_metrics is None or len(dow_metrics) == 0:
        return create_empty_figure("No day-of-week data available")

    df = dow_metrics.reset_index()
    df.columns = ['day', 'revenue']

    # Make sure days appear in correct order
    day_order = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    df['day'] = pd.Categorical(
        df['day'],
        categories=day_order,
        ordered=True
    )

    df = df.sort_values('day')

    # Weekday vs weekend colors
    colors = [
        '#667eea'
        if day not in ['Saturday', 'Sunday']
        else '#f59e0b'
        for day in df['day']
    ]

    fig = px.bar(
        df,
        x='day',
        y='revenue',
        labels={
            'revenue': 'Revenue (₹)',
            'day': 'Day'
        }
    )

    fig.update_traces(
        marker_color=colors
    )

    fig.update_layout(
        height=400,
        template='plotly_dark',

        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',

        title=dict(
            text='Revenue by Day of Week',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Day',
        yaxis_title='Revenue (₹)',

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
        title_font=dict(color='white'),
        tickprefix='₹',
        tickformat=',.0f'
    )

    fig.update_traces(
        texttemplate='₹%{y:,.0f}',
        textposition='outside',
        textfont=dict(
            color='white',
            size=10
        ),
        marker_line_color='white',
        marker_line_width=0.5,

        hovertemplate=(
            '<b>%{x}</b><br>'
            'Revenue: ₹%{y:,.0f}'
            '<extra></extra>'
        )
    )

    # Best and worst day
    best_day = df.loc[df['revenue'].idxmax(), 'day']
    worst_day = df.loc[df['revenue'].idxmin(), 'day']

    best_value = df.loc[
        df['day'] == best_day,
        'revenue'
    ].iloc[0]

    worst_value = df.loc[
        df['day'] == worst_day,
        'revenue'
    ].iloc[0]

    fig.add_annotation(
        x=best_day,
        y=best_value,
        text="⬆ Best",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-35,
        font=dict(
            color='#34d399',
            size=11
        )
    )

    fig.add_annotation(
        x=worst_day,
        y=worst_value,
        text="⬇ Worst",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-35,
        font=dict(
            color='#ef4444',
            size=11
        )
    )

    return fig


def create_season_category_chart(season_cat):
    """5. Category Performance by Season Line Chart"""

    if season_cat is None or season_cat.empty:
        fig = pgo.Figure()

        fig.add_annotation(
            text="No category-season data available",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=16,
                color="white"
            )
        )

        fig.update_layout(
            height=400,
            template='plotly_dark',
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',

            title=dict(
                text='Category Performance by Season',
                x=0.5,
                xanchor='center',
                font=dict(
                    size=18,
                    color='white'
                )
            ),

            font=dict(
                color='white'
            )
        )

        return fig

    # Top 8 categories
    top_cats = (
        season_cat.sum()
        .sort_values(ascending=False)
        .head(8)
        .index
    )

    fig = pgo.Figure()

    colors = [
        '#667eea',
        '#764ba2',
        '#f59e0b',
        '#34d399',
        '#ef4444',
        '#60a5fa',
        '#a78bfa',
        '#f472b6'
    ]

    for i, category in enumerate(top_cats):

        fig.add_trace(
            pgo.Scatter(
                x=season_cat.index,
                y=season_cat[category],
                mode='lines+markers',
                name=str(category)[:15],

                line=dict(
                    width=2,
                    color=colors[i % len(colors)]
                ),

                marker=dict(
                    size=8,
                    color=colors[i % len(colors)],
                    line=dict(
                        color='white',
                        width=1
                    )
                ),

                hovertemplate=(
                    f'<b>{category}</b><br>'
                    '%{x}: ₹%{y:,.0f}'
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
            text='Category Performance by Season (Top 8)',
            x=0.5,
            xanchor='center',
            font=dict(
                size=18,
                color='white'
            )
        ),

        xaxis_title='Season',
        yaxis_title='Revenue (₹)',

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,

            font=dict(
                color='white',
                size=9
            )
        ),

        margin=dict(
            l=50,
            r=40,
            t=80,
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
        title_font=dict(color='white'),
        tickprefix='₹',
        tickformat=',.0f'
    )

    return fig