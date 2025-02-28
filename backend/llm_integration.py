import os
from openai import OpenAI

api_key = os.getenv("OPENROUTER_API_KEY", "<OPENROUTER_API_KEY>")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def get_code_suggestions(prompt):
    system_prompt = """You are a Code Suggestions Assistant specialized in providing helpful programming guidance. Your purpose is to offer clear, efficient, and relevant code solutions.

When providing code suggestions:
1. Write clean, well-commented code that follows best practices
2. Explain your reasoning for implementation choices
3. Keep your solutions concise and focused on the specific problem
4. Consider performance, readability, and maintainability
5. Include error handling when appropriate"""

    response = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},],
    )
    return response.choices[0].message.content


def get_error_explanation(error_message):
    system_prompt = """You are an Error Explanations Assistant. Your purpose is to explain error messages in a clear, empathetic manner and provide practical solutions.

When explaining errors:
1. Provide a concise explanation of what the error means
2. Suggest 2-3 likely solutions to resolve the issue
3. Use a supportive, understanding tone
4. Keep your response to a maximum of two paragraphs

Examples:

Error: "ModuleNotFoundError: No module named 'pandas'"
Response: This error occurs because Python can't find the 'pandas' package in your environment. This typically happens when a required library hasn't been installed or isn't accessible in your current Python environment.

To fix this issue, try installing pandas using 'pip install pandas' in your terminal. If you're using a virtual environment, make sure it's activated first. For Jupyter notebooks, you can run '!pip install pandas' in a code cell. If the error persists, check if you're using the correct Python interpreter that has the necessary packages installed.

Error: "TypeError: can only concatenate str (not "int") to str"
Response: This error happens when you're trying to combine a string and an integer using the '+' operator. Python doesn't automatically convert between these types, so operations like 'hello' + 5 will fail because Python doesn't know how to add a number to a text string.

The simplest solution is to convert the integer to a string first using the str() function, like this: 'hello' + str(5). Alternatively, you can use formatted strings such as f"hello {5}" or "hello {}".format(5) to incorporate different data types into a string. Check where you're combining different data types in your code and ensure proper type conversion."""

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-distill-llama-70b:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please explain this error: {error_message}",},],
    )
    return response.choices[0].message.content
