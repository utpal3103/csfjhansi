VISITS_BY_SCHOOL_SUBJECT_QUARTER = """
    SELECT
        udise_code,
        observed_class,
        observed_subject,
        year,
        quarter,
        COUNT(*) AS num_visits
    FROM data_db.ss_data
    GROUP BY
        udise_code,
        observed_class,
        observed_subject,
        year,
        quarter
    ORDER BY
        udise_code,
        observed_class,
        observed_subject,
        year,
        quarter
"""

VISITS_BY_MENTOR_QUARTER = """
    SELECT
        mentor_name,
        year,
        quarter,
        COUNT(*) AS num_visits
    FROM data_db.ss_data
    GROUP BY
        mentor_name,
        year,
        quarter
    ORDER BY
        mentor_name,
        year,
        quarter
"""

VISITS_BY_DISTRICT_BLOCK = """
    SELECT
        district_name,
        block_town,
        year,
        quarter,
        COUNT(*) AS num_visits
    FROM data_db.ss_data
    GROUP BY
        district_name,
        block_town,
        year,
        quarter
    ORDER BY
        district_name,
        block_town,
        year,
        quarter
"""

INPUT_SCORE_AGGREGATION = """
    SELECT
    district_name,
    block_town,
    udise_code,
    year,
    quarter,
    month,
    COUNT(*) AS total_visits,

    -- Positive Score
    SUM(CASE WHEN bluetooth_speaker_sentiment = 'positive' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN library_reading_corner_usage_sentiment = 'positive' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN sports_equipment_usage_sentiment = 'positive' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN multiple_classes_in_same_room = 'नहीं' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN class1_school_readiness_calendar_availability = 'हाँ' THEN 1 ELSE 0 END)
    AS positive_score,

    -- Negative Score
    SUM(CASE WHEN bluetooth_speaker_sentiment = 'negative' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN library_reading_corner_usage_sentiment = 'negative' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN sports_equipment_usage_sentiment = 'negative' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN multiple_classes_in_same_room = 'हाँ' THEN 1 ELSE 0 END) +
    SUM(CASE WHEN class1_school_readiness_calendar_availability = 'नहीं' THEN 1 ELSE 0 END)
    AS negative_score,

    -- Unreported Score: catch NULL, 'nan', 'unknown', '', 'N/A', 'NA', 'None'
    SUM(CASE WHEN bluetooth_speaker_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR bluetooth_speaker_sentiment IS NULL THEN 1 ELSE 0 END) +
    SUM(CASE WHEN library_reading_corner_usage_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR library_reading_corner_usage_sentiment IS NULL THEN 1 ELSE 0 END) +
    SUM(CASE WHEN sports_equipment_usage_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR sports_equipment_usage_sentiment IS NULL THEN 1 ELSE 0 END) +
    SUM(CASE WHEN multiple_classes_in_same_room IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR multiple_classes_in_same_room IS NULL THEN 1 ELSE 0 END) +
    SUM(CASE WHEN class1_school_readiness_calendar_availability IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR class1_school_readiness_calendar_availability IS NULL THEN 1 ELSE 0 END)
    AS unreported_score

    FROM data_db.ss_data
    GROUP BY
    district_name,
    block_town,
    udise_code,
    year,
    quarter,
    month
    ORDER BY
    district_name,
    block_town,
    udise_code,
    year,
    quarter,
    month
"""

VISIT_DISTRIBUTION_BY_BLOCK_TOWN = """
    SELECT
    block_town,
    visit_counts.num_visits,
    COUNT(*) AS num_schools
    FROM (
    SELECT
        block_town,
        udise_code,
        COUNT(*) AS num_visits
    FROM data_db.ss_data
    GROUP BY block_town, udise_code
    ) AS visit_counts
    GROUP BY block_town, visit_counts.num_visits
    ORDER BY block_town, visit_counts.num_visits;
"""

INPUT_SCORE_SUMMARY_BY_BLOCK_QUARTER = """
    SELECT
    district_name,
    block_town,
    quarter,
    AVG(positive_score) AS avg_positive_score,
    AVG(negative_score) AS avg_negative_score,
    AVG(unreported_score) AS avg_unreported_score
    FROM input_score_aggregation
    GROUP BY district_name, block_town, quarter
    ORDER BY block_town, quarter
"""

