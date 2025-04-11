import streamlit as st
from soe import extract_sqlite_schema, parse_sql_schema, process_query, format_as_markdown
from pr_engine import recognize_protocol
from ai_engine import generate_sql_query, generate_sql_chart
import sqlite3
import pandas as pd
from chart_engine import ChartEngine

# Initialize Streamlit session state

def execute_sql(db_path, query):
    try:
        conn = sqlite3.connect(db_path)
        if query.strip().lower().startswith("select"):
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        else:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            conn.close()
            return f"Query executed successfully (non-SELECT)."
    except sqlite3.Error as e:
        return f"SQLite error: {e}"

def handle_protocol(protocol: str, original_query: str, improved_query: str, db_path: str):
    """Streamlit-integrated protocol handler"""
    # Retrieve schema
    create_statements = extract_sqlite_schema(db_path)
    if not create_statements:
        st.error("Error: Unable to extract schema from the database.")
        return

    schema = parse_sql_schema(create_statements)
    
    with st.container():
        st.subheader("Processing Results")
        
        if protocol in ["10", "11"]:
            query_results = process_query(improved_query, schema)
            md_schema = format_as_markdown(query_results, result_type="results")
            sql_query = generate_sql_query(improved_query, md_schema)
            
            with st.expander("Generated SQL"):
                st.code(sql_query["sql_query"])
            
            sql_result = execute_sql(db_path, sql_query["sql_query"])
            
            if isinstance(sql_result, pd.DataFrame):
                st.dataframe(sql_result)
            else:
                st.write(sql_result)

        elif protocol in ["12", "13"]:
            query_results = process_query(improved_query, schema)
            md_schema = format_as_markdown(query_results, result_type="results")
            sql_query = generate_sql_chart(improved_query, md_schema)
            
            with st.expander("Generated SQL"):
                st.code(sql_query["sql_query"])
            
            sql_result = execute_sql(db_path, sql_query["sql_query"])
            fig = ChartEngine.generate_chart(sql_result, chart_type=sql_query["chart_type"])
            st.pyplot(fig)

        elif protocol == "21":
            full_md_schema = format_as_markdown(schema, result_type="schema")
            sql_query = generate_sql_query(improved_query, full_md_schema)
            
            with st.expander("Generated SQL"):
                st.code(sql_query["sql_query"])
            
            sql_result = execute_sql(db_path, sql_query["sql_query"])
            if "error" not in str(sql_result).lower():
                st.success("✅ Successfully inserted data")
            else:
                st.error(f"❌ Insertion error: {sql_result}")

        elif protocol in ["22", "23"]:
            optimized_schema = process_query(improved_query, schema)
            md_schema = format_as_markdown(optimized_schema, result_type="results")
            sql_query = generate_sql_query(improved_query, md_schema)
            
            with st.expander("Generated SQL"):
                st.code(sql_query["sql_query"])
            
            sql_result = execute_sql(db_path, sql_query["sql_query"])
            if "error" not in str(sql_result).lower():
                st.success("✅ Operation successful")
            else:
                st.error(f"❌ Operation error: {sql_result}")

        elif protocol in ["30", "31", "32", "33", "34"]:
            table_names = list(schema.keys())
            tables_md = "\n".join([f"- {table}" for table in table_names])
            p = tables_md
            if protocol == "32":
                optimized_schema = process_query(improved_query, schema)
                md_schema = format_as_markdown(optimized_schema, result_type="results")
                p = md_schema
            
            sql_query = generate_sql_query(improved_query, p)
            
            with st.expander("Generated SQL"):
                st.code(sql_query["sql_query"])
            
            sql_result = execute_sql(db_path, sql_query["sql_query"])
            st.write(sql_result)

        elif protocol.startswith("40"):
            if protocol == "41":
                table_names = list(schema.keys())
                st.subheader("Available Tables")
                st.write("\n".join([f"- {table}" for table in table_names]))
            elif protocol == "42":
                table = improved_query.strip()
                if table in schema:
                    md_schema = format_as_markdown({table: schema[table]}, result_type="schema")
                    st.markdown(md_schema)
                else:
                    st.error(f"Table '{table}' not found")
            elif protocol == "40":
                full_md_schema = format_as_markdown(schema, result_type="schema")
                st.markdown(full_md_schema)
        else:
            st.error("Unsupported protocol code.")

# Streamlit UI
def main():
    st.title("Natural Language to SQL Interface")
    
    db_path = st.text_input("Database Path", "mydb.db")
    user_query = st.text_input("Enter your query", "find all customers")
    
    if st.button("Execute"):
        with st.spinner("Processing your query..."):
            # Classify protocol
            classification = recognize_protocol(user_query)
            protocol = classification["protocol"]
            improved_query = classification["improved_query"]
            
            st.subheader("Query Analysis")
            cols = st.columns(3)
            cols[0].metric("Original Query", user_query)
            cols[1].metric("Improved Query", improved_query)
            cols[2].metric("Protocol Code", protocol)
            
            handle_protocol(
                protocol=protocol,
                original_query=user_query,
                improved_query=improved_query,
                db_path=db_path
            )

if __name__ == "__main__":
    main()