"""
Student Average Marks Calculator
Reads student marks from a CSV, calculates total, average and grade,
and writes the result to an output CSV.
"""

import logging
import sys

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

SUBJECTS = ["maths", "science", "english", "social", "telugu"]
OUTPUT_COLUMNS = ["student_id", "student_name", "total", "average", "grade"]


def get_grade(average: float) -> str:
    """Return the grade for a given average."""
    if average >= 90:
        return "A+"
    elif average >= 76:
        return "A"
    elif average >= 60:
        return "B"
    elif average >= 40:
        return "C"
    return "Fail"


def handle_missing_marks(df: pd.DataFrame) -> pd.DataFrame:
    """Replace missing marks with 0 and log a warning for each one."""
    df = df.copy()
    for subject in SUBJECTS:
        missing_rows = df[df[subject].isna()]
        for _, row in missing_rows.iterrows():
            logger.warning(
                "Missing '%s' marks for student_id=%s (%s). Treating as 0.",
                subject, row["student_id"], row["student_name"],
            )
        df[subject] = df[subject].fillna(0)
    return df


def calculate_results(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total, average and grade for each student."""
    missing_cols = [c for c in ["student_id", "student_name"] + SUBJECTS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Input is missing required columns: {missing_cols}")

    df = handle_missing_marks(df)
    df["total"] = df[SUBJECTS].sum(axis=1)
    df["average"] = (df["total"] / len(SUBJECTS)).round(2)
    df["grade"] = df["average"].apply(get_grade)
    return df[OUTPUT_COLUMNS]


def main(input_file: str = "students_marks.csv",
         output_file: str = "student_results.csv") -> None:
    logger.info("Reading input file: %s", input_file)
    df = pd.read_csv(input_file)

    results = calculate_results(df)

    results.to_csv(output_file, index=False)
    logger.info("Results written to %s (%d students)", output_file, len(results))
    print(results.to_string(index=False))


if __name__ == "__main__":
    # Optional: python student_avg.py input.csv output.csv
    args = sys.argv[1:]
    main(*args)