INPUT_SCORE_TOTALS_BY_BLOCK_QUARTER= """
    SELECT
    block_town,
    quarter,
    COUNT(*) AS num_records,

    SUM(
    (CASE WHEN bluetooth_speaker_sentiment = 'positive' THEN 1 ELSE 0 END) +
    (CASE WHEN library_reading_corner_usage_sentiment = 'positive' THEN 1 ELSE 0 END) +
    (CASE WHEN sports_equipment_usage_sentiment = 'positive' THEN 1 ELSE 0 END) +
    (CASE WHEN multiple_classes_in_same_room = 'नहीं' THEN 1 ELSE 0 END) +
    (CASE WHEN class1_school_readiness_calendar_availability = 'हाँ' THEN 1 ELSE 0 END)
    ) AS total_positive,

    SUM(
    (CASE WHEN bluetooth_speaker_sentiment = 'negative' THEN 1 ELSE 0 END) +
    (CASE WHEN library_reading_corner_usage_sentiment = 'negative' THEN 1 ELSE 0 END) +
    (CASE WHEN sports_equipment_usage_sentiment = 'negative' THEN 1 ELSE 0 END) +
    (CASE WHEN multiple_classes_in_same_room = 'हाँ' THEN 1 ELSE 0 END) +
    (CASE WHEN class1_school_readiness_calendar_availability = 'नहीं' THEN 1 ELSE 0 END)
    ) AS total_negative,

    SUM(
    (CASE WHEN bluetooth_speaker_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR bluetooth_speaker_sentiment IS NULL THEN 1 ELSE 0 END) +
    (CASE WHEN library_reading_corner_usage_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR library_reading_corner_usage_sentiment IS NULL THEN 1 ELSE 0 END) +
    (CASE WHEN sports_equipment_usage_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR sports_equipment_usage_sentiment IS NULL THEN 1 ELSE 0 END) +
    (CASE WHEN multiple_classes_in_same_room IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR multiple_classes_in_same_room IS NULL THEN 1 ELSE 0 END) +
    (CASE WHEN class1_school_readiness_calendar_availability IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR class1_school_readiness_calendar_availability IS NULL THEN 1 ELSE 0 END)
    ) AS total_unreported

    FROM data_db.ss_data
    GROUP BY block_town, quarter
    ORDER BY block_town, quarter
;
"""

ATTENDANCE_SUMMARY_BY_BLOCK_QUARTER = """
    SELECT
    block_town,
    quarter,
    COUNT(*) AS num_visits,

    -- Average enrolled
    AVG(number_of_registered_boys + number_of_registered_girls) AS avg_registered_students,

    -- Average present
    AVG(number_of_present_boys + number_of_present_girls) AS avg_present_students,

    -- Attendance percentage
    ROUND(
        AVG(
        CASE 
            WHEN (number_of_registered_boys + number_of_registered_girls) > 0
            THEN ( (number_of_present_boys + number_of_present_girls) * 100.0 ) / (number_of_registered_boys + number_of_registered_girls)
            ELSE NULL
        END
        ), 
        1
    ) AS attendance_pct,

    -- Average total teachers
    AVG(total_working_teachers) AS avg_working_teachers,

    -- Student-teacher ratio
    ROUND(
        AVG(
        CASE 
            WHEN total_working_teachers > 0
            THEN (number_of_registered_boys + number_of_registered_girls) * 1.0 / total_working_teachers
            ELSE NULL
        END
        ), 
        1
    ) AS student_teacher_ratio

    FROM data_db.ss_data
    GROUP BY block_town, quarter
    ORDER BY block_town, quarter;
"""

