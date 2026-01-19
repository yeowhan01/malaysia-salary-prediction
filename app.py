import streamlit as st
import pandas as pd
from salary_predictor import predict_salary, predict_salary_range

# --------------------------------------------------
# Initialize session_state
# --------------------------------------------------
if "reset_counter" not in st.session_state:
    st.session_state["reset_counter"] = 0
if "category" not in st.session_state:
    st.session_state["category"] = None
if "job_title" not in st.session_state:
    st.session_state["job_title"] = None
if "experience" not in st.session_state:
    st.session_state["experience"] = 3
if "state" not in st.session_state:
    st.session_state["state"] = None


# --------------------------------------------------
# Sidebar Feedback
# --------------------------------------------------
# Sidebar Feedback Section
st.sidebar.markdown("## 💬 Feedback")
st.sidebar.caption("💡 Help us improve this salary prediction app by sharing your feedback!")

# Make a "button-like" link that opens Google Form
feedback_link = "https://forms.gle/zQMqx2tvwm1CY1Er6"
st.sidebar.markdown(
    f"""
    <a href="{feedback_link}" target="_blank">
        <button style="
            width: 100%;
            padding: 10px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;">
            📝 Share Feedback
        </button>
    </a>
    """,
    unsafe_allow_html=True
)



tab_predict, tab_insights = st.tabs([
    "💰 Salary Prediction",
    "📊 Market Insights"
])

with tab_predict:
    # --------------------------------------------------
    # Load UI reference data
    # --------------------------------------------------
    ui_df = pd.read_csv("ui_reference_data.csv")

    categories_all = sorted(ui_df["category_clean"].dropna().unique())
    states = sorted(ui_df["state_region"].dropna().unique())

    # Job → Categories
    job_to_categories = (
        ui_df.groupby("job_title_normalized")["category_clean"]
            .apply(lambda x: sorted(x.unique()))
            .to_dict()
    )

    # Category → Jobs
    category_to_jobs = (
        ui_df.groupby("category_clean")["job_title_normalized"]
            .apply(lambda x: sorted(x.unique()))
            .to_dict()
    )

    # --------------------------------------------------
    # Title
    # --------------------------------------------------
    st.title("Malaysia Job Salary Prediction")
    st.write(
        "Predict the average salary based on job category, job title, experience, and location."
    )

    # --------------------------------------------------
    # Job Category selectbox
    # --------------------------------------------------
    category_options_display = ["-- Select category --"] + categories_all
    category = st.selectbox(
        "Job Category",
        options=category_options_display,
        index=0 if st.session_state.get("category") is None else categories_all.index(st.session_state.get("category")) + 1,
        key=f"category_{st.session_state['reset_counter']}"
    )
    category = None if category == "-- Select category --" else category
    st.session_state["category"] = category

    # --------------------------------------------------
    # Job Title selectbox (filtered by category)
    # --------------------------------------------------
    if category:
        job_title_options = category_to_jobs.get(category, [])
    else:
        job_title_options = []

    job_title_options_display = ["-- Select job title --"] + job_title_options
    job_title = st.selectbox(
        "Job Title",
        options=job_title_options_display,
        index=0 if st.session_state.get("job_title") is None else job_title_options.index(st.session_state.get("job_title")) + 1 if st.session_state.get("job_title") in job_title_options else 0,
        key=f"job_title_{st.session_state['reset_counter']}"
    )
    job_title = None if job_title == "-- Select job title --" else job_title
    st.session_state["job_title"] = job_title

    # --------------------------------------------------
    # Other inputs
    # --------------------------------------------------
    # --------------------------------------------------
    # Determine max experience based on job title
    # --------------------------------------------------
    # --------------------------------------------------
    # Determine max experience based on job title
    # --------------------------------------------------
    # Determine experience input type
    if job_title and job_title.lower().startswith("internship"):
        experience = st.number_input(
            "Experience (years)",
            min_value=0,
            max_value=0,
            value=0,
            step=1,
            disabled=True,
            help="Internship experience is always 0 years.",
            key=f"experience_{st.session_state['reset_counter']}"
        )
    else:
        experience = st.slider(
            "Experience (years)",
            min_value=0,
            max_value=10,
            value=3,
            key=f"experience_{st.session_state['reset_counter']}"
        )


    st.caption(
        "Experience is grouped into ranges (intern, junior, mid, senior) "
        "to provide stable and realistic salary predictions."
    )

    state_options_display = ["-- Select state --"] + states
    state = st.selectbox(
        "State / Region",
        options=state_options_display,
        index=0 if st.session_state.get("state") is None else states.index(st.session_state.get("state")) + 1,
        key=f"state_{st.session_state['reset_counter']}"
    )

    # --------------------------------------------------
    # Form validation
    # --------------------------------------------------
    form_valid = category is not None and job_title is not None and state is not None
    # --------------------------------------------------
    # Predict button
    # --------------------------------------------------
    col1, col2, _ = st.columns([1, 1, 2])

    with col1:
        predict_clicked = st.button("💰 Predict Salary", disabled=not form_valid, use_container_width=True)

    with col2:
        reset_clicked = st.button("🔄 Reset", use_container_width=True)

    st.caption("Predict uses historical salary data. Reset clears all selections.")


    if reset_clicked:
        st.session_state["category"] = None
        st.session_state["job_title"] = None
        st.session_state["experience"] = 3
        st.session_state["state"] = None
        st.session_state["reset_counter"] += 1
        st.rerun()
        



    if predict_clicked:

        salary = predict_salary(
            job_title,
            category,
            experience,
            state
        )

        low, high = predict_salary_range(
            job_title,
            category,
            experience,
            state
        )

        st.success(f"💰 Predicted Salary: RM {salary:,.0f}")
        st.info(f"📊 Expected Salary Range: RM {low:,.0f} – RM {high:,.0f}")

        st.caption(
            f"This estimate is based on historical data for "
            f"'{job_title}' roles in the '{category}' category "
            f"in {state}, with around {experience} years of experience."
        )

        st.warning(
            "⚠️ This is an estimated salary. Actual compensation may vary "
            "based on company, skills, and market conditions."
        )


with tab_insights:
    st.subheader("📊 Malaysia Job Market Insights")
    st.caption("Insights based on historical job salary data.")

    # --- Avg salary by state ---
    st.markdown("### Average Salary by State")
    state_salary = (
        ui_df.groupby("state_region")["avg_salary_myr"]
        .mean()
        .sort_values(ascending=False)
    )
    st.bar_chart(state_salary)

    # --- Avg salary by category ---
    st.markdown("### Average Salary by Job Category")
    category_salary = (
        ui_df.groupby("category_clean")["avg_salary_myr"]
        .mean()
        .sort_values(ascending=False)
    )
    st.bar_chart(category_salary)

    # --- Salary distribution ---
    st.markdown("### Salary Distribution")
    st.histogram = st.bar_chart(
        ui_df["avg_salary_myr"].clip(upper=20000)
    )

    # --- Top paying roles ---
    st.markdown("### Top Paying Job Titles")
    top_roles = (
        ui_df.groupby("job_title_normalized")["avg_salary_myr"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    st.dataframe(top_roles.reset_index())
