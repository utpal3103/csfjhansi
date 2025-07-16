import streamlit as st
import duckdb
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import os

# Always compute BASE_DIR relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "interim", "aggregation.duckdb")

def show():
    st.header("🏢 District Dashboard")
    
    # Create columns
    col1, col2 = st.columns(2)
    
    # Database connection
    con = duckdb.connect(DB_PATH)
    
    # Query data
    df = con.execute("""
        SELECT
          block_town,
          num_visits,
          num_schools
        FROM visit_distribution_by_block_town
        ORDER BY block_town, num_visits
    """).fetchdf()
    
    con.close()
    
    # Plot
    with col1:
        fig = px.line(
            df,
            x="num_visits",
            y="num_schools",
            color="block_town",
            markers=True,
            title="School Visit Frequency Distribution per Block"
        )
        fig.update_layout(
            xaxis_title="Number of Visits per School",
            yaxis_title="Number of Schools",
            hovermode="x unified"
        )
    
        st.plotly_chart(fig, use_container_width=True)
    con.close()

    # SECOND VISUALIZATION: Input Score Totals by Block and Quarter

    # connect to DuckDB
    con2 = duckdb.connect(DB_PATH)

    # Read pre-aggregated table
    sql = """
        SELECT
        block_town,
        quarter,
        num_records,
        total_positive,
        total_negative,
        total_unreported,

        ROUND(total_positive * 100.0 / (num_records * 5), 1) AS pct_positive,
        ROUND(total_negative * 100.0 / (num_records * 5), 1) AS pct_negative,
        ROUND(total_unreported * 100.0 / (num_records * 5), 1) AS pct_unreported

        FROM input_score_totals_by_block_quarter
        ORDER BY block_town, quarter;
    """

    df2 = con2.execute(sql).fetchdf()
    con2.close()

    # Melt to long format
    df2_melted = df2.melt(
        id_vars=["block_town", "quarter"],
        value_vars=["pct_positive", "pct_negative", "pct_unreported"],
        var_name="Score Type",
        value_name="Percentage"
    )

    # Clean the quarter labels
    df2_melted["quarter"] = df2_melted["quarter"].astype(str)

    # Create the visualization
    with col2:
        fig = px.bar(
            df2_melted,
            x="block_town",
            y="Percentage",
            color="Score Type",
            barmode="group",
            facet_row="quarter",
            category_orders={
                "quarter": sorted(df2_melted["quarter"].unique())
            },
            color_discrete_map={
                "pct_positive": "#1b9e77",   # Teal
                "pct_negative": "#d95f02",   # Coral
                "pct_unreported": "#e6ab02"  # Gold
            },
            labels={
                "block_town": "Block",
                "quarter": "Quarter"
            },
            title="Percentage of Input Scores by Block (Grouped by Quarter)"
        )

        fig.update_layout(
            height=900,
            xaxis_title="Blocks",
            yaxis_title="Percentage",
            bargap=0.2,
            showlegend=True
        )

        # Improve facet labels appearance
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        st.plotly_chart(fig, use_container_width=True)

    # THIRD VISUALIZATION: Attendance Summary by Block and Quarter  
    st.subheader("📈 Attendance, Enrollment, and Student-Teacher Ratio Trends")

    # Connect to DuckDB
    con3 = duckdb.connect(DB_PATH)

    # Query the table
    sql = """
        SELECT
            block_town,
            quarter,
            attendance_pct,
            student_teacher_ratio,
            avg_registered_students
        FROM attendance_summary_by_block_quarter
        ORDER BY block_town, quarter
    """
    df3 = con3.execute(sql).fetchdf()
    con3.close()

    # Create columns
    col1, col2 = st.columns(2)

    # Attendance %
    with col1:
        fig1 = px.line(
            df3,
            x="quarter",
            y="attendance_pct",
            color="block_town",
            markers=True,
            title="Attendance % Trend"
        )
        fig1.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Attendance %",
            legend_title="Block"
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Student-Teacher Ratio
    with col2:
        fig2 = px.line(
            df3,
            x="quarter",
            y="student_teacher_ratio",
            color="block_town",
            markers=True,
            title="Student-Teacher Ratio Trend"
        )
        fig2.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Students per Teacher",
            legend_title="Block"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Avg Registered Students
    with col1:
        fig3 = px.bar(
            df3,
            x="quarter",
            y="avg_registered_students",
            color="block_town",
            barmode="group",
            title="Average Registered Students"
        )
        fig3.update_layout(
            xaxis_title="Quarter",
            yaxis_title="Avg Registered Students",
            legend_title="Block"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # FOURTH VISUALIZATION: Teacher Performance Scores
    st.subheader("Teacher Performance Scores")
    st.subheader("📊 Teacher Performance Scores Heatmap")

    # Connect to aggregation DB
    con4 = duckdb.connect(DB_PATH)

    # Fetch the summarized data
    sql = """
        SELECT
        block_town,
        quarter,
            AVG(positive_score_prep_general) / 3.0 AS avg_general_pct,
            AVG(positive_score_prep_class) / 4.0 AS avg_class_pct,
            AVG(positive_score_interaction) / 5.0 AS avg_interaction_pct
        FROM teacher_performance_scores
        GROUP BY block_town, quarter
        ORDER BY block_town, quarter
    """
    df4 = con4.execute(sql).fetchdf()

    con4.close()

    # Melt to long format for heatmap
    df4_melted = df4.melt(
        id_vars=["block_town", "quarter"],
        value_vars=[
            "avg_general_pct",
            "avg_class_pct",
            "avg_interaction_pct"
        ],
        var_name="Metric",
        value_name="Score Percentage"
    )

    # Make Metric labels nicer
    metric_map = {
        "avg_general_pct": "Teacher Preparedness (General)",
        "avg_class_pct": "Preparedness for Class",
        "avg_interaction_pct": "Teacher-Student Interaction"
    }
    df4_melted["Metric"] = df4_melted["Metric"].map(metric_map)

    # Create the heatmap
    fig = px.density_heatmap(
        df4_melted,
        x="quarter",
        y="block_town",
        z="Score Percentage",
        facet_col="Metric",
        color_continuous_scale="YlGnBu",
        title="Average Teacher Performance Scores by Block and Quarter",
        nbinsx=len(df4_melted["quarter"].unique()),
        histfunc="avg"
    )
    fig.update_traces(
        zmax=1,
        zmin=0,
        hovertemplate='%{z:.0%} positive'
    )

    fig.update_layout(
        height=600,
        coloraxis_colorbar=dict(
            title="Score Percentage"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # FIFTH VISUALIZATION: Class Observation Scores
    st.subheader("Change in Class Observation Scores (Dumbbell Chart)")

    # Connect
    con = duckdb.connect("../data/interim/aggregation.duckdb")

    # Query data
    sql = """
    SELECT
        block_town,
        quarter,
        AVG(positive_count) AS avg_positive_score
    FROM class_observation_scores
    GROUP BY block_town, quarter
    ORDER BY block_town, quarter
    """
    df = con.execute(sql).fetchdf()
    con.close()

    # Ensure correct quarter ordering (if needed)
    # For example, if quarters are strings like 'Q1 2023', you might need to sort them properly

    # Prepare data for dumbbell
    # We pivot to get first and last quarter side by side
    pivot_df = (
        df.sort_values(["block_town", "quarter"])
        .groupby("block_town")
        .agg(first_score=("avg_positive_score", "first"),
            last_score=("avg_positive_score", "last"))
        .reset_index()
    )

    # Create figure
    fig = go.Figure()

    # Add lines and markers
    for idx, row in pivot_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["first_score"], row["last_score"]],
            y=[row["block_town"], row["block_town"]],
            mode="lines+markers",
            line=dict(color="gray", width=2),
            marker=dict(size=10),
            name=row["block_town"]
        ))

    fig.update_layout(
        title="Change in Average Positive Class Observation Scores (First vs Last Quarter)",
        xaxis_title="Average Positive Score",
        yaxis_title="Block",
        yaxis=dict(type="category"),
        height=500,
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)
