import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import os

def load_data(file):
    """Load and process the CSV file."""
    df = pd.read_csv(file)
    df = df[~df['Description'].str.contains('paid', case=False, na=False)]
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Get absolute values for all numeric columns
    numeric_columns = ['Alysson', 'Bruce Cheng']
    for col in numeric_columns:
        df[col] = df[col].abs()
    
    return df

def process_daily_data(df, selected_person):
    """Process data to get daily totals."""
    daily_totals = df.groupby('Date')[[selected_person]].sum()
    daily_totals = daily_totals.reset_index()
    daily_totals.columns = ['Date', 'Total']
    return daily_totals

def process_monthly_data(df, selected_person):
    """Process data to get monthly totals and statistics."""
    monthly_totals = df.groupby(df['Date'].dt.strftime('%Y-%m'))[[selected_person]].agg({
        selected_person: ['sum', 'mean', 'count']
    }).reset_index()
    monthly_totals.columns = ['Month', 'Total', 'Average', 'Transactions']
    
    # Calculate month-over-month changes
    monthly_totals['Previous_Month_Total'] = monthly_totals['Total'].shift(1)
    monthly_totals['Change'] = monthly_totals['Total'] - monthly_totals['Previous_Month_Total']
    monthly_totals['Change_Percentage'] = (monthly_totals['Change'] / monthly_totals['Previous_Month_Total'] * 100).fillna(0)
    
    return monthly_totals

def get_category_data(df, selected_person, selected_date=None, is_monthly=False):
    """Get category breakdown for selected period."""
    if is_monthly:
        df['Month'] = df['Date'].dt.strftime('%Y-%m')
        df_filtered = df[df['Month'] == selected_date] if selected_date else df
    else:
        df_filtered = df[df['Date'] == selected_date] if selected_date else df
    
    category_totals = df_filtered.groupby('Category')[[selected_person]].sum()
    category_totals = category_totals.reset_index()
    category_totals.columns = ['Category', 'Total']
    category_totals = category_totals[category_totals['Category'].str.strip() != '']
    
    return category_totals

def create_daily_chart(daily_data, selected_person):
    """Create daily expenses bar chart."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=daily_data['Date'],
        y=daily_data['Total'],
        marker_color='#06b6d4',
        name='Daily Expense'
    ))
    
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        title={
            'text': f'Daily Expenses - {selected_person}',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 24}
        },
        xaxis=dict(
            title='Date',
            gridcolor='#333333',
            tickfont=dict(color='white', size=12),
            title_font=dict(color='white', size=14),
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor='#444444',
            linewidth=2
        ),
        yaxis=dict(
            title='Amount ($)',
            gridcolor='#333333',
            tickformat='$,.0f',
            tickfont=dict(color='white', size=12),
            title_font=dict(color='white', size=14),
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor='#444444',
            linewidth=2
        ),
        showlegend=False,
        height=500,
        hovermode='x unified'
    )
    
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>Date:</b> %{x|%Y-%m-%d}",
            "<b>Amount:</b> $%{y:,.2f}",
            "<extra></extra>"
        ])
    )
    
    return fig

def create_monthly_summary_chart(monthly_data, selected_person):
    """Create monthly summary charts with trends."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'Monthly Expenses - {selected_person}', 'Month-over-Month Changes'),
        vertical_spacing=0.22,
        specs=[[{"secondary_y": True}], [{"secondary_y": True}]]
    )
    
    # Add monthly total bars
    fig.add_trace(
        go.Bar(
            x=monthly_data['Month'],
            y=monthly_data['Total'],
            name='Monthly Total',
            marker_color='#06b6d4',
            hovertemplate="<br>".join([
                "<b>Month:</b> %{x}",
                "<b>Total:</b> $%{y:,.2f}",
                "<extra></extra>"
            ])
        ),
        row=1, col=1
    )
    
    # Add average line
    fig.add_trace(
        go.Scatter(
            x=monthly_data['Month'],
            y=monthly_data['Average'],
            name='Daily Average',
            line=dict(color='#10b981', width=2),
            hovertemplate="<br>".join([
                "<b>Month:</b> %{x}",
                "<b>Daily Average:</b> $%{y:,.2f}",
                "<extra></extra>"
            ])
        ),
        row=1, col=1
    )
    
    # Add month-over-month changes
    fig.add_trace(
        go.Bar(
            x=monthly_data['Month'],
            y=monthly_data['Change'],
            name='Monthly Change',
            marker_color='#8b5cf6',
            hovertemplate="<br>".join([
                "<b>Month:</b> %{x}",
                "<b>Change:</b> $%{y:,.2f}",
                "<extra></extra>"
            ])
        ),
        row=2, col=1
    )
    
    # Add percentage change line
    fig.add_trace(
        go.Scatter(
            x=monthly_data['Month'],
            y=monthly_data['Change_Percentage'],
            name='Change %',
            line=dict(color='#f59e0b', width=2),
            hovertemplate="<br>".join([
                "<b>Month:</b> %{x}",
                "<b>Change:</b> %{y:.1f}%",
                "<extra></extra>"
            ])
        ),
        row=2, col=1,
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        height=800,
        showlegend=True,
        legend=dict(
            font=dict(color='white'),
            bgcolor='#2d2d2d',
            bordercolor='#444444'
        )
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='#333333',
        tickfont=dict(color='white'),
        showgrid=True,
        zeroline=False,
        showline=True,
        linecolor='#444444'
    )
    
    fig.update_yaxes(
        gridcolor='#333333',
        tickfont=dict(color='white'),
        tickformat='$,.0f',
        showgrid=True,
        zeroline=False,
        showline=True,
        linecolor='#444444'
    )
    
    # Update secondary y-axis for percentage
    fig.update_yaxes(
        tickformat='.1%',
        tickfont=dict(color='white'),
        secondary_y=True,
        row=2, col=1
    )
    
    return fig

