import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime
import os

def load_data(file):
    df = pd.read_csv(file)
    df = df[~df['Description'].str.contains('paid', case=False, na=False)]
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Get absolute values for all numeric columns
    numeric_columns = ['Alysson', 'Bruce Cheng']
    for col in numeric_columns:
        df[col] = df[col].abs()
    
    return df

def process_daily_data(df, selected_person):
    daily_totals = df.groupby('Date')[[selected_person]].sum()
    daily_totals = daily_totals.reset_index()
    daily_totals.columns = ['Date', 'Total']
    return daily_totals

def process_monthly_data(df, selected_person):
    # Monthly totals
    monthly_totals = df.groupby(df['Date'].dt.strftime('%Y-%m'))[[selected_person]].agg({
        selected_person: ['sum', 'mean', 'count']
    }).reset_index()
    monthly_totals.columns = ['Month', 'Total', 'Average', 'Transactions']
    
    # Calculate month-over-month changes
    monthly_totals['Previous_Month_Total'] = monthly_totals['Total'].shift(1)
    monthly_totals['Change'] = monthly_totals['Total'] - monthly_totals['Previous_Month_Total']
    monthly_totals['Change_Percentage'] = (monthly_totals['Change'] / monthly_totals['Previous_Month_Total'] * 100).fillna(0)
    
    return monthly_totals

def create_daily_chart(daily_data, selected_person):
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
        height=500
    )
    
    return fig

def create_monthly_summary_chart(monthly_data, selected_person):
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=(f'Monthly Expenses - {selected_person}', 
                                     'Month-over-Month Changes'),
                       vertical_spacing=0.2,
                       specs=[[{"secondary_y": True}],
                            [{"secondary_y": True}]])
    
    # Add monthly total bars
    fig.add_trace(
        go.Bar(x=monthly_data['Month'], 
               y=monthly_data['Total'],
               name='Monthly Total',
               marker_color='#06b6d4',
               hovertemplate="<br>".join([
                   "<b>Month:</b> %{x}",
                   "<b>Total:</b> $%{y:,.2f}",
                   "<extra></extra>"
               ])),
        row=1, col=1
    )
    
    # Add average line
    fig.add_trace(
        go.Scatter(x=monthly_data['Month'],
                  y=monthly_data['Average'],
                  name='Daily Average',
                  line=dict(color='#10b981', width=2),
                  hovertemplate="<br>".join([
                      "<b>Month:</b> %{x}",
                      "<b>Daily Average:</b> $%{y:,.2f}",
                      "<extra></extra>"
                  ])),
        row=1, col=1
    )
    
    # Add month-over-month changes
    fig.add_trace(
        go.Bar(x=monthly_data['Month'],
               y=monthly_data['Change'],
               name='Monthly Change',
               marker_color='#8b5cf6',
               hovertemplate="<br>".join([
                   "<b>Month:</b> %{x}",
                   "<b>Change:</b> $%{y:,.2f}",
                   "<extra></extra>"
               ])),
        row=2, col=1
    )
    
    # Add percentage change line
    fig.add_trace(
        go.Scatter(x=monthly_data['Month'],
                  y=monthly_data['Change_Percentage'],
                  name='Change %',
                  line=dict(color='#f59e0b', width=2),
                  hovertemplate="<br>".join([
                      "<b>Month:</b> %{x}",
                      "<b>Change:</b> %{y:.1f}%",
                      "<extra></extra>"
                  ])),
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
        tickformat=',.1f%',
        tickfont=dict(color='white'),
        secondary_y=True,
        row=2, col=1
    )
    
    return fig

def main():
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

if __name__ == "__main__":
    main()