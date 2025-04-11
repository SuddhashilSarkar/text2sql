import os
from google import genai
from google.genai import types


def generate_sql_query(user_input, schema):
    """Generates an SQL query using Gemini based on user input and schema."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"

     

    system_instructions = types.Part.from_text(text=f"""You are an expert SQL generator. Your task is to generate a valid SQLite SQL query based on the given database schema and user request. Ensure the query adheres to SQLite syntax.

### Database Schema:
{schema}

### Instructions:
- You are provided with either an optimized schema or full schema. 
- Ensure that all constraints (e.g., NOT NULL, UNIQUE, PRIMARY KEY) are respected.
- Use proper WHERE conditions for filtering data based on user input.
- Do not include table names or columns that are not present in the schema.
- If a column has a UNIQUE constraint (e.g., email, phone), use it to filter queries when applicable.
- If a request is ambiguous, make an educated assumption based on common use cases.
- You can use "*" if needed as optimized schema may not all watys contain all the columns

### Output:
Provide only the SQL query in JSON format.
""")

    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_input)]),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            properties={
                "query": genai.types.Schema(type=genai.types.Type.STRING),
                "response": genai.types.Schema(type=genai.types.Type.STRING),
            },
        ),
        system_instruction=[system_instructions],
    )

    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )

    return response.text  # Returning generated SQL query in JSON format




def generate_sql_chart(user_question, schema):
    # Create the client using the API key from environment variables.
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    model = "gemini-2.0-flash"

    # Build the final user prompt (combining the user question and schema).
    user_prompt = f"""User question: {user_question}
Schema: {schema}

Please generate a SQL query that selects exactly two columns (one categorical/dimension and one numerical/measure) and determine an appropriate 2D chart type.
Guidelines:
- The SQL query must use standard SQL syntax and assume an optimized schema.
- Only return a chart type from [bar, line, pie, scatter]. Default to "bar" if not clearly specified.
- The final response must be a JSON object with exactly two keys: "sql_query" and "chart_type".
"""

    # Construct the system prompt with detailed instructions.
    system_prompt = (
        """You are a text-to-SQL assistant. Your task is to convert a user's natural language question into:\n
        1. A valid SQL query based on the provided database schema that selects exactly two columns: 
        one categorical/dimension and one numerical/measure.\n
        2. The most appropriate 2D chart type (bar, line, pie, or scatter) for visualizing the result.\n\n
        3. The first column would be x_axis, second column would be y_axis
        Guidelines:\n
        - Generate a SQL query that follows standard SQL syntax and works with an optimized schema.\n
        - Default to 'bar' if the request does not clearly indicate one of the supported types.\n
        - Use only the supported chart types: bar, line, pie, or scatter.\n
        - Return the response as a JSON object with exactly two keys: 'sql_query' and 'chart_type'.\n\n
        Example 1:\n
        User: Show me sales per category\n
        Response: {\"sql_query\": \"SELECT category, SUM(sales) FROM orders GROUP BY category\", \"chart_type\": \"bar\"}\n\n
        Example 2:\n
        User: How has temperature changed over time?\n
        Response: {\"sql_query\": \"SELECT date, AVG(temperature) FROM weather_data GROUP BY date\", \"chart_type\": \"line\"}"""
    )

    # Define the content parts for the Gemini API.
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_prompt)],
        )
    ]

    # Configure the response schema and embed the system prompt.
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            required=["sql_query", "chart_type"],
            properties={
                "sql_query": types.Schema(
                    type=types.Type.STRING,
                ),
                "chart_type": types.Schema(
                    type=types.Type.STRING,
                    enum=["bar", "line", "pie", "scatter"],
                ),
            },
        ),
        system_instruction=[types.Part.from_text(text=system_prompt)],
    )

    # Generate the content stream and print each output chunk.
    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )
    return response.text


if __name__ == "__main__":
    schema = ("schema.yaml")  # Load schema from file
    user_query = input("Enter your query: ")  # User input
    sql_query = generate_sql_query(user_query, schema)
    print("\nGenerated SQL Query:\n", sql_query)