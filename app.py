import streamlit as st
import json
import pandas as pd
from datetime import datetime
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

# Custom theme and styling
st.set_page_config(page_title="GearFlow AI", layout="wide")

# Custom CSS for modern UI with new color scheme
st.markdown("""
<style>
body {
    background-color: #f0f2f6;
}
h1, h2, h3 {
    color: #333;
}
</style>
""", unsafe_allow_html=True)

def authenticate_google_sheets():
    try:
        # Use the credentials from Streamlit secrets
        credentials_dict = st.secrets["google_credentials"]
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ],
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Error authenticating with Google Sheets: {str(e)}")
        return None


def update_google_sheet(data, selected_date):
    client = authenticate_google_sheets()
    if not client:
        return False

    try:
        sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1zTSpmjkItId-4S1u-_RvLBu4jOT1c7YUwaa39AlpASE/edit?usp=sharing')
        
        worksheet_title = f"Orders_{selected_date.strftime('%Y%m%d_%H%M%S')}"
        
        new_worksheet = sheet.add_worksheet(title=worksheet_title, rows="100", cols="20")
        
        df = pd.DataFrame(data)
        
        new_worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        return True
    except Exception as e:
        st.error(f"Error updating Google Sheet: {str(e)}")
        return False

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

    if 'report' not in st.session_state:
        st.session_state.report = ""

    selected_date = st.date_input("Select submission date", datetime.now())

    st.subheader("Enter Order Data")
    json_input = st.text_area("Paste your JSON data here", height=200)

    if st.button("Generate Report"):
        if json_input:
            try:
                json_data = json.loads(json_input)

                excel_output = json_to_excel(json_data)
                st.download_button(
                    label="📥 Download Spreadsheet",
                    data=excel_output,
                    file_name=f"order_data_{selected_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                with st.spinner("Updating Google Sheet..."):
                    sheet_updated = update_google_sheet(json_data, selected_date)

                if sheet_updated:
                    st.success("Google Sheet updated successfully!")
                else:
                    st.warning("Failed to update Google Sheet. Please check the logs.")

                st.session_state.report = generate_performance_report(json_data, selected_date)

                st.success("Performance Report generated successfully!")

            except json.JSONDecodeError:
                st.error("Invalid JSON data. Please check your input.")
        else:
            st.warning("Please enter JSON data.")

    if st.session_state.report:
        st.subheader("📊 Performance Report")
        st.markdown(f"```\n{st.session_state.report}\n```")

        st.markdown("**Instructions:**")
        st.markdown("Send this generated text to Hasin & F1RST GEAR Messenger Group right now.")
        st.markdown("**Thank you for your hard work and dedication today. Your efforts are the driving force behind F1rst Gear's success. Please take this time to rest and recharge. You've earned it!\nGoodnight and rest well**.")
        st.markdown("**GearFlow AI**")

if __name__ == "__main__":
    main()
