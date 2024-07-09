import os
import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from datetime import datetime
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials
import base64

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
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 24px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 4px;
}
.stTextArea>div>div>textarea {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# Configure the Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2097152,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="""
    [Your existing system instruction here]
    """
)

def authenticate_google_sheets():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["google_credentials"],
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
        sheet = client.open_by_url(st.secrets["GOOGLE_SHEET_URL"])
        
        worksheet_title = f"Orders_{selected_date.strftime('%Y%m%d_%H%M%S')}"
        
        new_worksheet = sheet.add_worksheet(title=worksheet_title, rows="100", cols="20")
        
        df = pd.DataFrame(data)
        
        new_worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        
        return new_worksheet.url
    except Exception as e:
        st.error(f"Error updating Google Sheet: {str(e)}")
        return None

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

def get_download_link(json_data, filename="orders.json"):
    b64 = base64.b64encode(json_data.encode()).decode()
    return f'<a href="data:file/json;base64,{b64}" download="{filename}" class="stButton">Download JSON</a>'

def main():
    st.title("🚚 GearFlow AI")
    st.subheader("A F1RST GEAR AI tool")

    selected_date = st.date_input("Select submission date", datetime.now())

    st.subheader("Enter Order Data")
    user_input = st.text_area("Paste your order information here", height=200)

    if st.button("Process Orders and Generate Report", key="process_orders"):
        if user_input:
            with st.spinner("Processing orders and generating report..."):
                try:
                    # Generate JSON from text
                    response = model.generate_content(user_input)
                    
                    json_start = response.text.find('[')
                    json_end = response.text.rfind(']') + 1
                    summary_start = response.text.rfind('```', json_end) + 4
                    
                    json_data = response.text[json_start:json_end]
                    summary = response.text[summary_start:]
                    
                    st.subheader("Processed Orders:")
                    try:
                        orders = json.loads(json_data)
                        st.json(orders)
                        
                        st.markdown(get_download_link(json_data), unsafe_allow_html=True)
                    except json.JSONDecodeError:
                        st.error("Error parsing JSON data")
                        return
                    
                    st.subheader("Summary:")
                    st.text(summary)

                    # Generate report from JSON
                    excel_output = json_to_excel(orders)
                    st.download_button(
                        label="📥 Download Spreadsheet",
                        data=excel_output,
                        file_name=f"order_data_{selected_date}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    with st.spinner("Updating Google Sheet..."):
                        google_sheet_url = update_google_sheet(orders, selected_date)

                    if google_sheet_url:
                        st.success(f"Google Sheet updated successfully! You can see it [here]({google_sheet_url}).")
                    else:
                        st.warning("Failed to update Google Sheet. Please check the logs.")

                    performance_report = generate_performance_report(orders, selected_date)

                    st.subheader("📊 Performance Report")
                    st.markdown(f"```\n{performance_report}\n```")

                    st.markdown("**Instructions:**")
                    st.markdown("Send this generated text to Hasin & F1RST GEAR Messenger Group right now.")
                    st.markdown("**Thank you for your hard work and dedication today. Your efforts are the driving force behind F1rst Gear's success. Please take this time to rest and recharge. You've earned it!\nGoodnight and rest well**.")
                    st.markdown("**GearFlow AI**")

                    st.success("Orders processed and report generated successfully!")
                except Exception as e:
                    st.error(f"An error occurred while processing the orders and generating the report: {str(e)}")
        else:
            st.warning("Please enter order information.")

if __name__ == "__main__":
    main()
