# main_app.py
import streamlit as st

# Import page modules
from app_modules import (
    home,
    district_dashboard,
    mentor_dashboard,
    school_dashboard
)

# App title and config
st.set_page_config(page_title="JHANSI District Monitoring", layout="wide")
st.title("📊 JHANSI District Monitoring")

# Sidebar menu
menu = [
    "JHANSI - Overview",
    "District Dashboard",
    "Mentor Dashboard",
    "School Dashboard"
]

choice = st.sidebar.radio("📂 Select a Dashboard", menu)

# Page router
if choice == "JHANSI - Overview":
    home.show()
elif choice == "District Dashboard":
    district_dashboard.show()
elif choice == "Mentor Dashboard":
    mentor_dashboard.show()
elif choice == "School Dashboard":
    school_dashboard.show()
else:
    st.write("Please select a dashboard from the menu.")

# Footer
st.markdown("---")
st.caption("Developed by Utpal Sinha • v0.1")