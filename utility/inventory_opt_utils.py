import textwrap

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
def calculate_inventory_metrics(sales, inventory, sku):
    """Calculate inventory optimization metrics"""

    # Get latest inventory
    if 'last_restock_date' in inventory.columns:
        latest_inventory = inventory.sort_values('last_restock_date').groupby('sku_id').last().reset_index()
    else:
        latest_inventory = inventory.copy()

    # Calculate daily sales per SKU
    if not sales.empty and 'sku_id' in sales.columns and 'quantity' in sales.columns and 'date' in sales.columns:
        total_days = (sales['date'].max() - sales['date'].min()).days
        if total_days > 0:
            sku_daily_sales = sales.groupby('sku_id')['quantity'].sum() / total_days
        else:
            sku_daily_sales = sales.groupby('sku_id')['quantity'].sum() / 30
    else:
        # Create synthetic daily sales
        sku_daily_sales = pd.Series(np.random.uniform(1, 20, len(latest_inventory)),
                                    index=latest_inventory['sku_id'])

    # Merge with inventory
    inventory_analysis = latest_inventory.merge(
        sku_daily_sales.reset_index(),
        on='sku_id',
        how='left'
    )
    inventory_analysis['daily_sales'] = inventory_analysis.iloc[:, -1].fillna(0.1)

    # Calculate stockout risk
    inventory_analysis['days_of_stock'] = inventory_analysis['stock_on_hand'] / \
                (inventory_analysis['daily_sales'] + 0.01)
    inventory_analysis['stockout_risk'] = pd.cut(
        inventory_analysis['days_of_stock'],
        bins=[-np.inf, 3, 7, 15, np.inf],
        labels=['HIGH', 'MEDIUM', 'LOW', 'NONE']
    )

    # Merge with SKU for category
    if not sku.empty and 'sku_id' in sku.columns:
        inventory_analysis = inventory_analysis.merge(
            sku[['sku_id', 'sku_name', 'category', 'subcategory']],
            on='sku_id',
            how='left'
        )

    # Calculate stock value
    if 'unit_price' in inventory_analysis.columns:
        inventory_analysis['stock_value'] = inventory_analysis['stock_on_hand'] * inventory_analysis['unit_price']
    else:
        inventory_analysis['stock_value'] = inventory_analysis['stock_on_hand'] * 100

    # Generate reorder recommendations
    reorder_recs = generate_reorder_recommendations(inventory_analysis)

    # Overstock analysis
    inventory_analysis['overstock'] = inventory_analysis['days_of_stock'] > 30
    overstock_skus = inventory_analysis[inventory_analysis['overstock']]

    return inventory_analysis, reorder_recs, overstock_skus


def generate_reorder_recommendations(inv_df, lead_time=7, safety_stock=1.5):
    """Generate reorder recommendations"""

    recommendations = []

    for _, row in inv_df.iterrows():
        if row['stockout_risk'] in ['HIGH', 'MEDIUM']:
            daily_demand = row['daily_sales']
            lead_time_demand = daily_demand * lead_time
            safety_stock_qty = daily_demand * safety_stock
            reorder_qty = max(lead_time_demand + safety_stock_qty - row['stock_on_hand'], 0)

            recommendations.append({
                'sku_id': row['sku_id'],
                'current_stock': row['stock_on_hand'],
                'daily_demand': daily_demand,
                'stockout_risk': row['stockout_risk'],
                'reorder_qty': int(reorder_qty),
                'priority': 'HIGH' if row['stockout_risk'] == 'HIGH' else 'MEDIUM',
                'category': row.get('category', 'Unknown')
            })

    rec_df = pd.DataFrame(recommendations)
    if not rec_df.empty:
        rec_df = rec_df.sort_values('priority')

    return rec_df


def create_stockout_risk_chart(inventory_analysis):
    """1. Stockout Risk Distribution - Donut Chart"""

    risk_counts = inventory_analysis['stockout_risk'].value_counts()

    colors = {
        'HIGH': '#ef4444',
        'MEDIUM': '#f59e0b',
        'LOW': '#fcd34d',
        'NONE': '#34d399'
    }

    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title='Stockout Risk Distribution',
        hole=0.4,
        color=risk_counts.index,
        color_discrete_map=colors
    )

    fig.update_layout(
        height=400,

        # Dark background
        paper_bgcolor='#000000',
        plot_bgcolor='#0a0a0a',

        # White text
        font=dict(
            color='white',
            size=12
        ),

        # Center title
        title=dict(
            text='Stockout Risk Distribution',
            x=0.5,
            xanchor='center',
            font=dict(
                color='white',
                size=18
            )
        ),

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='white')
        ),

        margin=dict(
            l=20,
            r=20,
            t=80,
            b=30
        )
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont=dict(
            color='white',
            size=11
        ),
        hovertemplate=(
            '<b>%{label}</b><br>'
            'SKUs: %{value:,}<br>'
            'Share: %{percent}'
            '<extra></extra>'
        )
    )

    return fig


