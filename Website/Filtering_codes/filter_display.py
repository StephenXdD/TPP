# filter_display.py

import streamlit as st
from filter_logic import (
    connect_to_db, get_subjects, get_topics, get_subtopics, 
    get_years, get_variants, get_paper_numbers, get_paper_variants,
    get_difficulties, filter_papers
)

# Establish database connection
conn = connect_to_db()

# Get subjects
subject_list = get_subjects(conn)

# Subject selection
selected_subject = st.radio("Select Subject:", subject_list)

# Initialize selections
selected_topics = []
selected_subtopics = []
selected_years = []
selected_variants = []
selected_paper_numbers = []
selected_paper_variants = []
selected_difficulties = []

# Fetch related data based on selected subject
if selected_subject:
    # Fetch topics for the chosen subject
    selected_topics = get_topics(conn, selected_subject)
    selected_topics = st.multiselect("Select Topic(s):", selected_topics)

    if selected_topics:
        # Fetch subtopics based on selected topics
        selected_subtopics = get_subtopics(conn, selected_subject, selected_topics)
        if selected_subtopics:
            selected_subtopics = st.multiselect("Select Subtopic(s):", selected_subtopics)

        # Fetch years after topic and optional subtopic selection
        selected_years = get_years(conn, selected_subject, selected_topics, selected_subtopics)
        if selected_years:
            selected_years = st.multiselect("Select Year(s):", selected_years)

            if selected_years:
                # Fetch variants after year selection
                selected_variants = get_variants(conn, selected_subject, selected_years, selected_topics, selected_subtopics)
                if selected_variants:
                    selected_variants = st.multiselect("Select Variant(s):", selected_variants)

                    if selected_variants:
                        # Fetch paper numbers after variant selection
                        selected_paper_numbers = get_paper_numbers(conn, selected_subject, selected_years, selected_variants, selected_topics, selected_subtopics)
                        if selected_paper_numbers:
                            selected_paper_numbers = st.multiselect("Select Paper Number(s):", selected_paper_numbers)

                            if selected_paper_numbers:
                                # Fetch paper variants after paper number selection
                                selected_paper_variants = get_paper_variants(conn, selected_subject, selected_years, selected_variants, selected_paper_numbers, selected_topics, selected_subtopics)
                                if selected_paper_variants:
                                    selected_paper_variants = st.multiselect("Select Paper Variant(s):", selected_paper_variants)

                                    # Fetch difficulties after all previous selections
                                    selected_difficulties = get_difficulties(conn, selected_subject, selected_years, selected_variants, selected_paper_numbers, selected_paper_variants, selected_topics, selected_subtopics)
                                    if selected_difficulties:
                                        selected_difficulties = st.multiselect("Select Difficulty(ies):", selected_difficulties)

# Display filtered papers
if st.button("Click to generate Papers"):
    filtered_data = filter_papers(conn, selected_subject, selected_years, selected_variants, selected_difficulties, selected_topics, selected_subtopics, selected_paper_numbers, selected_paper_variants)

    if filtered_data:
        st.write("Filtered Past Papers:")
        for row in filtered_data:
            st.write(row)
    else:
        st.write("No papers found with the selected filters.")

# Close the database connection
conn.close()
