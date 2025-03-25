import streamlit as st
import sqlite3
import pandas as pd
import json
from ai_engine import load_schema, generate_sql_and_chart_params, parse_llm_response
from chart_engine import ChartEngine

# Configure the Streamlit page layout
st.set_page_config(page_title="Text2SQL with Charts", layout="wide")

# Sidebar for instructions
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Enter your query in natural language (e.g., "Show sales by region")
2. We'll generate and execute the SQL
3. Results will be shown as both a table and chart
""")

# Main content
st.title("Text2SQL with Charts")
user_input = st.text_area("Enter your query:", placeholder="e.g., Show monthly revenue trends", height=100)

if st.button("Generate & Execute"):
    if not user_input.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Generating SQL and chart parameters..."):
            try:
                # Load schema and generate SQL + chart params
                schema = load_schema("schema.yaml")
                llm_response = generate_sql_and_chart_params(user_input, schema)
                sql, chart_params = parse_llm_response(llm_response)
                
                # Display LLM output in expandable section
                with st.expander("See complete LLM output", expanded=False):
                    st.json(llm_response)  # Display raw LLM response as JSON
                
                # Display generated SQL
                st.success("Generated SQL Query:")
                st.code(sql, language="sql")

                # Execute query
                conn = sqlite3.connect("mydb.db")
                cursor = conn.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                conn.close()

                if rows:
                    df = pd.DataFrame(rows, columns=columns)
                    
                    # Display data and chart side-by-side
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.success("Query Results")
                        st.dataframe(df, use_container_width=True)
                    
                    with col2:
                        st.success("Visualization")
                        fig = ChartEngine.generate_chart(
                            sql_results=rows,
                            chart_params=chart_params,
                            column_names=columns
                        )
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("Could not generate chart. Showing raw data.")
                            st.dataframe(df)
                else:
                    st.info("Query executed successfully but returned no results.")

            except Exception as e:
                st.error(f"Error: {str(e)}")