import os
import streamlit as st
import google.generativeai as genai
import json
import base64

# Set the API key as an environment variable
os.environ["GEMINI_API_KEY"] = "AIzaSyBm9FxVS_FKmE3FohpVD1-5I1D43zvo8Tk"

# Configure the Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

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
    **Instruction:**

    Given the following messages:

    ```
    [05/07/2024 02:27] Ammu: Sir, kindly share these infos to place an order
    Name :Mamun 
    Phone Number :01866652777
    Delivery Address :ashi dag,Mirpur 13,dhaka
    Size & Quantity :L (1)
    Email (Optional) :sychomamunuae537k@gmail.com
    [05/07/2024 02:36] Ammu: Khandokar mim
    01849993495 
    Dhaka North Shahjahanpur Amtola moshjid goli 439no building 
    One redbull polo Size 4xl
    [05/07/2024 02:36] Ammu: Sir, kindly share these infos to place an order
    Name :Mamun 
    Phone Number :01866652777
    Delivery Address :ashi dag,Mirpur 13,dhaka
    Size & Quantity :L (1)
    Email (Optional) :sychomamunuae537k@gmail.com
    ```

    1. Remove the date and time, the text "Ammu", and any redundant information.
    2. Remove the email addresses.
    3. Sort the information by:
       - Name
       - Phone Number
       - Delivery Address
       - Size & Quantity (rename to Note in the output JSON)
    4. Format the information as a JSON object with the following fields:
       - Invoice (generate a 4-digit order number prefixed with "FGRB")
       - Name
       - Address
       - Phone
       - Amount (calculate based on the quantity: 1 unit = 650 taka, more than 1 unit = quantity * 650)
       - Note (size and quantity details)

    5. Generate a summary text listing the total quantities for each size in two columns.

    Filter out all unnecessary information, remove redundant entries, remove email addresses, and format the remaining information as a JSON object with the specified fields. Calculate the amount based on the quantity (1 unit = 650 taka, more than 1 unit = quantity * 650). Then generate a summary text listing the total quantities for each size and perform the financial calculations as shown in the example.
    """
)

# Function to create a download link for the JSON data
def get_download_link(json_data, filename="orders.json"):
    b64 = base64.b64encode(json_data.encode()).decode()
    return f'<a href="data:file/json;base64,{b64}" download="{filename}">Download JSON</a>'

# Streamlit app
st.title("Order Processing App")

# Text area for input
user_input = st.text_area("Enter order information:", height=200)

if st.button("Process Orders"):
    if user_input:
        with st.spinner("Processing orders..."):
            try:
                # Send message to the model
                response = model.generate_content(user_input)
                
                # Extract JSON and summary from the response
                json_start = response.text.find('[')
                json_end = response.text.rfind(']') + 1
                summary_start = response.text.rfind('```', json_end) + 4
                
                json_data = response.text[json_start:json_end]
                summary = response.text[summary_start:]
                
                # Display JSON data
                st.subheader("Processed Orders:")
                try:
                    orders = json.loads(json_data)
                    st.json(orders)  # Display the entire JSON
                    
                    # Create download link
                    st.markdown(get_download_link(json_data), unsafe_allow_html=True)
                except json.JSONDecodeError:
                    st.error("Error parsing JSON data")
                
                # Display summary
                st.subheader("Summary:")
                st.text(summary)

                st.success("Orders processed successfully!")
            except Exception as e:
                st.error(f"An error occurred while processing the orders: {str(e)}")
    else:
        st.warning("Please enter order information.")

# Add a note about usage
st.sidebar.info("Enter order information in the text area and click 'Process Orders' to generate the output and download option.")