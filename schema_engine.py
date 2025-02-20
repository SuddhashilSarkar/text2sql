import sqlite3
import yaml
import re

def extract_column_definition(create_stmt, column_name):
    """
    A simple regex to capture the column definition segment for a given column.
    This function looks for a segment starting with the column name followed by its definition.
    """
    # Regex explanation:
    # \b{col_name}\b  - match the column name as a whole word
    # \s+             - one or more whitespace
    # ([^,]+)        - capture everything until the next comma or closing parenthesis
    pattern = re.compile(r'\b' + re.escape(column_name) + r'\b\s+([^,)+]+)(?:,|\))', re.IGNORECASE)
    match = pattern.search(create_stmt)
    if match:
        return match.group(1)
    return ""

def get_unique_columns(cursor, table):
    """
    Returns a set of column names that have a unique constraint via an index.
    This inspects all indexes for the table that are marked as unique.
    """
    unique_cols = set()
    cursor.execute("PRAGMA index_list('{}')".format(table))
    indices = cursor.fetchall()
    for index in indices:
        # index tuple: (seq, name, unique, origin, partial)
        index_name = index[1]
        unique_flag = index[2]
        if unique_flag:
            # Get columns for this index.
            cursor.execute("PRAGMA index_info('{}')".format(index_name))
            index_info = cursor.fetchall()
            # If it's a single-column unique index, add that column.
            if len(index_info) == 1:
                col = index_info[0][2]  # The third element is the column name.
                unique_cols.add(col)
    return unique_cols

def get_table_schema(cursor, table):
    """
    For a given table, this function returns a dictionary with a list of columns.
    Each column includes its name, data type, and a simplified list of constraints.
    """
    # Get the CREATE statement.
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table,))
    create_stmt_row = cursor.fetchone()
    create_stmt = create_stmt_row[0] if create_stmt_row else ""
    
    # Get column info via PRAGMA.
    cursor.execute("PRAGMA table_info('{}')".format(table))
    table_info = cursor.fetchall()
    
    # Determine unique columns via indexes.
    unique_columns = get_unique_columns(cursor, table)
    
    columns = []
    for col in table_info:
        # col: (cid, name, type, notnull, dflt_value, pk)
        col_name = col[1]
        col_type = col[2]
        constraints = []
        
        # Add constraints based on PRAGMA.
        if col[3]:
            constraints.append("NOT NULL")
        if col[5]:
            constraints.append("PRIMARY KEY")
        
        # Extract additional info from the CREATE statement.
        col_def = extract_column_definition(create_stmt, col_name)
        if col_def:
            # Check for AUTOINCREMENT.
            if "AUTOINCREMENT" in col_def.upper():
                constraints.append("AUTOINCREMENT")
            # Check for UNIQUE.
            if "UNIQUE" in col_def.upper():
                if "UNIQUE" not in constraints:
                    constraints.append("UNIQUE")
            # Check for a CHECK constraint.
            check_match = re.search(r'CHECK\s*\((.*?)\)', col_def, re.IGNORECASE)
            if check_match:
                check_str = "CHECK(" + check_match.group(1).strip() + ")"
                constraints.append(check_str)
        
        # Add UNIQUE if found in indexes (and not already in constraints).
        if col_name in unique_columns and "UNIQUE" not in constraints:
            constraints.append("UNIQUE")
        
        columns.append({
            "name": col_name,
            "type": col_type,
            "constraints": constraints
        })
    
    return {"columns": columns}

def get_optimized_schema(db_path):
    """
    Connects to the SQLite database, extracts the schema for all user-defined tables
    (excluding system tables), and returns a dictionary suitable for YAML output.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {}
    # Get all tables and filter out system tables (those starting with "sqlite_").
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    
    for table in tables:
        schema[table] = get_table_schema(cursor, table)
    
    conn.close()
    return schema

if __name__ == '__main__':
    db_path = "mydb.db"
    schema_data = get_optimized_schema(db_path)
    
    # Write the optimized schema to schema.yaml.
    with open("schema.yaml", "w") as yaml_file:
        yaml.dump(schema_data, yaml_file, sort_keys=False, default_flow_style=False)
    
    print("Optimized schema has been written to schema.yaml")
