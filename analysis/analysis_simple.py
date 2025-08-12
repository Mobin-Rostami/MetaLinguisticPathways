# analysis_simple.py
# Simple analysis script for MetaLinguisticPathways repo
# Expects data at: data/processed/pre_post_tests_simulated_processed.xlsx
# If Excel not found, falls back to CSV with same name.
# Saves figures to: analysis/figures/

from pathlib import Path           # easy path handling (works on Windows/Mac/Linux)
import pandas as pd               # main data library
import matplotlib.pyplot as plt   # plotting library
import seaborn as sns             # nicer default plot styles

# ---------------------------
# 1. File locations (repo-root relative)
# ---------------------------
# __file__ is the current script file (analysis/analysis_simple.py).
# .resolve().parent.parent gives the repo root directory.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Data files (preferred Excel, fallback CSV)
DATA_XLSX = REPO_ROOT / "data" / "processed" / "pre_post_tests_processed.xlsx"
DATA_CSV  = REPO_ROOT / "data" / "processed" / "pre_post_tests_processed.csv"

# Output folder for figures (create if missing)
FIG_DIR = REPO_ROOT / "analysis" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# 2. Load data (Excel preferred)
# ---------------------------
if DATA_XLSX.exists():
    # read_excel reads the first sheet by default into a DataFrame
    df = pd.read_excel(DATA_XLSX)
    print(f"Loaded Excel data from: {DATA_XLSX}")
elif DATA_CSV.exists():
    df = pd.read_csv(DATA_CSV)
    print(f"Loaded CSV data from: {DATA_CSV}")
else:
    raise FileNotFoundError("No data file found. Please add pre_post_tests_processed.xlsx or .csv to data/processed/")

# Quick check that the key columns exist
print("Columns found:", df.columns.tolist())

# ---------------------------
# 3. Ensure Totals & Diffs exist (compute if missing)
# ---------------------------
# expected per-section columns: Pre_A..Pre_F and Post_A..Post_F
sections = ["A","B","C","D","E","F"]
pre_cols = [f"Pre_{s}" for s in sections]
post_cols = [f"Post_{s}" for s in sections]

# compute totals if not present
if "Total_Pre" not in df.columns:
    df["Total_Pre"] = df[pre_cols].sum(axis=1)
if "Total_Post" not in df.columns:
    df["Total_Post"] = df[post_cols].sum(axis=1)
# compute diff and percent change
df["Diff"] = df["Total_Post"] - df["Total_Pre"]
df["Percent_Change"] = df["Diff"] / df["Total_Pre"].replace({0:1}) * 100

# ---------------------------
# 4. Simple summary by Group
# ---------------------------
group_means = df.groupby("Group")[["Total_Pre","Total_Post","Diff","Percent_Change"]].mean().round(2)
print("\nGroup means (Total_Pre, Total_Post, Diff, Percent_Change):")
print(group_means)

# Save summary for quick reporting
group_means.to_csv(REPO_ROOT / "data" / "processed" / "group_summary_stats_simple.csv")

# ---------------------------
# 5. Plot 1 — Average improvement by group
# ---------------------------
plt.figure(figsize=(6,4))
sns.barplot(data=df, x="Group", y="Diff", ci="sd", palette="coolwarm")  # ci="sd" draws error bars for sd
plt.title("Average Improvement in Total Score by Group")
plt.ylabel("Score Difference (Post - Pre)")
plt.xlabel("Group")
plt.tight_layout()
plt.savefig(FIG_DIR / "total_improvement_simple.png")
plt.close()

# ---------------------------
# 6. Plot 2 — Percent change distribution
# ---------------------------
plt.figure(figsize=(6,4))
sns.histplot(data=df, x="Percent_Change", hue="Group", bins=10, kde=True, stat="count", element="step")
plt.title("Distribution of Percent Change in Scores")
plt.xlabel("Percent Change (%)")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.savefig(FIG_DIR / "percent_change_distribution_simple.png")
plt.close()

# ---------------------------
# 7. Plot 3 — Section-by-section improvements (A-F)
# ---------------------------
# Create per-section diff columns (Post - Pre) if not already present
for s in sections:
    diff_col = f"Diff_{s}"
    if diff_col not in df.columns:
        df[diff_col] = df[f"Post_{s}"] - df[f"Pre_{s}"]

# Convert to long form for plotting
section_cols = [f"Diff_{s}" for s in sections]
section_df = df.melt(id_vars=["Student_ID","Group"], value_vars=section_cols,
                     var_name="Section", value_name="Score_Diff")

# Remove the "Diff_" prefix so the x-axis shows A..F
section_df["Section"] = section_df["Section"].str.replace("Diff_","")

plt.figure(figsize=(8,4))
sns.barplot(data=section_df, x="Section", y="Score_Diff", hue="Group", ci=None, palette="coolwarm")
plt.title("Improvement by Section (A–F)")
plt.ylabel("Score Difference (points)")
plt.xlabel("Section")
plt.tight_layout()
plt.savefig(FIG_DIR / "section_improvement_by_group_simple.png")
plt.close()

# ---------------------------
# 8. Final print & save processed data (optional)
# ---------------------------
# Save the dataframe with any computed columns so you can inspect later
df.to_csv(REPO_ROOT / "data" / "processed" / "pre_post_processed_with_diffs_simple.csv", index=False)

print("Done. Figures saved to:", FIG_DIR)
