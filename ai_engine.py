import os
import json
import yaml
from google import genai
from google.genai import types

def load_schema(schema_path="schema.yaml"):
    """Loads the database schema from a YAML file."""
    with open(schema_path, "r") as file:
        return yaml.safe_load(file)

def generate_sql_and_chart_params(user_input, schema):
    """Generates SQL query and chart parameters using Gemini."""
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    model = "gemini-2.0-flash"

    schema_text = yaml.dump(schema, default_flow_style=False)

    system_instructions = types.Part.from_text(text=f"""You are an expert SQL generator. Your task is to:
1. Generate a valid SQLite SQL query based on the schema and user request
2. Suggest chart parameters for visualizing the results

### Database Schema:
{schema_text}

### Instructions:
- Use only tables/columns from the schema
- For chart parameters:
  - Default to bar chart if unspecified
  - Identify x-axis (categorical) and y-axis (numerical) columns
  - Use column aliases from the SELECT clause
- Output format:
{{
  "query": "SELECT...",
  "chart_type": "bar|line|pie",
  "x_column": "column_name",
  "y_column": "column_name"
}}""")

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
                "chart_type": genai.types.Schema(type=genai.types.Type.STRING),
                "x_column": genai.types.Schema(type=genai.types.Type.STRING),
                "y_column": genai.types.Schema(type=genai.types.Type.STRING)
            },
        ),
        system_instruction=[system_instructions],
    )

    response = client.models.generate_content(
        model=model, contents=contents, config=generate_content_config
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "query": "SELECT * FROM table",
            "chart_type": "bar",
            "x_column": "column1",
            "y_column": "column2"
        }

def parse_llm_response(response: dict) -> tuple:
    """Extracts SQL and chart parameters from LLM response."""
    return (
        response.get("query", "SELECT * FROM table"),
        {
            "chart_type": response.get("chart_type", "bar"),
            "x": response.get("x_column", "column1"),
            "y": response.get("y_column", "column2")
        }
    )

if __name__ == "__main__":
    schema = load_schema("schema.yaml")
    user_query = input("Enter your query: ")
    response = generate_sql_and_chart_params(user_query, schema)
    sql, chart_params = parse_llm_response(response)
    
    print("\nGenerated SQL:\n", sql)
    print("\nChart Parameters:\n", chart_params)