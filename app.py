import time

import streamlit as st

from lemmo_app import lemmo_app

if not st.session_state.get("logged_in"):
    st.title("Login")

    # login form to get the password
    password = st.text_input("Passwort", type="password")

    # check if the password is correct
    if password == st.secrets["PASSWORD"]:
        st.success("Erfolgreich eingeloggt!")
        st.session_state["logged_in"] = True
        time.sleep(1)
        st.rerun()
    elif password:
        st.error("Falsches Passwort!")
else:
    lemmo_app()
