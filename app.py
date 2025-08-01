# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from db import init_db, insert_expense, delete_last_expense, get_all_expenses
import altair as alt

# Initialize database
init_db()

# Background color using custom CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1C3948;
    }
    [data-testid="stSidebar"] {
        background-color: #CC8A4D; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- SIDEBAR INPUT FORM ----
st.sidebar.title("Add Expense")


# Dropdowns for month and year
month = st.sidebar.selectbox("Select Month", list(calendar.month_name)[6:])
year = st.sidebar.selectbox("Select Year", list(range(2025, datetime.now().year + 1)))
date_str = f"{month} {year}"

with st.sidebar.form("expense_form", clear_on_submit=False):
    label = st.selectbox("Select Expense Category:", [
        "Dining", "Chicken", "Lovely", "House", "Fuel", "EMI", "Non-Essentials"
    ])
    col_amt, col_btn = st.columns([2, 1])
    with col_amt:
        amount = st.number_input("Enter Amount", min_value=0, step=10, format="%d")
    with col_btn:
        st.markdown("<div style='height: 1.8em'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add")
    comment = st.text_input("Comment (optional)" if label != "Non-Essentials" else "Comment (required)")

if submitted:
    if label == "Non-Essentials" and comment.strip() == "":
        st.warning("Comment is required for Non-Essentials.")
    else:
        insert_expense(date_str, label, amount, comment.strip())
        st.rerun()

    if label == "Non-Essentials" and comment.strip() == "":
        st.sidebar.warning("Comment is required for Non-Essentials.")
    else:
        insert_expense(date_str, label, amount, comment.strip())
        st.rerun()

# Delete last entry
if st.sidebar.button("Delete Last Entry"):
    delete_last_expense()
    st.rerun()

# ---- MAIN SECTION ----

# st.title("📊 Monthly Expense Tracker")

# Calculate and display summary totals: total value for selected month
df = get_all_expenses()
df_filtered = df[df["date_str"] == date_str]
if not df_filtered.empty:
    basic_total = df_filtered[df_filtered['label'].isin(["Dining", "House", "Fuel"])] ["amount"].sum()
    dog_total = df_filtered[df_filtered['label'].isin(["Chicken", "Lovely"])] ["amount"].sum()
    emi_total = df_filtered[df_filtered['label'] == "EMI"] ["amount"].sum()
    non_essential_total = df_filtered[df_filtered['label'] == "Non-Essentials"] ["amount"].sum()
    summary_total = int(basic_total) + int(dog_total) + int(emi_total) + int(non_essential_total)

    # Calculate last month
    month_names = list(calendar.month_name)
    current_month_idx = month_names.index(month)
    if current_month_idx == 1:
        prev_month = month_names[12]
        prev_year = year - 1
    else:
        prev_month = month_names[current_month_idx - 1]
        prev_year = year
    prev_date_str = f"{prev_month} {prev_year}"
    prev_df = df[df["date_str"] == prev_date_str]
    if not prev_df.empty:
        prev_basic = prev_df[prev_df['label'].isin(["Dining", "House", "Fuel"])] ["amount"].sum()
        prev_dog = prev_df[prev_df['label'].isin(["Chicken", "Lovely"])] ["amount"].sum()
        prev_emi = prev_df[prev_df['label'] == "EMI"] ["amount"].sum()
        prev_non_essential = prev_df[prev_df['label'] == "Non-Essentials"] ["amount"].sum()
        prev_total = int(prev_basic) + int(prev_dog) + int(prev_emi) + int(prev_non_essential)
    else:
        prev_total = 0


    # Determine color and rupee symbol for this month expense
    if summary_total < prev_total:
        this_color = '#4CAF50'  # green
    elif summary_total > prev_total:
        this_color = '#FF5252'  # red
    else:
        this_color = '#fff'     # white
    rupee = '&#8377;'
    st.markdown(f"""
        <div style='text-align:center; font-size:2em; font-weight:bold; letter-spacing:2px; color:#E68C3A; text-transform:uppercase;'>
            THIS MONTH EXPENSE: <span style='color:{this_color};'>{rupee} {summary_total:,}</span>
        </div>
        <div style='text-align:center; font-size:1.1em; color:#E68C3A; margin-top:0.2em;'>
            Last month expense: <span style='color:#fff;'>{rupee} {prev_total:,}</span>
        </div>
    """, unsafe_allow_html=True)

    # Add vertical space and a divider for presentation
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

df = get_all_expenses()

if df.empty:
    st.info("No data available yet.")
else:
    # Filter by selected month/year
    df_filtered = df[df["date_str"] == date_str]

    if df_filtered.empty:
        st.warning(f"No records for {date_str}")
    else:
        # Group totals
        def get_total(labels):
            return df_filtered[df_filtered['label'].isin(labels)]['amount'].sum()

        basic_total = get_total(["Dining", "House", "Fuel"])
        dog_total = get_total(["Chicken", "Lovely"])
        emi_total = get_total(["EMI"])
        non_essential_total = get_total(["Non-Essentials"])



        st.markdown("<h3 style='text-align:left; color:#fff; font-weight:bold;'>Summary Totals</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns([2,2])

        with col1:
            summary_df = pd.DataFrame({
                "Category": ["Basic (Essentials)", "Dog Expenses", "EMI", "Non-Essentials"],
                "Total": [int(basic_total), int(dog_total), int(emi_total), int(non_essential_total)]
            })
            total_sum = summary_df["Total"].sum()
            summary_df = pd.concat([
                summary_df,
                pd.DataFrame({"Category": ["Total"], "Total": [total_sum]})
            ], ignore_index=True)
            summary_df.index += 1
            st.table(summary_df)
            summary_csv = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=" Download",
                data=summary_csv,
                file_name=f'summary_totals_{date_str.replace(" ", "_")}.csv',
                mime='text/csv'
            )

        with col2:
            import altair as alt
            pie_df = summary_df[summary_df["Category"] != "Total"]
            pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=90, stroke='white', strokeWidth=3).encode(
                theta=alt.Theta(field="Total", type="quantitative"),
                color=alt.Color(field="Category", type="nominal"),
                tooltip=["Category", "Total"]
            ).properties(
                width=300,
                height=300,
                background="#1C3948"
            )
            st.altair_chart(pie_chart, use_container_width=True)


        # Expense Category Totals table and pie chart side by side

        st.markdown("<h3 style='text-align:left; color:#fff; font-weight:bold;'>Expense Category Totals</h3>", unsafe_allow_html=True)
        cat_col1, cat_col2 = st.columns([2,2])

        with cat_col1:
            label_totals = df_filtered.groupby("label")["amount"].sum().astype(int).reset_index()
            label_totals.columns = ["Label", "Total"]
            label_totals.index += 1
            st.table(label_totals)

        with cat_col2:
            import altair as alt
            if not label_totals.empty:
                pie_chart2 = alt.Chart(label_totals).mark_arc(innerRadius=90, stroke='white', strokeWidth=3).encode(
                    theta=alt.Theta(field="Total", type="quantitative"),
                    color=alt.Color(field="Label", type="nominal"),
                    tooltip=["Label", "Total"]
                ).properties(
                    width=300,
                    height=300,
                    background="#1C3948"
                )
                st.altair_chart(pie_chart2, use_container_width=True)


        # Essentials vs Non-Essentials Table and Pie Chart side by side
        st.divider()
        essentials_total = int(basic_total) + int(dog_total) + int(emi_total)
        non_essentials_total = int(non_essential_total)
        essentials_vs_non_df = pd.DataFrame({
            "Category": ["Essentials Total", "Non-Essentials Total"],
            "Total": [essentials_total, non_essentials_total]
        })
        # Merged right-aligned section title above both columns
        st.markdown("<h3 style='text-align:right; color:#fff; font-weight:bold;'>Essentials vs Non-Essentials</h3>", unsafe_allow_html=True)
        ess_col1, ess_col2 = st.columns([2,2])
        with ess_col1:
            import altair as alt
            pie_chart3 = alt.Chart(essentials_vs_non_df).mark_arc(innerRadius=90, stroke='white', strokeWidth=3).encode(
                theta=alt.Theta(field="Total", type="quantitative"),
                color=alt.Color(field="Category", type="nominal"),
                tooltip=["Category", "Total"]
            ).properties(
                width=300,
                height=300,
                background="#1C3948"
            )
            st.altair_chart(pie_chart3, use_container_width=True)
        with ess_col2:
            essentials_vs_non_df.index += 1
            st.table(essentials_vs_non_df)
        st.divider()




        # All entries table as dropdown with label filter
        with st.expander(f"All Entries for {date_str}"):
            label_options = ["All"] + sorted(df_filtered["label"].unique().tolist())
            selected_label = st.selectbox("Filter by Label", label_options, key="all_entries_label_filter")
            df_filtered["amount"] = df_filtered["amount"].astype(int)
            if selected_label == "All":
                display_df = df_filtered
            else:
                display_df = df_filtered[df_filtered["label"] == selected_label]
            total_amt = display_df["amount"].sum()
            st.markdown(f"**Total Amount: <span style='color:#E68C3A;font-size:1.2em'>{total_amt:,}</span>**", unsafe_allow_html=True)
            df_to_show = display_df[["date_str", "label", "amount", "comment", "timestamp"]].copy()
            df_to_show.index += 1

        # --- Multi-Line Chart for Summary Totals for All Months ---
        st.divider()
        st.markdown("<h3 style='text-align:center; color:#fff; font-weight:bold;'>📈 Month to Month Analysis</h3>", unsafe_allow_html=True)
        # Prepare summary totals for all months
        all_months = df["date_str"].unique()
        summary_list = []
        for m in sorted(all_months, key=lambda x: (int(x.split()[1]), list(calendar.month_name).index(x.split()[0]))):
            month_df = df[df["date_str"] == m]
            basic = month_df[month_df['label'].isin(["Dining", "House", "Fuel"])] ["amount"].sum()
            dog = month_df[month_df['label'].isin(["Chicken", "Lovely"])] ["amount"].sum()
            emi = month_df[month_df['label'] == "EMI"] ["amount"].sum()
            non_ess = month_df[month_df['label'] == "Non-Essentials"] ["amount"].sum()
            summary_list.append({
                "Month": m,
                "Basic (Essentials)": int(basic),
                "Dog Expenses": int(dog),
                "EMI": int(emi),
                "Non-Essentials": int(non_ess)
            })
        summary_line_df = pd.DataFrame(summary_list)
        if not summary_line_df.empty:
            line_df = summary_line_df.melt(id_vars=["Month"], value_vars=["Basic (Essentials)", "Dog Expenses", "EMI", "Non-Essentials"], var_name="Category", value_name="Total")
            # Main multi-line chart
            line_chart_main = alt.Chart(line_df).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Month:N', sort=None, axis=alt.Axis(
                    labelAngle=-45,
                    domainColor='white',
                    tickColor='white',
                    labelColor='white',
                    titleColor='white',
                    gridColor='white',
                    gridOpacity=0.3
                )),
                y=alt.Y('Total:Q', axis=alt.Axis(
                    domainColor='white',
                    tickColor='white',
                    labelColor='white',
                    titleColor='white',
                    gridColor='white',
                    gridOpacity=0.3
                )),
                color=alt.Color('Category:N'),
                tooltip=['Month', 'Category', 'Total']
            )
            # Vertical rules at each month
            months_unique = line_df['Month'].unique().tolist()
            rule_df = pd.DataFrame({'Month': months_unique})
            vlines = alt.Chart(rule_df).mark_rule(
                color='white',
                strokeDash=[4,2],
                size=2,
                opacity=0.4
            ).encode(
                x=alt.X('Month:N', sort=None)
            )
            line_chart = (line_chart_main + vlines).properties(
                width='container',
                height=400,
                background="#1C3948"
            )
            st.altair_chart(line_chart, use_container_width=True)

        # --- Multi-Line Chart for Expense Category Totals Table ---
        st.divider()
        st.markdown("<h3 style='text-align:center; color:#fff; font-weight:bold;'>📈 Category Totals by Month</h3>", unsafe_allow_html=True)
        # Prepare category totals for all months
        cat_months = df["date_str"].unique()
        cat_labels = df["label"].unique()
        cat_list = []
        for m in sorted(cat_months, key=lambda x: (int(x.split()[1]), list(calendar.month_name).index(x.split()[0]))):
            month_df = df[df["date_str"] == m]
            for label in cat_labels:
                total = month_df[month_df["label"] == label]["amount"].sum()
                cat_list.append({
                    "Month": m,
                    "Label": label,
                    "Total": int(total)
                })
        cat_line_df = pd.DataFrame(cat_list)
        if not cat_line_df.empty:
            # Main multi-line chart
            cat_line = alt.Chart(cat_line_df).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('Month:N', sort=None, axis=alt.Axis(
                    labelAngle=-45,
                    domainColor='white',
                    tickColor='white',
                    labelColor='white',
                    titleColor='white',
                    gridColor='white',
                    gridOpacity=0.3
                )),
                y=alt.Y('Total:Q', axis=alt.Axis(
                    domainColor='white',
                    tickColor='white',
                    labelColor='white',
                    titleColor='white',
                    gridColor='white',
                    gridOpacity=0.3
                )),
                color=alt.Color('Label:N'),
                tooltip=['Month', 'Label', 'Total']
            )
            # Vertical rules at each month
            months_unique = cat_line_df['Month'].unique().tolist()
            rule_df = pd.DataFrame({'Month': months_unique})
            vlines = alt.Chart(rule_df).mark_rule(
                color='white',
                strokeDash=[4,2],
                size=2,
                opacity=0.4
            ).encode(
                x=alt.X('Month:N', sort=None)
            )
            cat_line_chart = (cat_line + vlines).properties(
                width='container',
                height=400,
                background="#1C3948"
            )


            st.altair_chart(cat_line_chart, use_container_width=True)
            st.divider()

            # --- Quick Summary: Category Progress Compared to Previous Month ---
            if len(cat_line_df['Month'].unique()) > 1:
                months_sorted = sorted(cat_line_df['Month'].unique(), key=lambda x: (int(x.split()[1]), list(calendar.month_name).index(x.split()[0])))
                last_month = months_sorted[-1]
                prev_month = months_sorted[-2]
                last_df = cat_line_df[cat_line_df['Month'] == last_month].set_index('Label')
                prev_df = cat_line_df[cat_line_df['Month'] == prev_month].set_index('Label')
                green_msgs = []
                red_msgs = []
                for label in cat_labels:
                    last_val = last_df.loc[label, 'Total'] if label in last_df.index else 0
                    prev_val = prev_df.loc[label, 'Total'] if label in prev_df.index else 0
                    if last_val < prev_val:
                        diff = prev_val - last_val
                        green_msgs.append(f"<li style='margin-bottom:0.2em'><span style='color:#4CAF50;font-weight:bold'>{label} ↓ {diff:,}</span></li>")
                    elif last_val > prev_val:
                        diff = last_val - prev_val
                        red_msgs.append(f"<li style='margin-bottom:0.2em'><span style='color:#FF5252;font-weight:bold'>{label} ↑ {diff:,}</span></li>")
                if green_msgs or red_msgs:
                    # Prepare change data for plot
                    change_data = []
                    for label in cat_labels:
                        last_val = last_df.loc[label, 'Total'] if label in last_df.index else 0
                        prev_val = prev_df.loc[label, 'Total'] if label in prev_df.index else 0
                        diff = last_val - prev_val
                        change_data.append({"Label": label, "Change": diff})
                    import altair as alt
                    change_df = pd.DataFrame(change_data)
                    # Bar plot: green for decrease, red for increase
                    change_df["Color"] = change_df["Change"].apply(lambda x: '#4CAF50' if x < 0 else ('#FF5252' if x > 0 else '#E68C3A'))
                    bar_chart = alt.Chart(change_df).mark_bar(size=35, cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
                        x=alt.X('Label:N', sort=None, axis=alt.Axis(labelColor='white', titleColor='white', domainColor='white', tickColor='white')),
                        y=alt.Y('Change:Q', axis=alt.Axis(labelColor='white', titleColor='white', domainColor='white', tickColor='white')),
                        color=alt.Color('Color:N', scale=None, legend=None),
                        tooltip=['Label', 'Change']
                    ).properties(
                        width=300,
                        height=220,
                        background="#22384a",
                        title=alt.TitleParams(text="Change by Category", color="#E68C3A", fontSize=18, anchor="middle")
                    )
                    # Side-by-side layout using Streamlit columns
                    table_col, plot_col = st.columns([2,1])
                    with table_col:
                        st.markdown(
                            f"""
                            <div style='margin-top:1em; display:flex; justify-content:flex-start;'>
                              <div style='border:2px solid #E68C3A; border-radius:10px; background:#22384a; padding:1em 2em; display:flex; min-width:350px; max-width:700px; width:100%;'>
                                <div style='flex:1; text-align:left; padding-right:1em; border-right:1.5px solid #E68C3A;'>
                                  <div style='font-size:1.1em; font-weight:bold; margin-bottom:0.5em;'>Expense Decreased 👍</div>
                                  <ul style='list-style-type:none; padding-left:0; margin:0;'>
                                    {''.join(green_msgs)}
                                  </ul>
                                </div>
                                <div style='flex:1; text-align:right; padding-left:1em;'>
                                  <div style='font-size:1.1em; font-weight:bold; margin-bottom:0.5em;'>Expense Increased 👎</div>
                                  <ul style='list-style-type:none; padding-left:0; margin:0;'>
                                    {''.join(red_msgs)}
                                  </ul>
                                </div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with plot_col:
                        st.markdown("<div style='margin-top:2.5em'></div>", unsafe_allow_html=True)
                        st.altair_chart(bar_chart, use_container_width=False)