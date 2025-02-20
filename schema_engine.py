import sqlite3
import yaml

def get_database_schema(db_path):
    # Connect to the SQLite database.
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Retrieve the names of all tables.
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    
    for table in tables:
        # Retrieve the CREATE TABLE statement for each table.
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        create_stmt = cursor.fetchone()[0]
        
        # Retrieve detailed column information using PRAGMA.
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns_info = cursor.fetchall()
        
        # Build the column details list.
        columns = []
        for col in columns_info:
            # Each col tuple: (cid, name, type, notnull, dflt_value, pk)
            columns.append({
                'cid': col[0],
                'name': col[1],
                'type': col[2],
                'notnull': bool(col[3]),
                'default': col[4],
                'primary_key': bool(col[5])
            })
        
        # Organize the table schema.
        schema[table] = {
            'create_statement': create_stmt,
            'columns': columns
        }
    
    # Close the database connection.
    conn.close()
    return schema

if __name__ == '__main__':
    db_path = "mydb.db"
    schema_data = get_database_schema(db_path)
    
    # Write the schema dictionary to a YAML file.
    with open("schema.yaml", "w") as yaml_file:
        yaml.dump(schema_data, yaml_file, sort_keys=False, default_flow_style=False)
    
    print("Database schema has been written to schema.yaml")
