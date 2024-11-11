# Importing required libraries
import streamlit as st
import sqlite3 as s3

# Establishing a connection to the SQLite database
try:
    conn = s3.connect('past_papers.db')
    c = conn.cursor()
except s3.Error as e:
    st.error(f"Database connection error: {e}")

# Query to retrieve distinct subjects for selection
subjects_query = "SELECT DISTINCT Subject_name FROM past_papers"
c.execute(subjects_query)
subjects = c.fetchall()
subject_list = [subject[0] for subject in subjects]  # Convert tuples to a list of subjects

# Subject selection
selected_subject = st.radio("Select Subject:", subject_list)

# Initialize lists for the selections
selected_topics = []
selected_subtopics = []
selected_years = []
selected_variants = []
selected_paper_numbers = []
selected_paper_variants = []
selected_difficulties = []

# Dynamically fetching related data based on selected subject
if selected_subject:
    # Fetch topics for the chosen subject
    topic_query = """
        SELECT DISTINCT topic 
        FROM past_papers 
        WHERE Subject_name = ?
    """
    c.execute(topic_query, (selected_subject,))
    topics_data = c.fetchall()
    topic_list = sorted(set(row[0] for row in topics_data if row[0] is not None))

    # Topic selection
    selected_topics = st.multiselect("Select Topic(s):", topic_list)

    if selected_topics:
        # Fetch subtopics based on selected topics
        subtopic_query = """
            SELECT DISTINCT sub_topic 
            FROM past_papers 
            WHERE Subject_name = ? AND topic IN ({})
        """.format(','.join('?' * len(selected_topics)))
        c.execute(subtopic_query, (selected_subject, *selected_topics))
        subtopics_data = c.fetchall()
        subtopic_list = sorted(set(row[0] for row in subtopics_data if row[0] is not None))

        # Only show the subtopic multiselect box if there are available subtopics
        if subtopic_list:
            selected_subtopics = st.multiselect("Select Subtopic(s):", subtopic_list)
        else:
            st.warning("No subtopics available for the selected topics.")

        # Proceed to fetch years only if topics are selected
        year_query = """
            SELECT DISTINCT Year 
            FROM past_papers 
            WHERE Subject_name = ? AND topic IN ({}) {}
        """.format(','.join('?' * len(selected_topics)), 
                   "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
        
        params = [selected_subject] + selected_topics + (selected_subtopics if selected_subtopics else [])
        c.execute(year_query, params)
        years_data = c.fetchall()
        year_list = sorted(set(row[0] for row in years_data))

        # Year selection only if topics are selected
        selected_years = st.multiselect("Select Year(s):", year_list)

    if selected_years:
        # Fetch variants after year selection
        variant_query = """
            SELECT DISTINCT Variant 
            FROM past_papers 
            WHERE Subject_name = ? AND Year IN ({}) AND topic IN ({}) {}
        """.format(','.join('?' * len(selected_years)), 
                   ','.join('?' * len(selected_topics)), 
                   "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
        
        params = [selected_subject] + selected_years + selected_topics + (selected_subtopics if selected_subtopics else [])
        c.execute(variant_query, params)
        variants_data = c.fetchall()
        variant_list = sorted(set(row[0] for row in variants_data))

        # Variant selection
        selected_variants = st.multiselect("Select Variant(s):", variant_list)

    if selected_variants:
        # Fetch paper numbers after variant selection
        paper_number_query = """
            SELECT DISTINCT paper_number 
            FROM past_papers 
            WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND topic IN ({}) {}
        """.format(','.join('?' * len(selected_years)), 
                   ','.join('?' * len(selected_variants)), 
                   ','.join('?' * len(selected_topics)), 
                   "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
        
        params = [selected_subject] + selected_years + selected_variants + selected_topics + (selected_subtopics if selected_subtopics else [])
        c.execute(paper_number_query, params)
        paper_numbers_data = c.fetchall()
        paper_number_list = sorted(set(row[0] for row in paper_numbers_data))

        # Paper number selection
        selected_paper_numbers = st.multiselect("Select Paper Number(s):", paper_number_list)

    if selected_paper_numbers:
        # Fetch paper variants after paper number selection
        paper_variant_query = """
            SELECT DISTINCT paper_variant 
            FROM past_papers 
            WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND paper_number IN ({}) AND topic IN ({}) {}
        """.format(','.join('?' * len(selected_years)), 
                   ','.join('?' * len(selected_variants)), 
                   ','.join('?' * len(selected_paper_numbers)), 
                   ','.join('?' * len(selected_topics)), 
                   "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
        
        params = [selected_subject] + selected_years + selected_variants + selected_paper_numbers + selected_topics + (selected_subtopics if selected_subtopics else [])
        c.execute(paper_variant_query, params)
        paper_variants_data = c.fetchall()
        paper_variant_list = sorted(set(row[0] for row in paper_variants_data))

        # Paper variant selection
        selected_paper_variants = st.multiselect("Select Paper Variant(s):", paper_variant_list)

    # Fetch difficulties after all previous selections
    if selected_paper_variants:
        difficulty_query = """
            SELECT DISTINCT Difficulty 
            FROM past_papers 
            WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND paper_number IN ({}) AND paper_variant IN ({}) AND topic IN ({}) {}
        """.format(','.join('?' * len(selected_years)), 
                   ','.join('?' * len(selected_variants)), 
                   ','.join('?' * len(selected_paper_numbers)), 
                   ','.join('?' * len(selected_paper_variants)), 
                   ','.join('?' * len(selected_topics)), 
                   "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
        
        params = [selected_subject] + selected_years + selected_variants + selected_paper_numbers + selected_paper_variants + selected_topics + (selected_subtopics if selected_subtopics else [])
        c.execute(difficulty_query, params)
        difficulties_data = c.fetchall()
        difficulty_list = sorted(set(row[0] for row in difficulties_data))

        # Difficulty selection
        selected_difficulties = st.multiselect("Select Difficulty(ies):", difficulty_list)

# Function to filter past papers based on the user's selections
def filter_papers(subject, years, variants, difficulties, topics, subtopics, paper_numbers, paper_variants):
    """
    Filters the past papers database table based on the selected subject, years, variants, difficulties,
    topics, subtopics, paper numbers, and paper variants.
    """
    query_parts = ["Subject_name = ?"]
    params = [subject]
    
    if years:
        query_parts.append("Year IN ({})".format(','.join('?' * len(years))))
        params.extend(years)
        
    if variants:
        query_parts.append("Variant IN ({})".format(','.join('?' * len(variants))))
        params.extend(variants)

    if difficulties:
        query_parts.append("Difficulty IN ({})".format(','.join('?' * len(difficulties))))
        params.extend(difficulties)

    if topics:
        query_parts.append("topic IN ({})".format(','.join('?' * len(topics))))
        params.extend(topics)

    if subtopics:
        query_parts.append("sub_topic IN ({})".format(','.join('?' * len(subtopics))))
        params.extend(subtopics)

    if paper_numbers:
        query_parts.append("paper_number IN ({})".format(','.join('?' * len(paper_numbers))))
        params.extend(paper_numbers)

    if paper_variants:
        query_parts.append("paper_variant IN ({})".format(','.join('?' * len(paper_variants))))
        params.extend(paper_variants)

    query = "SELECT * FROM past_papers WHERE " + " AND ".join(query_parts)
    
    result = c.execute(query, params).fetchall()
    return result

# Displaying data using Streamlit
if st.button("Click to generate Papers"):
    filtered_data = filter_papers(selected_subject, selected_years, selected_variants, selected_difficulties, selected_topics, selected_subtopics, selected_paper_numbers, selected_paper_variants)

    if filtered_data:
        st.write("Filtered Past Papers:")
        for row in filtered_data:
            st.write(row)
    else:
        st.write("No papers found with the selected filters.")

# Close the database connection
conn.close()