def create_days_of_stock_chart(inventory_analysis):
    """2. Days of Stock Distribution - Histogram"""

    df = inventory_analysis[
        inventory_analysis['days_of_stock'] < 60
    ].copy()

    fig = px.histogram(
        df,
        x='days_of_stock',
        nbins=30,
        title='Days of Stock Distribution',
        labels={
            'days_of_stock': 'Days of Stock',
            'count': 'Number of SKUs'
        },
        color_discrete_sequence=['#667eea']
    )

    # High risk line
    fig.add_vline(
        x=3,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="High Risk (3d)",
        annotation_position="top right",
        annotation_font=dict(
            color="#ef4444",
            size=10
        )
    )

    # Medium risk line
    fig.add_vline(
        x=7,
        line_dash="dash",
        line_color="#f59e0b",
        annotation_text="Medium Risk (7d)",
        annotation_position="top right",
        annotation_font=dict(
            color="#f59e0b",
            size=10
        )
    )

    fig.update_layout(
        height=400,

        # Dark background
        paper_bgcolor='#000000',
        plot_bgcolor='#0a0a0a',

        # White text
        font=dict(
            color='white',
            size=12
        ),

        # Center title
        title=dict(
            text='Days of Stock Distribution',
            x=0.5,
            xanchor='center',
            font=dict(
                color='white',
                size=18
            )
        ),

        showlegend=False,

        margin=dict(
            l=60,
            r=30,
            t=80,
            b=60
        )
    )

    fig.update_xaxes(
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        gridcolor='rgba(255,255,255,0.06)',
        zerolinecolor='rgba(255,255,255,0.1)'
    )

    fig.update_yaxes(
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        gridcolor='rgba(255,255,255,0.06)',
        zerolinecolor='rgba(255,255,255,0.1)'
    )

    return fig


def create_reorder_chart(reorder_recs):
    """3. Reorder Quantity by SKU - Bar Chart"""

    if reorder_recs.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No reorder recommendations",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color='white'
            )
        )

        fig.update_layout(
            height=400,
            paper_bgcolor='#000000',
            plot_bgcolor='#0a0a0a',
            font=dict(color='white')
        )

        return fig

    top_recs = reorder_recs.head(15).copy()

    fig = px.bar(
        top_recs,
        x='reorder_qty',
        y='sku_id',
        orientation='h',
        title='Top 15 Reorder Recommendations',
        labels={
            'reorder_qty': 'Reorder Quantity',
            'sku_id': ''
        },
        color='priority',
        color_discrete_map={
            'HIGH': '#ef4444',
            'MEDIUM': '#f59e0b',
            'LOW': '#34d399'
        },
        hover_data=[
            'current_stock',
            'daily_demand'
        ]
    )

    fig.update_layout(
        height=400,

        # Dark background
        paper_bgcolor='#000000',
        plot_bgcolor='#0a0a0a',

        # White text
        font=dict(
            color='white',
            size=12
        ),

        # Center title
        title=dict(
            text='Top 15 Reorder Recommendations',
            x=0.5,
            xanchor='center',
            font=dict(
                color='white',
                size=18
            )
        ),

        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='white')
        ),

        margin=dict(
            l=80,
            r=50,
            t=85,
            b=50
        )
    )

    fig.update_xaxes(
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        gridcolor='rgba(255,255,255,0.06)',
        zerolinecolor='rgba(255,255,255,0.1)'
    )

    fig.update_yaxes(
        title_font=dict(color='white'),
        tickfont=dict(color='white'),
        gridcolor='rgba(255,255,255,0.06)',
        autorange='reversed'
    )

    fig.update_traces(
        texttemplate='%{x}',
        textposition='outside',
        textfont=dict(
            color='white',
            size=10
        )
    )

    return fig