def create_category_chart(category_data, title):
    """Create category breakdown pie chart."""
    colors = [
        '#06b6d4',  # cyan
        '#8b5cf6',  # violet
        '#ec4899',  # pink
        '#f59e0b',  # amber
        '#10b981',  # emerald
        '#6366f1',  # indigo
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=category_data['Category'],
        values=category_data['Total'],
        textinfo='label+percent',
        marker=dict(colors=colors),
        textfont=dict(size=14, color='white'),  # Changed text color to white
        hovertemplate="<br>".join([
            "<b>%{label}</b>",
            "Amount: $%{value:,.2f}",
            "Percentage: %{percent}",
            "<extra></extra>"
        ]),
        textposition='inside',  # Ensure text is inside the pie slices
        hole=0.3  # Add a hole to make it a donut chart (optional)
    ))
    
    fig.update_layout(
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': 'white', 'size': 24}
        },
        margin=dict(t=50, l=20, r=20, b=20),
        height=500,  # Increased height
        showlegend=True,
        legend=dict(
            font=dict(color='white', size=12),
            bgcolor='#2d2d2d',
            bordercolor='#444444',
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig
def main():
    """Main application function."""
    st.set_page_config(page_title="Expense Tracker", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #1a1a1a;
            color: white;
        }
        div[data-testid="metric-container"] {
            background-color: #2d2d2d;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        div[data-testid="metric-container"] label {
            color: #06b6d4;
        }
        div[data-testid="stFileUploader"] {
            background-color: #2d2d2d;
            border-radius: 8px;
            padding: 15px;
        }
        .streamlit-expanderHeader {
            background-color: #2d2d2d;
            color: white;
        }
        div[data-testid="stDataFrame"] {
            background-color: #2d2d2d;
            padding: 10px;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("💰 Expense Tracker Dashboard")
    
    uploaded_file = st.file_uploader("Upload Splitwise CSV file", type=['csv'])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # User selection
        col1, col2 = st.columns(2)
        with col1:
            selected_person = st.selectbox(
                "Select Person",
                ["Bruce Cheng", "Alysson"]
            )
        
        with col2:
            view_mode = st.selectbox(
                "Select View",
                ["Daily Expenses", "Monthly Summary"]
            )
        
        if view_mode == "Daily Expenses":
            daily_data = process_daily_data(df, selected_person)
            
            # Display metrics
            total_expenses = daily_data['Total'].sum()
            avg_daily = daily_data['Total'].mean()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Expenses", f"${total_expenses:,.2f}")
            with col2:
                st.metric("Average Daily Expense", f"${avg_daily:,.2f}")
            
            # Display daily chart
            st.plotly_chart(create_daily_chart(daily_data, selected_person), use_container_width=True)
            
            # Create two columns for category analysis
            cat_col1, cat_col2 = st.columns([1, 2])
            
            with cat_col1:
                # Add date selector for daily view
                selected_date = st.date_input(
                    "Select date for category breakdown",
                    value=daily_data['Date'].max(),
                    min_value=daily_data['Date'].min(),
                    max_value=daily_data['Date'].max()
                )
            
            # Display category breakdown
            if selected_date:
                category_data = get_category_data(
                    df, 
                    selected_person, 
                    pd.to_datetime(selected_date),
                    is_monthly=False
                )
                if not category_data.empty:
                    st.markdown("### Category Breakdown")
                    
                    # Create two columns for pie chart and details
                    pie_col1, pie_col2 = st.columns([2, 1])
                    
                    with pie_col1:
                        fig = create_category_chart(
                            category_data, 
                            f'Expenses by Category - {selected_date.strftime("%Y-%m-%d")}'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with pie_col2:
                        st.markdown("#### Category Details")
                        # Display category details in a table
                        category_data_styled = pd.DataFrame({
                            'Category': category_data['Category'],
                            'Amount': category_data['Total'].apply(lambda x: f"${x:,.2f}")
                        })
                        st.dataframe(
                            category_data_styled, 
                            hide_index=True,
                            use_container_width=True
                        )
                else:
                    st.info("No expenses for the selected date.")
            
        else:  # Monthly Summary
            monthly_data = process_monthly_data(df, selected_person)
            
            # Display metrics
            total_expenses = monthly_data['Total'].sum()
            avg_monthly = monthly_data['Total'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Expenses", f"${total_expenses:,.2f}")
            with col2:
                st.metric("Average Monthly Expense", f"${avg_monthly:,.2f}")
            with col3:
                last_month_change = monthly_data['Change_Percentage'].iloc[-1]
                st.metric("Last Month Change", 
                         f"{last_month_change:,.1f}%",
                         delta=f"{last_month_change:,.1f}%")
            
            # Display monthly summary chart
            st.plotly_chart(create_monthly_summary_chart(monthly_data, selected_person), 
                          use_container_width=True)
            
            # Create two columns for category analysis
            cat_col1, cat_col2 = st.columns([1, 2])
            
            with cat_col1:
                # Add month selector for monthly view
                selected_month = st.selectbox(
                    "Select month for category breakdown",
                    monthly_data['Month'].tolist(),
                    index=len(monthly_data['Month'])-1
                )
            
            # Display category breakdown for selected month
            if selected_month:
                category_data = get_category_data(
                    df, 
                    selected_person, 
                    selected_month,
                    is_monthly=True
                )
                
                st.markdown("### Category Breakdown")
                
                # Create two columns for pie chart and details
                pie_col1, pie_col2 = st.columns([2, 1])
                
                with pie_col1:
                    fig = create_category_chart(
                        category_data, 
                        f'Expenses by Category - {selected_month}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with pie_col2:
                    st.markdown("#### Category Details")
                    # Display category details in a table
                    category_data_styled = pd.DataFrame({
                        'Category': category_data['Category'],
                        'Amount': category_data['Total'].apply(lambda x: f"${x:,.2f}")
                    })
                    st.dataframe(
                        category_data_styled, 
                        hide_index=True,
                        use_container_width=True
                    )

if __name__ == "__main__":
    main()
