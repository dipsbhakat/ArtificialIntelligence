import streamlit as st

st.title("🟢 Hello Azure!")
st.success("If you can see this, Streamlit is working on Azure App Service!")
st.write("Current working directory:", st.session_state.get('cwd', 'Unknown'))

import os
st.write("Environment variables:")
for key, value in os.environ.items():
    if 'AZURE' in key:
        st.write(f"- {key}: {value[:10]}..." if len(value) > 10 else f"- {key}: {value}")