def create_overstock_chart(overstock_skus):
    """4. Overstock Value by Category - Treemap"""

    if overstock_skus.empty:

        fig = go.Figure()

        fig.add_annotation(
            text="No overstock SKUs found",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(
                size=15,
                color='white'
            )
        )

        fig.update_layout(
            height=400,
            paper_bgcolor='#000000',
            plot_bgcolor='#0a0a0a',
            font=dict(color='white')
        )

        return fig

    if 'category' in overstock_skus.columns:

        overstock_value = (
            overstock_skus
            .groupby('category')['stock_value']
            .sum()
            .reset_index()
        )

        fig = px.treemap(
            overstock_value,
            path=['category'],
            values='stock_value',
            title='Overstock Value by Category',
            color='stock_value',
            color_continuous_scale='Reds',
            hover_data={
                'stock_value': ':,.0f'
            }
        )

    else:

        fig = px.treemap(
            overstock_skus.head(20),
            path=['sku_id'],
            values='stock_value',
            title='Overstock Value by SKU',
            color='stock_value',
            color_continuous_scale='Reds'
        )

    fig.update_layout(
        height=400,

        # Dark background
        paper_bgcolor='#000000',
        plot_bgcolor='#0a0a0a',

        # White text
        font=dict(
            color='white',
            size=12
        ),

        # Center title
        title=dict(
            text=(
                'Overstock Value by Category'
                if 'category' in overstock_skus.columns
                else 'Overstock Value by SKU'
            ),
            x=0.5,
            xanchor='center',
            font=dict(
                color='white',
                size=18
            )
        ),

        margin=dict(
            l=20,
            r=20,
            t=80,
            b=20
        )
    )

    fig.update_traces(
        textinfo="label+value",
        textfont=dict(
            color='white',
            size=12
        )
    )

    return fig


def create_reorder_table(reorder_recs):
    """Reorder Recommendations Table"""

    if reorder_recs.empty:

        st.info(
            "✅ No reorder recommendations. "
            "All SKUs have healthy stock levels."
        )

        return

    # --------------------------------------------------------
    # DARK HEADER CARD
    # --------------------------------------------------------

    html = textwrap.dedent("""
        <div style="
            background: #050505;
            border: 1px solid rgba(255,255,255,0.12);
            padding: 1rem;
            border-radius: 12px 12px 0 0;
            border-left: 4px solid #f59e0b;
            margin-top: 1rem;
            margin-bottom: 0;
        ">
            <h4 style="
                color: #f59e0b;
                text-align: center;
                margin: 0;
                font-size: 1.1rem;
                font-weight: 700;
                letter-spacing: 0.5px;
            ">
                📋 REORDER RECOMMENDATIONS
            </h4>
        </div>
    """)

    st.markdown(
        html,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TABLE DATA
    # --------------------------------------------------------

    required_columns = [
        "sku_id",
        "current_stock",
        "daily_demand",
        "reorder_qty",
        "priority",
        "category"
    ]

    # Only use columns that exist
    available_columns = [
        col for col in required_columns
        if col in reorder_recs.columns
    ]

    display_df = (
        reorder_recs
        .head(20)[available_columns]
        .copy()
    )

    # Rename columns
    rename_map = {
        "sku_id": "SKU",
        "current_stock": "Current Stock",
        "daily_demand": "Daily Demand",
        "reorder_qty": "Reorder Qty",
        "priority": "Priority",
        "category": "Category"
    }

    display_df.rename(
        columns=rename_map,
        inplace=True
    )

    # --------------------------------------------------------
    # PRIORITY COLORS / ICONS
    # --------------------------------------------------------

    if "Priority" in display_df.columns:

        def color_priority(value):

            value = str(value).upper()

            if value == "HIGH":
                return "🔴 HIGH"

            elif value == "MEDIUM":
                return "🟡 MEDIUM"

            elif value == "LOW":
                return "🟢 LOW"

            return value

        display_df["Priority"] = (
            display_df["Priority"]
            .apply(color_priority)
        )

    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    column_config = {}

    if "SKU" in display_df.columns:
        column_config["SKU"] = st.column_config.TextColumn(
            "SKU"
        )

    if "Current Stock" in display_df.columns:
        column_config["Current Stock"] = st.column_config.NumberColumn(
            "Current Stock",
            format="%d"
        )

    if "Daily Demand" in display_df.columns:
        column_config["Daily Demand"] = st.column_config.NumberColumn(
            "Daily Demand",
            format="%.1f"
        )

    if "Reorder Qty" in display_df.columns:
        column_config["Reorder Qty"] = st.column_config.NumberColumn(
            "Reorder Qty",
            format="%d"
        )

    if "Priority" in display_df.columns:
        column_config["Priority"] = st.column_config.TextColumn(
            "Priority"
        )

    if "Category" in display_df.columns:
        column_config["Category"] = st.column_config.TextColumn(
            "Category"
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config
    )