TEACHER_PERFORMANCE_SCORES = """
    SELECT
    district_name,
    block_town,
    udise_code,
    year,
    quarter,
    month,

    -- Teacher Preparedness (General)
    (
        (CASE WHEN teaching_plan_assessment_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN clarity_of_weekly_objectives = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN diary_filled_by_teacher = 'हाँ' THEN 1 ELSE 0 END)
    ) AS positive_score_prep_general,

    (
        (CASE WHEN teaching_plan_assessment_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN clarity_of_weekly_objectives = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN diary_filled_by_teacher = 'नहीं' THEN 1 ELSE 0 END)
    ) AS negative_score_prep_general,

    (
        (CASE WHEN teaching_plan_assessment_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR teaching_plan_assessment_sentiment IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN clarity_of_weekly_objectives NOT IN ('हाँ','नहीं') OR clarity_of_weekly_objectives IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN diary_filled_by_teacher NOT IN ('हाँ','नहीं') OR diary_filled_by_teacher IS NULL THEN 1 ELSE 0 END)
    ) AS unreported_score_prep_general,

    -- Teacher Preparedness for Class
    (
        (CASE WHEN teaching_plan_source = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN learning_outcome_in_plan = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN teaching_plan_for_all_levels = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN today_teaching_plan_prepared = 'हाँ' THEN 1 ELSE 0 END)
    ) AS positive_score_prep_class,

    (
        (CASE WHEN teaching_plan_source = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN learning_outcome_in_plan = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN teaching_plan_for_all_levels = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN today_teaching_plan_prepared = 'नहीं' THEN 1 ELSE 0 END)
    ) AS negative_score_prep_class,

    (
        (CASE WHEN teaching_plan_source NOT IN ('हाँ','नहीं') OR teaching_plan_source IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN learning_outcome_in_plan NOT IN ('हाँ','नहीं') OR learning_outcome_in_plan IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN teaching_plan_for_all_levels NOT IN ('हाँ','नहीं') OR teaching_plan_for_all_levels IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN today_teaching_plan_prepared NOT IN ('हाँ','नहीं') OR today_teaching_plan_prepared IS NULL THEN 1 ELSE 0 END)
    ) AS unreported_score_prep_class,

    -- Teacher-Student Interaction
    (
        (CASE WHEN teacher_understanding_current_learning_level = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_giving_equal_opportunities = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_conducting_group_work = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN is_teacher_doing_group_work = 'हाँ' THEN 1 ELSE 0 END) +
        (CASE WHEN language_opportunity_encouragement_sentiment = 'positive' THEN 1 ELSE 0 END)
    ) AS positive_score_interaction,

    (
        (CASE WHEN teacher_understanding_current_learning_level = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_giving_equal_opportunities = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_conducting_group_work = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN is_teacher_doing_group_work = 'नहीं' THEN 1 ELSE 0 END) +
        (CASE WHEN language_opportunity_encouragement_sentiment = 'negative' THEN 1 ELSE 0 END)
    ) AS negative_score_interaction,

    (
        (CASE WHEN teacher_understanding_current_learning_level NOT IN ('हाँ','नहीं') OR teacher_understanding_current_learning_level IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_giving_equal_opportunities NOT IN ('हाँ','नहीं') OR teacher_giving_equal_opportunities IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_conducting_group_work NOT IN ('हाँ','नहीं') OR teacher_conducting_group_work IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN is_teacher_doing_group_work NOT IN ('हाँ','नहीं') OR is_teacher_doing_group_work IS NULL THEN 1 ELSE 0 END) +
        (CASE WHEN language_opportunity_encouragement_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') OR language_opportunity_encouragement_sentiment IS NULL THEN 1 ELSE 0 END)
    ) AS unreported_score_interaction

    FROM data_db.ss_data
    ORDER BY district_name, block_town, udise_code, year, quarter, month
"""

CLASS_OBSERVATION_SCORES = """
    SELECT
    district_name,
    block_town,
    udise_code,
    year,
    quarter,
    month,

    -- Positive count (each 'positive' adds 1)
    (
        (CASE WHEN teacher_material_use_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN class_activity_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN activity_conducted_as_per_plan_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_actions_while_narrating_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN student_participation_in_activity_sentiment = 'positive' THEN 1 ELSE 0 END) +
        (CASE WHEN activity_as_per_guide_sentiment = 'positive' THEN 1 ELSE 0 END)
    ) AS positive_count,

    -- Negative count
    (
        (CASE WHEN teacher_material_use_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN class_activity_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN activity_conducted_as_per_plan_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_actions_while_narrating_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN student_participation_in_activity_sentiment = 'negative' THEN 1 ELSE 0 END) +
        (CASE WHEN activity_as_per_guide_sentiment = 'negative' THEN 1 ELSE 0 END)
    ) AS negative_count,

    -- Unreported count
    (
        (CASE WHEN teacher_material_use_sentiment IS NULL OR teacher_material_use_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END) +
        (CASE WHEN class_activity_sentiment IS NULL OR class_activity_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END) +
        (CASE WHEN activity_conducted_as_per_plan_sentiment IS NULL OR activity_conducted_as_per_plan_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END) +
        (CASE WHEN teacher_actions_while_narrating_sentiment IS NULL OR teacher_actions_while_narrating_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END) +
        (CASE WHEN student_participation_in_activity_sentiment IS NULL OR student_participation_in_activity_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END) +
        (CASE WHEN activity_as_per_guide_sentiment IS NULL OR activity_as_per_guide_sentiment IN ('unknown', 'nan', '', 'N/A', 'NA', 'None') THEN 1 ELSE 0 END)
    ) AS unreported_count

    FROM data_db.ss_data;
"""

HOME_SUMMARY_TABLE = """
    SELECT
        MIN(inspection_date) AS earliest_date,
        MAX(inspection_date) AS latest_date,
        COUNT(DISTINCT CONCAT(year, '-', quarter)) AS unique_quarters,
        COUNT(DISTINCT CONCAT(year, '-', month)) AS unique_months,
        COUNT(*) AS total_visits,
        COUNT(DISTINCT udise_code) AS unique_schools,
        COUNT(DISTINCT mentor_name) AS unique_mentors,
        COUNT(DISTINCT block_town) AS unique_blocks,
        ROUND(CAST(COUNT(*) AS DOUBLE) / COUNT(DISTINCT udise_code), 2) AS avg_visits_per_school,
        ROUND(CAST(COUNT(*) AS DOUBLE) / COUNT(DISTINCT mentor_name), 2) AS avg_visits_per_mentor
    FROM data_db.ss_data;
"""

