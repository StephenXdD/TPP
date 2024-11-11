# filter_logic.py

import sqlite3 as s3

def connect_to_db(db_name='past_papers.db'):
    """Establish a connection to the SQLite database."""
    try:
        conn = s3.connect(db_name)
        return conn
    except s3.Error as e:
        raise Exception(f"Database connection error: {e}")

def get_subjects(conn):
    """Retrieve distinct subjects from the database."""
    subjects_query = "SELECT DISTINCT Subject_name FROM past_papers"
    c = conn.cursor()
    c.execute(subjects_query)
    subjects = c.fetchall()
    return [subject[0] for subject in subjects]

def get_topics(conn, selected_subject):
    """Fetch topics for the chosen subject."""
    topic_query = "SELECT DISTINCT topic FROM past_papers WHERE Subject_name = ?"
    c = conn.cursor()
    c.execute(topic_query, (selected_subject,))
    topics_data = c.fetchall()
    return sorted(set(row[0] for row in topics_data if row[0] is not None))

def get_subtopics(conn, selected_subject, selected_topics):
    """Fetch subtopics based on selected topics."""
    subtopic_query = "SELECT DISTINCT sub_topic FROM past_papers WHERE Subject_name = ? AND topic IN ({})".format(','.join('?' * len(selected_topics)))
    c = conn.cursor()
    c.execute(subtopic_query, (selected_subject, *selected_topics))
    subtopics_data = c.fetchall()
    return sorted(set(row[0] for row in subtopics_data if row[0] is not None))

def get_years(conn, selected_subject, selected_topics, selected_subtopics):
    """Fetch years based on selected topics and subtopics."""
    year_query = "SELECT DISTINCT Year FROM past_papers WHERE Subject_name = ? AND topic IN ({}) {}".format(','.join('?' * len(selected_topics)), "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
    c = conn.cursor()
    params = [selected_subject] + selected_topics + (selected_subtopics if selected_subtopics else [])
    c.execute(year_query, params)
    years_data = c.fetchall()
    return sorted(set(row[0] for row in years_data))

def get_variants(conn, selected_subject, selected_years, selected_topics, selected_subtopics):
    """Fetch variants based on selected years, topics, and subtopics."""
    variant_query = "SELECT DISTINCT Variant FROM past_papers WHERE Subject_name = ? AND Year IN ({}) AND topic IN ({}) {}".format(','.join('?' * len(selected_years)), ','.join('?' * len(selected_topics)), "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
    c = conn.cursor()
    params = [selected_subject] + selected_years + selected_topics + (selected_subtopics if selected_subtopics else [])
    c.execute(variant_query, params)
    variants_data = c.fetchall()
    return sorted(set(row[0] for row in variants_data))

def get_paper_numbers(conn, selected_subject, selected_years, selected_variants, selected_topics, selected_subtopics):
    """Fetch paper numbers based on selected years, variants, topics, and subtopics."""
    paper_number_query = "SELECT DISTINCT paper_number FROM past_papers WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND topic IN ({}) {}".format(','.join('?' * len(selected_years)), ','.join('?' * len(selected_variants)), ','.join('?' * len(selected_topics)), "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
    c = conn.cursor()
    params = [selected_subject] + selected_years + selected_variants + selected_topics + (selected_subtopics if selected_subtopics else [])
    c.execute(paper_number_query, params)
    paper_numbers_data = c.fetchall()
    return sorted(set(row[0] for row in paper_numbers_data))

def get_paper_variants(conn, selected_subject, selected_years, selected_variants, selected_paper_numbers, selected_topics, selected_subtopics):
    """Fetch paper variants based on selected years, variants, paper numbers, topics, and subtopics."""
    paper_variant_query = "SELECT DISTINCT paper_variant FROM past_papers WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND paper_number IN ({}) AND topic IN ({}) {}".format(','.join('?' * len(selected_years)), ','.join('?' * len(selected_variants)), ','.join('?' * len(selected_paper_numbers)), ','.join('?' * len(selected_topics)), "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
    c = conn.cursor()
    params = [selected_subject] + selected_years + selected_variants + selected_paper_numbers + selected_topics + (selected_subtopics if selected_subtopics else [])
    c.execute(paper_variant_query, params)
    paper_variants_data = c.fetchall()
    return sorted(set(row[0] for row in paper_variants_data))

def get_difficulties(conn, selected_subject, selected_years, selected_variants, selected_paper_numbers, selected_paper_variants, selected_topics, selected_subtopics):
    """Fetch difficulties based on all previous selections."""
    difficulty_query = "SELECT DISTINCT Difficulty FROM past_papers WHERE Subject_name = ? AND Year IN ({}) AND Variant IN ({}) AND paper_number IN ({}) AND paper_variant IN ({}) AND topic IN ({}) {}".format(','.join('?' * len(selected_years)), ','.join('?' * len(selected_variants)), ','.join('?' * len(selected_paper_numbers)), ','.join('?' * len(selected_paper_variants)), ','.join('?' * len(selected_topics)), "AND sub_topic IN ({})".format(','.join('?' * len(selected_subtopics))) if selected_subtopics else "")
    c = conn.cursor()
    params = [selected_subject] + selected_years + selected_variants + selected_paper_numbers + selected_paper_variants + selected_topics + (selected_subtopics if selected_subtopics else [])
    c.execute(difficulty_query, params)
    difficulties_data = c.fetchall()
    return sorted(set(row[0] for row in difficulties_data))

def filter_papers(conn, subject, years, variants, difficulties, topics, subtopics, paper_numbers, paper_variants):
    """Filters the past papers database table based on the selected criteria."""
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
    
    c = conn.cursor()
    result = c.execute(query, params).fetchall()
    return result
