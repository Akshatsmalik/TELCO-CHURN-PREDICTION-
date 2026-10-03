"""
run_sql.py

Executes SQL files against the SQLite churn.db database.
Handles DDL/DML statements for star schema creation and SELECT queries for churn analysis.
Prints readable result tables and saves query outputs to the `outputs/` directory.
"""

from pathlib import Path
import re
import sqlite3
import pandas as pd


def parse_sql_statements(sql_content: str) -> list[dict]:
    """
    Parses a SQL file into individual statements, capturing query titles from comment headers.
    
    Returns:
        list of dicts containing 'title' and 'sql' for each statement.
    """
    lines = sql_content.splitlines()
    statements = []
    current_title = ""
    current_lines = []

    for line in lines:
        stripped = line.strip()
        
        # Capture query title from lines starting with '-- Query'
        if stripped.startswith("-- Query"):
            current_title = stripped.lstrip("-").strip()
            continue

        # Skip other comment lines before statement starts
        if stripped.startswith("--") and not current_lines:
            if not current_title:
                current_title = stripped.lstrip("-").strip()
            continue

        if stripped:
            current_lines.append(line)

        # Semicolon marks the end of a SQL statement
        if ";" in line:
            full_sql = "\n".join(current_lines).strip()
            if full_sql:
                statements.append({
                    "title": current_title if current_title else "Query",
                    "sql": full_sql
                })
            current_lines = []
            current_title = ""

    return statements


def execute_sql_file(sql_file_path: Path, db_path: Path = None, output_dir: Path = None) -> list:
    """
    Executes all SQL statements in a given .sql file against churn.db.
    Prints SELECT results as formatted tables and writes CSV files to outputs/.
    
    Args:
        sql_file_path: Path to the .sql file.
        db_path: Path to churn.db SQLite database.
        output_dir: Path to directory where CSV outputs are saved.
        
    Returns:
        list of pandas DataFrames for SELECT queries.
    """
    project_root = Path(__file__).parent.parent
    if db_path is None:
        db_path = project_root / "churn.db"
    if output_dir is None:
        output_dir = project_root / "outputs"
        
    output_dir.mkdir(parents=True, exist_ok=True)

    if not sql_file_path.exists():
        raise FileNotFoundError(f"SQL file not found at {sql_file_path}")

    sql_content = sql_file_path.read_text(encoding="utf-8")
    parsed_statements = parse_sql_statements(sql_content)

    results = []

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for idx, stmt_info in enumerate(parsed_statements, 1):
            title = stmt_info["title"]
            sql_text = stmt_info["sql"]

            # Determine if statement is a SELECT query
            first_word = sql_text.lstrip().split()[0].upper() if sql_text.lstrip() else ""

            if first_word in ("SELECT", "WITH"):
                # Execute query into pandas DataFrame
                df = pd.read_sql_query(sql_text, conn)
                results.append((title, df))

                # Display table in terminal
                print("\n" + "=" * 60)
                print(f" {title} ")
                print("=" * 60)
                print(df.to_string(index=False))
                print("-" * 60)

                # Generate clean filename for individual CSV export
                sanitised_title = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower()).strip('_')
                csv_filename = output_dir / f"{sanitised_title}.csv"
                df.to_csv(csv_filename, index=False)
                print(f"[EXPORT] Saved query output to outputs/{csv_filename.name}")

            else:
                # Execute DDL/DML statement (CREATE, INSERT, DROP, etc.)
                cursor.executescript(sql_text)

        conn.commit()

    # Save consolidated results for analysis file if SELECT queries were run
    if results:
        combined_csv = output_dir / "analysis_results.csv"
        with open(combined_csv, "w", encoding="utf-8") as f:
            for title, df in results:
                f.write(f"# {title}\n")
                df.to_csv(f, index=False)
                f.write("\n\n")
        print(f"\n[SUMMARY] Combined analysis results written to outputs/analysis_results.csv")

    return results


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    schema_sql = project_root / "sql" / "01_create_star_schema.sql"
    analysis_sql = project_root / "sql" / "02_churn_analysis.sql"
    
    print("--- Executing Star Schema DDL ---")
    execute_sql_file(schema_sql)
    
    print("\n--- Executing Churn Analysis ---")
    execute_sql_file(analysis_sql)
