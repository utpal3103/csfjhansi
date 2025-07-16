# mentor_dashboard.py
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import os

# Always compute BASE_DIR relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "interim", "aggregation.duckdb")

def show():
    st.header("👨‍🏫 Mentor Dashboard")
    st.write(
        """
        Explore mentor-specific metrics, visit patterns, and engagement summaries.
        """
    )

    # Connect
    con = duckdb.connect(DB_PATH)

    # Mentor selection
    mentors_df = con.execute("""
        SELECT DISTINCT mentor_name, mobile_number
        FROM mentor_summary
        ORDER BY mentor_name
    """).fetchdf()

    mentor_options = mentors_df["mentor_name"].tolist()
    selected_mentor = st.selectbox("Select Mentor", mentor_options)

    selected_mobile = mentors_df.loc[
        mentors_df["mentor_name"] == selected_mentor, "mobile_number"
    ].values[0]

    st.markdown("---")

    # Summary metrics
    summary_row = con.execute(f"""
        SELECT *
        FROM mentor_summary
        WHERE mentor_name = '{selected_mentor}'
    """).fetchdf().iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Visits", int(summary_row["total_visits"]))
        st.metric("Unique Schools Visited", int(summary_row["unique_schools_visited"]))
        st.metric("Unique Blocks Visited", int(summary_row["unique_blocks_visited"]))
    with col2:
        st.metric("First Visit Date", str(summary_row["first_visit_date"].date()))
        st.metric("Last Visit Date", str(summary_row["last_visit_date"].date()))
        st.metric("Average Visits per Month", float(summary_row["avg_visits_per_month"]))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        # Visits per quarter
        quarter_df = con.execute(f"""
        SELECT year, quarter, visits_in_quarter
        FROM mentor_visits_per_quarter
        WHERE mentor_name = '{selected_mentor}'
        ORDER BY year, quarter
        """).fetchdf()

        # Convert year to string to force categorical coloring
        quarter_df["year"] = quarter_df["year"].astype(str)

        fig_quarter = px.bar(
            quarter_df,
            x="quarter",
            y="visits_in_quarter",
            color="year",
            barmode="group",
            labels={"visits_in_quarter": "Visits", "year": "Year"},
            title="Visits per Quarter"
        )
        st.plotly_chart(fig_quarter, use_container_width=True)

    with col2:
        # Monthly timeline
        monthly_df = con.execute(f"""
        SELECT year_month, visits_in_month
        FROM mentor_visits_per_month
        WHERE mentor_name = '{selected_mentor}'
        ORDER BY year_month
        """).fetchdf()

        fig_months = px.line(
            monthly_df,
            x="year_month",
            y="visits_in_month",
            markers=True,
            labels={"year_month": "Month", "visits_in_month": "Visits"},
            title="Monthly Visit Timeline"
        )
        st.plotly_chart(fig_months, use_container_width=True)

    con.close()