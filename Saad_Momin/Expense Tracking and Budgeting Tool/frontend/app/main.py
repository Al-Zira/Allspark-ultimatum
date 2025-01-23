import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.api_client import APIClient

# Initialize API client
api_client = APIClient()

class ExpenseTracker:
    def __init__(self):
        st.set_page_config(
            page_title="Smart Expense Tracker",
            page_icon="💰",
            layout="wide"
        )
        
        # Initialize session state
        if 'show_success' not in st.session_state:
            st.session_state.show_success = False
    
    def render_sidebar(self):
        st.sidebar.title("💰 Smart Finance")
        menu_options = [
            "Dashboard",
            "Add Expense",
            "View Expenses",
            "Budget Management",
            "AI Insights"
        ]
        return st.sidebar.radio("Navigation", menu_options)
    
    def render_dashboard(self):
        st.title("Dashboard")
        
        # Get statistics
        stats = api_client.get_expense_stats()
        
        # Create columns for metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Spending", f"${stats['total_spending']:.2f}")
        with col2:
            st.metric("Average Transaction", f"${stats['average_transaction']:.2f}")
        with col3:
            st.metric("Total Transactions", stats['total_transactions'])
        
        # Monthly trend
        st.subheader("Monthly Spending Trends")
        monthly_data = api_client.get_monthly_trend()
        if monthly_data:
            fig = px.line(monthly_data, x='month', y='amount',
                         title='Monthly Spending Trends')
            st.plotly_chart(fig, use_container_width=True)
        
        # Category distribution
        st.subheader("Spending by Category")
        distribution = api_client.get_category_distribution()
        if distribution:
            fig = px.pie(distribution, values='amount', names='category',
                        title='Category Distribution')
            st.plotly_chart(fig, use_container_width=True)
        
        # Budget alerts
        st.subheader("Budget Alerts")
        alerts = api_client.get_budget_alerts()
        for alert in alerts:
            color = "green"
            if alert['status'] == "Warning":
                color = "orange"
            elif alert['status'] == "Critical":
                color = "red"
            
            st.markdown(f"""
            <div style='padding: 10px; border-radius: 5px; background-color: {color}20;'>
                <h4 style='color: {color};'>{alert['category']}</h4>
                <p>Spent: ${alert['spent']:.2f} / ${alert['budget']:.2f} ({alert['percentage']:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_add_expense(self):
        st.title("Add Expense")
        
        with st.form("add_expense_form"):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            description = st.text_input("Description")
            
            # Add a button to get AI suggestion for category
            col1, col2 = st.columns([3, 1])
            with col1:
                category = st.text_input("Category")
            with col2:
                if st.form_submit_button("Suggest Category"):
                    if not description:
                        st.error("Please enter a description first")
                    else:
                        try:
                            suggestion = api_client.get_category_suggestion(description, amount)
                            if suggestion and suggestion.get("suggested_category"):
                                st.session_state.suggested_category = suggestion["suggested_category"]
                                st.info(f"Suggested Category: {st.session_state.suggested_category}")
                        except Exception as e:
                            st.error(f"Error getting category suggestion: {str(e)}")
            
            # Use suggested category if available
            if hasattr(st.session_state, 'suggested_category') and not category:
                category = st.session_state.suggested_category
            
            if st.form_submit_button("Add Expense"):
                if not description:
                    st.error("Description is required")
                    return
                if not category:
                    st.error("Category is required")
                    return
                
                try:
                    # Convert date to datetime with time component
                    date_time = datetime.combine(date, datetime.min.time())
                    
                    expense_data = {
                        "date": date_time.isoformat(),
                        "amount": float(amount),
                        "description": description.strip(),
                        "category": category.strip().upper()
                    }
                    api_client.create_expense(expense_data)
                    st.success("Expense added successfully!")
                    # Clear form using session state
                    st.session_state.show_success = True
                    if hasattr(st.session_state, 'suggested_category'):
                        del st.session_state.suggested_category
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding expense: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            st.error(f"API Error: {error_detail.get('detail', str(e))}")
                        except:
                            st.error(f"Error details: {e.response.text}")
    
    def render_view_expenses(self):
        st.title("View Expenses")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")
        with col3:
            try:
                categories = [expense['category'] for expense in api_client.get_expenses()]
                category = st.selectbox("Category", ["All"] + list(set(categories)))
            except Exception:
                # If we can't get categories, provide a default empty list
                category = st.selectbox("Category", ["All"])
        
        try:
            # Convert dates to datetime with time components
            start_datetime = datetime.combine(start_date, datetime.min.time())
            # Set end_datetime to end of day
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get filtered expenses
            expenses = api_client.get_expenses(
                start_date=start_datetime,
                end_date=end_datetime,
                category=category if category != "All" else None
            )
            
            # Display expenses table
            if expenses:
                expense_data = []
                for expense in expenses:
                    expense_data.append({
                        "Date": expense['date'].split('T')[0],
                        "Amount": f"${expense['amount']:.2f}",
                        "Description": expense['description'],
                        "Category": expense['category']
                    })
                st.table(expense_data)
            else:
                st.info("No expenses found for the selected filters.")
        except Exception as e:
            st.error(f"Error loading expenses: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    st.error(f"API Error: {error_detail.get('detail', str(e))}")
                except:
                    st.error(f"Error details: {e.response.text}")
    
    def render_budget_management(self):
        st.title("Budget Management")
        
        # Add/Update Budget
        with st.form("budget_form"):
            category = st.text_input("Category")
            monthly_limit = st.number_input("Monthly Budget", min_value=0.01, format="%f")
            
            if st.form_submit_button("Set Budget"):
                try:
                    budget_data = {
                        "category": category,
                        "monthly_limit": monthly_limit
                    }
                    api_client.create_or_update_budget(budget_data)
                    st.success("Budget updated successfully!")
                except Exception as e:
                    st.error(f"Error updating budget: {str(e)}")
        
        # View Current Budgets
        st.subheader("Current Budgets")
        budgets = api_client.get_budgets()
        if budgets:
            for budget in budgets:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{budget['category']}**: ${budget['monthly_limit']:.2f}")
                with col3:
                    if st.button("Delete", key=f"delete_{budget['category']}"):
                        try:
                            api_client.delete_budget(budget['category'])
                            st.success(f"Budget for {budget['category']} deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting budget: {str(e)}")
    
    def render_ai_insights(self):
        st.title("AI Insights")
        
        # Create tabs for different insights
        tab1, tab2 = st.tabs(["Spending Analysis", "Budget Recommendations"])
        
        with tab1:
            st.subheader("Spending Pattern Analysis")
            try:
                insights = api_client.get_spending_insights()
                st.markdown(insights["insights"])
            except Exception as e:
                st.error(f"Error getting spending insights: {str(e)}")
        
        with tab2:
            st.subheader("Budget Recommendations")
            try:
                recommendations = api_client.get_budget_recommendations()
                st.markdown(recommendations["recommendations"])
            except Exception as e:
                st.error(f"Error getting budget recommendations: {str(e)}")
    
    def run(self):
        menu_selection = self.render_sidebar()
        
        if menu_selection == "Dashboard":
            self.render_dashboard()
        elif menu_selection == "Add Expense":
            self.render_add_expense()
        elif menu_selection == "View Expenses":
            self.render_view_expenses()
        elif menu_selection == "Budget Management":
            self.render_budget_management()
        elif menu_selection == "AI Insights":
            self.render_ai_insights()

if __name__ == "__main__":
    app = ExpenseTracker()
    app.run() 