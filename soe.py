import sqlite3
import sqlparse
import re
from rapidfuzz import fuzz
from typing import Dict, List, Union, Optional
from pathlib import Path

def extract_sqlite_schema(db_path: Union[str, Path]) -> Optional[str]:
    """
    Extracts CREATE TABLE statements from a SQLite database file.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        Combined CREATE TABLE statements as a string, or None if error occurs
    
    Example:
        >>> schema_sql = extract_sqlite_schema("my_database.db")
    """
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            # Get all table creation SQL
            cursor.execute("""
                SELECT sql 
                FROM sqlite_master 
                WHERE type='table' 
                AND sql IS NOT NULL
            """)
            tables = [row[0] for row in cursor.fetchall()]
            return ";\n".join(tables) + ";" if tables else None
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None

def parse_sql_schema(sql_text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Parses SQL CREATE TABLE statements to extract schema details.

    Args:
        sql_text: SQL text containing CREATE TABLE statements

    Returns:
        Dictionary with table names as keys and list of column details as values.
        Each column detail contains 'name', 'datatype', and 'constraints'.

    Example:
        >>> schema = parse_sql_schema('CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR);')
        >>> print(schema)
        {'users': [{'name': 'id', 'datatype': 'INT', 'constraints': 'PRIMARY KEY'},
                  {'name': 'name', 'datatype': 'VARCHAR', 'constraints': ''}]}
    """
    statements = sqlparse.split(sql_text)
    schema = {}

    for statement in statements:
        clean_statement = sqlparse.format(statement, strip_comments=True).strip()
        if not clean_statement.lower().startswith("create table"):
            continue

        table_match = re.search(
            r'create table\s+([^\s(]+)\s*\((.*)\)', 
            clean_statement, 
            re.IGNORECASE | re.DOTALL
        )
        
        if not table_match:
            continue

        table_name, columns_section = table_match.groups()
        columns_raw = re.split(r',\s*(?![^()]*\))', columns_section)
        columns = []

        for col_def in columns_raw:
            col_def = col_def.strip()
            if col_def.lower().startswith(("primary key", "foreign key", "unique", "constraint", "check")):
                continue

            parts = col_def.split()
            if len(parts) >= 2:
                columns.append({
                    'name': parts[0],
                    'datatype': parts[1],
                    'constraints': " ".join(parts[2:]) if len(parts) > 2 else ""
                })

        schema[table_name] = columns
    return schema


def process_query(
    query: str,
    schema: Dict[str, List[Dict[str, str]]],
    column_threshold: int = 50,
    table_threshold: int = 60,
    show_all_columns: bool = False
) -> Dict[str, Dict[str, Union[int, List[Dict[str, str]]]]]:
    """
    Matches natural language query against database schema using fuzzy string matching.

    Args:
        query: Natural language query to process
        schema: Parsed schema from parse_sql_schema
        column_threshold: Minimum match score for columns (0-100)
        table_threshold: Minimum match score for tables (0-100)
        show_all_columns: Return all columns if no matches found

    Returns:
        Dictionary of relevant tables with match scores and columns

    Example:
        >>> schema = parse_sql_schema(...)
        >>> results = process_query("find customer emails", schema)
    """
    results = {}

    for table, columns in schema.items():
        table_score = fuzz.partial_ratio(query.lower(), table.lower())
        matching_columns = [
            col for col in columns
            if fuzz.partial_ratio(query.lower(), col['name'].lower()) > column_threshold
        ]

        if table_score > table_threshold or matching_columns:
            results[table] = {
                'table_score': table_score,
                'columns': matching_columns if matching_columns else (columns if show_all_columns else [])
            }

    return results

def format_as_markdown(
    data: Union[Dict[str, List[Dict[str, str]]], Dict[str, Dict]],
    result_type: str = "schema"
) -> str:
    """
    Formats schema or query results as structured Markdown with bullet points
    
    Args:
        data: Schema or results data to format
        result_type: 'schema' or 'results' formatting style
    
    Returns:
        Formatted Markdown string with tables and bullet points
    """
    md = []
    
    if result_type == "schema":
        md.append("# Database Schema\n")
        for table, columns in data.items():
            md.append(f"## Table: `{table}`")
            for col in columns:
                constraints = f" [{col['constraints']}]" if col['constraints'] else ""
                md.append(f"- **{col['name']}** ({col['datatype']}{constraints})")
            md.append("")  # Add empty line between tables
            
    elif result_type == "results":
        md.append("# Query Results\n")
        if not data:
            return "No matching tables or columns found"
            
        for table, details in data.items():
            md.append(f"## `{table}` (Match Score: {details['table_score']}%)")
            if details['columns']:
                for col in details['columns']:
                    md.append(f"- {col['name']} ({col['datatype']})")
            else:
                md.append("- No specific columns matched - showing all:")
                for col in details.get('columns', []):
                    md.append(f"- {col['name']} ({col['datatype']})")
            md.append("")  # Add empty line between tables
            
    return "\n".join(md)


if __name__ == "__main__":
    test_sql = """
    CREATE TABLE Customers (
        customer_id INT PRIMARY KEY,
        email VARCHAR(255) UNIQUE,
        phone VARCHAR(20),
        registration_date DATE
    );

    CREATE TABLE Transactions (
        transaction_id SERIAL PRIMARY KEY,
        customer_id INT REFERENCES Customers(customer_id),
        amount DECIMAL(10,2) NOT NULL,
        transaction_date TIMESTAMP
    );
    """

    #test_query = "show customer emails with transaction amounts"
    
    # Process data
    #schema = parse_sql_schema(test_sql)
    #results = process_query(test_query, schema)
    
    # Generate formatted output
    #output = [
    #    format_as_markdown(schema, "schema"),
    #    format_as_markdown(results, "results")
    #]
    
    # Print combined report
    #print("\n\n".join(output))
    schema_sql = extract_sqlite_schema("mydb.db")
    print(schema_sql)
