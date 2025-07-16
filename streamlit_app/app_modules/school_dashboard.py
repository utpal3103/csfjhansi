# school_dashboard.py
import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from pathlib import Path

DB_PATH = Path("data/interim/aggregation.duckdb")

def show():
    st.header("🏫 School Dashboard")

    # Select or enter UDISC code
    con = duckdb.connect("DB_PATH")

    all_schools_df = con.execute("SELECT DISTINCT udise_code FROM school_identifiers_summary ORDER BY udise_code").fetchdf()
    udise_options = all_schools_df["udise_code"].tolist()

    selected_udise = st.selectbox("Select School UDISC Code:", udise_options)

    # Fetch identifiers and summary
    id_summary = con.execute(f"""
        SELECT * FROM school_identifiers_summary
        WHERE udise_code = '{selected_udise}'
    """).fetchdf().iloc[0]

    # Display identifiers
    st.subheader(f"{id_summary['school_name']} ({selected_udise})")
    st.write(f"**Block Town:** {id_summary['block_town']}")
    st.write(f"**District:** {id_summary['district_name']}")
    st.write(f"**Area Type:** {id_summary['area_type']}")

    # Display visit metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Visits", int(id_summary["total_visits"]))
    with col2:
        st.metric("Unique Mentors", int(id_summary["unique_mentors"]))

    st.markdown("---")

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        mentor_visits_df = con.execute(f"""
            SELECT mentor_name, mobile_number, visits
            FROM school_mentor_visits
            WHERE udise_code = '{selected_udise}'
            ORDER BY visits DESC
        """).fetchdf()

        st.subheader("Mentor Visits")
        st.dataframe(mentor_visits_df, use_container_width=True)

    with col2:
        visits_quarter_df = con.execute(f"""
            SELECT year, quarter, visits_in_quarter
            FROM school_visit_quarter_summary
            WHERE udise_code = '{selected_udise}'
            ORDER BY year, quarter
        """).fetchdf()

        st.subheader("Visits per Quarter")

        # Create a combined label for x-axis
        visits_quarter_df["period"] = visits_quarter_df["quarter"].astype(str)

        fig = px.bar(
            visits_quarter_df,
            x="period",
            y="visits_in_quarter",
            labels={"period": "Quarter", "visits_in_quarter": "Visits"},
            color_discrete_sequence=["#F58518"],  # Custom color (orange tone)
            title=""
        )
        fig.update_layout(showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    # Scores: Input Score
    # Input Score per quarter
    input_df = con.execute(f"""
        SELECT
            year,
            quarter,
            AVG(positive_score) AS avg_positive,
            AVG(negative_score) AS avg_negative,
            AVG(unreported_score) AS avg_unreported
        FROM input_score_aggregation
        WHERE udise_code = '{selected_udise}'
        GROUP BY year, quarter
        ORDER BY year, quarter
    """).fetchdf()

    # Combine year and quarter for x-axis
    input_df["period"] = input_df["quarter"].astype(str)

    # Melt to long format
    input_melted = input_df.melt(
        id_vars="period",
        value_vars=["avg_positive", "avg_negative", "avg_unreported"],
        var_name="Score Type",
        value_name="Average Score"
    )

    # Two columns
    col1, col2 = st.columns(2)

    with col1:
        # Bar Chart
        fig_input = px.bar(
            input_melted,
            x="period",
            y="Average Score",
            color="Score Type",
            barmode="group",
            color_discrete_map={
                "avg_positive": "green",
                "avg_negative": "red",
                "avg_unreported": "gray"
            },
            title="Input Scores by Quarter"
        )
        st.plotly_chart(fig_input, use_container_width=True)
    
    with col2:
        # Assuming you already have 'con' open and 'selected_udise' set

        ######################################
        # TEACHER PREPAREDNESS - GENERAL
        ######################################
        # Query
        teacher_prep_general_df = con.execute(f"""
            SELECT
                year,
                quarter,
                AVG(positive_score_prep_general) AS avg_positive,
                AVG(negative_score_prep_general) AS avg_negative,
                AVG(unreported_score_prep_general) AS avg_unreported
            FROM teacher_performance_scores
            WHERE udise_code = '{selected_udise}'
            GROUP BY year, quarter
            ORDER BY year, quarter
        """).fetchdf()

        # Prepare
        teacher_prep_general_df["period"] = teacher_prep_general_df["quarter"].astype(str)
        teacher_prep_general_melted = teacher_prep_general_df.melt(
            id_vars="period",
            value_vars=["avg_positive", "avg_negative", "avg_unreported"],
            var_name="Score Type",
            value_name="Average Score"
        )

        # Chart
        fig_teacher_prep_general = px.bar(
            teacher_prep_general_melted,
            x="period",
            y="Average Score",
            color="Score Type",
            barmode="group",
            color_discrete_map={
                "avg_positive": "#2ca02c",
                "avg_negative": "#d62728",
                "avg_unreported": "#7f7f7f"
            },
            title="Teacher Preparedness (General) by Quarter"
        )
        st.plotly_chart(fig_teacher_prep_general, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        ######################################
        # TEACHER PREPAREDNESS - FOR CLASS
        ######################################
        # Query
        teacher_prep_class_df = con.execute(f"""
            SELECT
                year,
                quarter,
                AVG(positive_score_prep_class) AS avg_positive,
                AVG(negative_score_prep_class) AS avg_negative,
                AVG(unreported_score_prep_class) AS avg_unreported
            FROM teacher_performance_scores
            WHERE udise_code = '{selected_udise}'
            GROUP BY year, quarter
            ORDER BY year, quarter
        """).fetchdf()

        teacher_prep_class_df["period"] = teacher_prep_class_df["quarter"].astype(str)
        teacher_prep_class_melted = teacher_prep_class_df.melt(
            id_vars="period",
            value_vars=["avg_positive", "avg_negative", "avg_unreported"],
            var_name="Score Type",
            value_name="Average Score"
        )

        fig_teacher_prep_class = px.bar(
            teacher_prep_class_melted,
            x="period",
            y="Average Score",
            color="Score Type",
            barmode="group",
            color_discrete_map={
                "avg_positive": "#1f77b4",
                "avg_negative": "#ff7f0e",
                "avg_unreported": "#7f7f7f"
            },
            title="Teacher Preparedness (Class) by Quarter"
        )
        st.plotly_chart(fig_teacher_prep_class, use_container_width=True)

    with col2:
        ######################################
        # TEACHER-STUDENT INTERACTION
        ######################################
        # Query
        teacher_interaction_df = con.execute(f"""
            SELECT
                year,
                quarter,
                AVG(positive_score_interaction) AS avg_positive,
                AVG(negative_score_interaction) AS avg_negative,
                AVG(unreported_score_interaction) AS avg_unreported
            FROM teacher_performance_scores
            WHERE udise_code = '{selected_udise}'
            GROUP BY year, quarter
            ORDER BY year, quarter
        """).fetchdf()

        teacher_interaction_df["period"] = teacher_interaction_df["quarter"].astype(str)
        teacher_interaction_melted = teacher_interaction_df.melt(
            id_vars="period",
            value_vars=["avg_positive", "avg_negative", "avg_unreported"],
            var_name="Score Type",
            value_name="Average Score"
        )

        fig_teacher_interaction = px.bar(
            teacher_interaction_melted,
            x="period",
            y="Average Score",
            color="Score Type",
            barmode="group",
            color_discrete_map={
                "avg_positive": "#17becf",
                "avg_negative": "#e377c2",
                "avg_unreported": "#7f7f7f"
            },
            title="Teacher-Student Interaction by Quarter"
        )
        st.plotly_chart(fig_teacher_interaction, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        #####################################
        # CLASS OBSERVATION SCORE
        #####################################
        # Query
        class_obs_df = con.execute(f"""
            SELECT
                year,
                quarter,
                AVG(positive_count) AS avg_positive,
                AVG(negative_count) AS avg_negative,
                AVG(unreported_count) AS avg_unreported
            FROM class_observation_scores
            WHERE udise_code = '{selected_udise}'
            GROUP BY year, quarter
            ORDER BY year, quarter
        """).fetchdf()

        class_obs_df["period"] = class_obs_df["quarter"].astype(str)
        class_obs_melted = class_obs_df.melt(
            id_vars="period",
            value_vars=["avg_positive", "avg_negative", "avg_unreported"],
            var_name="Score Type",
            value_name="Average Score"
        )

        fig_class_obs = px.bar(
            class_obs_melted,
            x="period",
            y="Average Score",
            color="Score Type",
            barmode="group",
            color_discrete_map={
                "avg_positive": "#9467bd",
                "avg_negative": "#bcbd22",
                "avg_unreported": "#7f7f7f"
            },
            title="Class Observation Scores by Quarter"
        )
        st.plotly_chart(fig_class_obs, use_container_width=True)

    con.close()