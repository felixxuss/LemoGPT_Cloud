import streamlit as st

from agent import LemoAgent


def lemmo_app():
    st.title("LemoGPT")

    # Add a sidebar for model selection
    model = st.sidebar.radio("Wähle ein Modell:", ("gpt-4o-mini", "gpt-4o"))

    col1_1, col1_2 = st.columns(2)
    start_year = col1_1.number_input(
        "Start Jahr", min_value=1900, max_value=2017, value=2000
    )
    end_year = col1_2.number_input(
        "End Jahr", min_value=1900, max_value=2017, value=2000
    )

    question = st.text_input("Frage", "")

    current_year = 0
    total_steps = end_year - start_year + 2
    col2_1, inter, col2_2 = st.columns((3, 8, 4))
    if col2_1.button("Los geht's!"):
        # get the agent with selected model
        agent = LemoAgent(model, start_year, end_year)

        progress_text = st.empty()
        progress_bar = st.progress(0)

        # collect information over the years
        current_year += 1
        progress_bar.progress(current_year / total_steps)
        for year in agent.get_context(question):
            current_year += 1
            progress_bar.progress(current_year / total_steps)
            progress_text.text(f"Verarbeite den Inhalt aus dem Jahr {year}...")

        # summarize the collected information
        answer, price = agent.query(question)  # returns price in cent

        # answer, price = "Test Antwort", 1.0

        # show the answer and the price
        st.text_area("Zusammenfassung", answer, height=350)
        col2_2.write(f"\tGeschätzter Preis: {price*0.91:.2f} Cent")

        # save the answer and informations to a file
        content, file_name = agent.format_save_content(question, answer, price)
        st.download_button(
            label="Antwort downloaden", data=content, file_name=file_name
        )
