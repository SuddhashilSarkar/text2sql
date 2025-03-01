import streamlit as st
import sqlite3
import json
import re
import pandas as pd
from ai_engine import load_schema, generate_sql_query  # Import your functions

# Configure the Streamlit page layout
st.set_page_config(page_title="Text2SQL Query Generator", layout="wide")

# Sidebar for instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
Enter your natural language query to generate a SQL query, execute it on the database, and display results.
For example: **Show me all students with CGPA above 3.5.**
""")

# Custom CSS for responsive table (optional)
st.markdown(
    """
    <style>
    .dataframe-container {
        overflow-x: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main content
st.title("Text2SQL Query Generator")
st.write("Enter your query below:")

user_input = st.text_area("Your Query", placeholder="e.g., Show me all students with CGPA above 3.5", height=100)

if st.button("Submit"):
    if not user_input.strip():
        st.warning("Please enter a query.")
    else:
        st.info("Generating SQL query...")
        # Load the schema from file
        schema = load_schema("schema.yaml")
        
        # Generate SQL query using the LLM function
        response_text = generate_sql_query(user_input, schema)
        st.write("**LLM Raw Response:**")
        st.code(response_text, language="json")
        
        # Extract the JSON part from the response using regex
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                data = json.loads(json_str)
                sql_query = data.get("query")
                if not sql_query:
                    st.error("No SQL query found in the response.")
                else:
                    st.success("Extracted SQL Query:")
                    st.code(sql_query, language="sql")
                    
                    # Execute the SQL query against your SQLite database
                    try:
                        conn = sqlite3.connect("mydb.db")
                        cursor = conn.cursor()
                        cursor.execute(sql_query)
                        rows = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        conn.close()
                        
                        if rows:
                            st.success("Query executed successfully. Results:")
                            df = pd.DataFrame(rows, columns=columns)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("Query executed successfully but returned no results.")
                    except Exception as e:
                        st.error(f"Error executing SQL query: {e}")
            except json.JSONDecodeError as e:
                st.error(f"Error parsing JSON: {e}")
        else:
            st.error("Failed to extract JSON from the LLM response.")
