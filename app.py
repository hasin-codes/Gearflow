import streamlit as st
import json
import pandas as pd
from datetime import datetime
from io import BytesIO

# Custom theme and styling
st.set_page_config(page_title="GearFlow Ai", layout="wide")

# Custom CSS for modern UI with new color scheme
st.markdown("""

""", unsafe_allow_html=True)
def test_sqlite_connection():
    try:
        conn = sqlite3.connect('test.db')
        conn.close()
        return "SQLite connection successful!"
    except sqlite3.Error as e:
        return f"SQLite connection failed: {e}"
# Rest of your Python code remains the same
def json_to_excel(data):
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def generate_performance_report(data, selected_date):
    num_orders = len(data)
    total_revenue = num_orders * 650
    profit = total_revenue - (num_orders * 520)
    orders_needed_for_target = max(0, int((25000 - profit) / (650 - 520)) + 1)

    report = f"""Date: {selected_date}

Performance Report:
-------------------
Total Orders: {num_orders}
Expected Revenue: {total_revenue} BDT
Estimated Profit: {profit} BDT

To reach the target profit of 25,000 BDT:
Additional orders needed: {orders_needed_for_target}

Summary:
For {selected_date}, we received {num_orders} orders.

Operational Manager signing off."""

    return report

def main():
    st.title("🚚 GearFlow AI")
    st.subheader("A F1RST GEAR AI tool")

    # Initialize session state
    if 'report' not in st.session_state:
        st.session_state.report = ""

    # Date selector
    selected_date = st.date_input("Select submission date", datetime.now())

    # JSON input
    st.subheader("Enter Order Data")
    json_input = st.text_area("Paste your JSON data here", height=200)

    if st.button("Generate Report"):
        if json_input:
            try:
                json_data = json.loads(json_input)

                # Generate Excel
                excel_output = json_to_excel(json_data)
                st.download_button(
                    label="📥 Download Spreadsheet",
                    data=excel_output,
                    file_name=f"order_data_{selected_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                # Generate Performance Report
                st.session_state.report = generate_performance_report(json_data, selected_date)

                st.success("Performance Report generated successfully!")

            except json.JSONDecodeError:
                st.error("Invalid JSON data. Please check your input.")
        else:
            st.warning("Please enter JSON data.")

    # Display report if it exists
    if st.session_state.report:
        st.subheader("📊 Performance Report")
        st.markdown(f"```\n{st.session_state.report}\n```")

        # Instructions
        st.markdown("**Instructions:**")
        st.markdown("Send this generated text to Hasin & F1RST GEAR Messenger Group right now.")
        st.markdown("**Thank you for your hard work and dedication today. Your efforts are the driving force behind F1rst Gear's success. Please take this time to rest and recharge. You've earned it!\nGoodnight and rest well**.")
        st.markdown("**GearFlow AI**")

if __name__ == "__main__":
    main()