TOP_THREE_ACTIVE_MENTORS = """
    SELECT
        mentor_name,
        mobile_number,
        COUNT(*) AS total_visits
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number
    ORDER BY total_visits DESC
    LIMIT 3;
""" 

BOTTOM_THREE_ACTIVE_MENTORS = """
    SELECT
        mentor_name,
        mobile_number,
        COUNT(*) AS total_visits
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number
    ORDER BY total_visits ASC
    LIMIT 3;
""" 

TOP_THREE_VISITED_SCHOOLS = """
    SELECT
        district_name,
        block_town,
        school_name,
        udise_code,
        COUNT(*) AS total_visits
    FROM data_db.ss_data
    GROUP BY district_name, block_town, school_name, udise_code
    ORDER BY total_visits DESC
    LIMIT 3;
"""

BOTTOM_THREE_VISITED_SCHOOLS = """
    SELECT
        district_name,
        block_town,
        school_name,
        udise_code,
        COUNT(*) AS total_visits
    FROM data_db.ss_data
    GROUP BY district_name, block_town, school_name, udise_code
    ORDER BY total_visits ASC
    LIMIT 3;
"""

MENTOR_BLOCK_VISITS_TABLE = """
    SELECT
        block_town,
        COUNT(*) AS total_visits
    FROM data_db.ss_data
    GROUP BY block_town
    ORDER BY total_visits DESC;
"""

MENTOR_BLOCK_UNIQUE_MENTORS = """
    SELECT
    block_town,
    COUNT(DISTINCT mentor_name) AS unique_mentors
    FROM data_db.ss_data
    GROUP BY block_town
    ORDER BY block_town;
"""

SCHOOL_IDENTIFIERS_SUMMARY = """
    SELECT
    udise_code,
    ANY_VALUE(school_name) AS school_name,
    ANY_VALUE(block_town) AS block_town,
    ANY_VALUE(district_name) AS district_name,
    ANY_VALUE(area_type) AS area_type,
    COUNT(*) AS total_visits,
    COUNT(DISTINCT mobile_number) AS unique_mentors
    FROM data_db.ss_data
    GROUP BY udise_code;
"""

SCHOOL_MENTOR_VISITS = """
    SELECT
    udise_code,
    mentor_name,
    mobile_number,
    COUNT(*) AS visits
    FROM data_db.ss_data
    GROUP BY udise_code, mentor_name, mobile_number
    ORDER BY udise_code, visits DESC;
"""

SCHOOL_VISIT_QUARTER_SUMMARY = """
    SELECT
    udise_code,
    year,
    quarter,
    COUNT(*) AS visits_in_quarter
    FROM data_db.ss_data
    GROUP BY udise_code, year, quarter
    ORDER BY udise_code, year, quarter;
"""

MENTOR_SUMMARY = """
    SELECT
    mentor_name,
    mobile_number,
    COUNT(*) AS total_visits,
    COUNT(DISTINCT udise_code) AS unique_schools_visited,
    COUNT(DISTINCT block_town) AS unique_blocks_visited,
    MIN(inspection_date) AS first_visit_date,
    MAX(inspection_date) AS last_visit_date,
    ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT strftime('%Y-%m', inspection_date)), 0), 2) AS avg_visits_per_month
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number
    ORDER BY total_visits DESC;
"""

MENTOR_VISITS_PER_QUARTER = """
    SELECT
    mentor_name,
    mobile_number,
    year,
    quarter,
    COUNT(*) AS visits_in_quarter
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number, year, quarter
    ORDER BY mentor_name, year, quarter;
"""

MENTOR_VISITS_PER_BLOCK = """
    SELECT
    mentor_name,
    mobile_number,
    block_town,
    COUNT(*) AS visits_in_block
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number, block_town
    ORDER BY mentor_name, visits_in_block DESC;
"""

MENTOR_UNIQUE_SCHOOLS_PER_BLOCK = """
    SELECT
    mentor_name,
    mobile_number,
    block_town,
    COUNT(DISTINCT udise_code) AS unique_schools
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number, block_town
    ORDER BY mentor_name, unique_schools DESC;
"""

MENTOR_VISITS_PER_MONTH = """
    SELECT
    mentor_name,
    mobile_number,
    strftime('%Y-%m', inspection_date) AS year_month,
    COUNT(*) AS visits_in_month
    FROM data_db.ss_data
    GROUP BY mentor_name, mobile_number, year_month
    ORDER BY mentor_name, year_month;
"""
    