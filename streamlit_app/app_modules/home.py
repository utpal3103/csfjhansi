# home.py
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

# Always compute BASE_DIR relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "interim", "aggregation.duckdb")

def show():
    st.subheader("Key Indicators")
    st.write(
        """
        This page shows a summary of data collected across the district, including key statistics,
        visit distributions, and mentor activity.
        """
    )

    # Connect
    con = duckdb.connect(DB_PATH)

    # Key summary
    # Load a single-row DataFrame
    summary_df = con.execute("SELECT * FROM home_summary_table").fetchdf()

    # Extract the row as a dict
    summary_row = summary_df.iloc[0]

    # Create columns
    col1, col2 = st.columns(2)

    # Use your own labels
    with col1:
        st.metric("Total School Visits", int(summary_row["total_visits"]))
        st.metric("Data Start Date", str(summary_row["earliest_date"].date()))
        st.metric("Data End Date", str(summary_row["latest_date"].date()))
        st.metric("Number of Quarters", int(summary_row["unique_quarters"]))
        st.metric("Number of Months", int(summary_row["unique_months"]))
        
    with col2:
        st.metric("Number of Blocks", int(summary_row["unique_blocks"]))
        st.metric("Number of Schools", int(summary_row["unique_schools"]))
        st.metric("Number of Mentors", int(summary_row["unique_mentors"]))
        st.metric("Average Visits per Mentor", float(summary_row["avg_visits_per_mentor"]))
        st.metric("Average Visits per School", float(summary_row["avg_visits_per_school"]))

    st.markdown("---")

    # Visits across blocks
    visits_df = con.execute("""
        SELECT block_town, total_visits
        FROM mentor_block_visits_table
        ORDER BY total_visits DESC
    """).fetchdf()

    mentors_df = con.execute("""
        SELECT block_town, unique_mentors
        FROM mentor_block_unique_mentors
        ORDER BY unique_mentors DESC
    """).fetchdf()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Visits Across Blocks")
        fig_visits = px.bar(
            visits_df,
            x="block_town",
            y="total_visits",
            color_discrete_sequence=["#4C78A8"],  # e.g., blue tone
            labels={"block_town": "Block", "total_visits": "Total Visits"},
            title=""
        )
        fig_visits.update_layout(showlegend=False)
        st.plotly_chart(fig_visits, use_container_width=True)

    with col2:
        st.subheader("Unique Mentors Per Block")
        fig_mentors = px.bar(
            mentors_df,
            x="block_town",
            y="unique_mentors",
            color_discrete_sequence=["#F58518"],  # e.g., orange tone
            labels={"block_town": "Block", "unique_mentors": "Unique Mentors"},
            title=""
        )
        fig_mentors.update_layout(showlegend=False)
        st.plotly_chart(fig_mentors, use_container_width=True)

    st.markdown("---")

    # Top/least active mentors
    top_mentors_df = con.execute("SELECT * FROM top_three_active_mentors").fetchdf()
    least_mentors_df = con.execute("SELECT * FROM bottom_three_active_mentors").fetchdf()

    st.subheader("Mentor Activity")
    col3, col4 = st.columns(2)
    with col3:
        st.write("**Most Active Mentors**")
        st.dataframe(top_mentors_df, use_container_width=True)
    with col4:
        st.write("**Least Active Mentors**")
        st.dataframe(least_mentors_df, use_container_width=True)

    st.markdown("---")

    # Top/least visited schools
    top_schools_df = con.execute("SELECT * FROM top_three_visited_schools").fetchdf()
    least_schools_df = con.execute("SELECT * FROM bottom_three_visited_schools").fetchdf()

    st.subheader("School Visit Frequency")
    col5, col6 = st.columns(2)
    with col5:
        st.write("**Most Visited Schools**")
        st.dataframe(top_schools_df, use_container_width=True)
    with col6:
        st.write("**Least Visited Schools**")
        st.dataframe(least_schools_df, use_container_width=True)

    con.close()