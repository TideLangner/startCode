import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

# Rebuild task data after reset
start_date = dt.date(2025, 7, 28)

tasks = [
    ("Stakeholder Engagement & Project Initiation", 0, 14),
    ("Initiation Report", 0, 14),
    ("Literature Review & Background Research", 0, 28),
    ("Project Planning & Admin Setup", 0, 14),

    # Modelling phase starts earlier and runs longer
    ("Model Setup (PVLib & PVMismatch)", 14, 28),
    ("Mid-Project Report", 28, 11),
    ("Model Expansion & Data Integration", 28, 28),

    # Interim PMGAP finishes exactly on 17 Sept (Day 51 from start)
    ("Interim PMGAP", 44, 7),

    # More time for experimentation & analysis
    ("Analysis & Strategy Testing", 42, 28),

    # Extended report writing after main analysis
    ("Final Report Writing", 56, 35),
    ("Poster & Final Deliverables", 63, 28),

    # Conference preparation finishes *before* conference days
    ("Presentation Preparation", 56, 7),   # Ends ~28 Sept
    ("Conference & Delivery", 63, 3),       # 29 Sept – 2 Oct
]

df = pd.DataFrame(tasks, columns=["Task", "StartOffset", "Duration"])
df["Start"] = [start_date + pd.Timedelta(days=int(x)) for x in df["StartOffset"]]
df["Finish"] = df["Start"] + pd.to_timedelta(df["Duration"], unit="D")

# Milestones
milestones = [
    ("Initiation Report", dt.date(2025, 8, 11)),
    ("Mid-Project Report", dt.date(2025, 9, 5)),
    ("Interim PMGAP", dt.date(2025, 9, 17)),
    ("Slides Submission", dt.date(2025, 9, 29)),
    ("Conference Day 1", dt.date(2025, 9, 29)),
    ("Conference Day 2", dt.date(2025, 9, 30)),
    ("Conference Day 3", dt.date(2025, 10, 2)),
    ("Final Submission", dt.date(2025, 10, 27)),
]

# Category colors
category_colors = {
    "Stakeholder Engagement": "#A6CEE3",
    "Planning & Admin": "#1F78B4",
    "Research": "#B2DF8A",
    "Modelling": "#33A02C",
    "Analysis": "#E31A1C",
    "Reporting": "#FDBF6F",
    "Presentation": "#FF7F00",
    "Finalisation": "#CAB2D6"
}

# Map tasks to categories
task_categories = {
    "Stakeholder Engagement & Project Initiation": "Stakeholder Engagement",
    "Initiation Report": "Stakeholder Engagement",
    "Literature Review & Background Research": "Research",
    "Project Planning & Admin Setup": "Planning & Admin",
    "Model Setup (PVLib & PVMismatch)": "Modelling",
    "Mid-Project Report": "Reporting",
    "Model Expansion & Data Integration": "Modelling",
    "Interim PMGAP": "Reporting",
    "Analysis & Strategy Testing": "Analysis",
    "Presentation Preparation": "Presentation",
    "Conference & Delivery": "Presentation",
    "Final Report Writing": "Reporting",
    "Poster & Final Deliverables": "Finalisation"
}

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

# Plot tasks
for i, row in df.iterrows():
    category = task_categories[row["Task"]]
    color = category_colors[category]
    ax.barh(
        y=row["Task"],
        width=row["Duration"],
        left=row["Start"],
        height=0.5,
        color=color,
        edgecolor="black"
    )

# Add milestones
for name, date in milestones:
    ax.plot(date, name, "rD", markersize=6)
    ax.text(date + pd.Timedelta(days=1), name, date.strftime("%d %b"), va="center", fontsize=8)

# Format date axis
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
plt.xticks(rotation=45)

# Labels and title
ax.set_title("13-Week FYP Gantt Chart (Colour-Coded by WBS Category)", fontsize=14, fontweight="bold")
ax.set_xlabel("Timeline")
ax.set_ylabel("Tasks")
ax.grid(axis="x", linestyle="--", alpha=0.5)
ax.invert_yaxis()

# Legend
handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in category_colors.values()]
labels = list(category_colors.keys())
ax.legend(handles, labels, title="WBS Categories", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()