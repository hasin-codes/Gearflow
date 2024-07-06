import subprocess
import os

# Set the Streamlit configuration to serve on all available IP addresses
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = os.getenv("PORT", "8501")

# Start the Streamlit app
subprocess.run(["streamlit", "run", "app.py"])
