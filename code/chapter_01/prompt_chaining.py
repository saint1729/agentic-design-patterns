import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

MODEL_ID = os.getenv("MODEL_ID")
llm = ChatOpenAI(temperature=0, model=MODEL_ID)

# --- Prompt 1: Extract Information ---
prompt_extract = ChatPromptTemplate.from_template(
    "Extract the technical specifications from the following text:\n\n{text_input}\n\n"
)

# --- Prompt 2: Transform to JSON ---
prompt_transform = ChatPromptTemplate.from_template(
    "Transform the following specifications into a JSON object with 'cpu', 'memory', and 'storage' as keys:\n\n{specifications}"
)

# -- Build the Chain using LCEL --
# The StrOutputParser() converts the LLM's message output to a simple string.
extraction_chain = prompt_extract | llm | StrOutputParser()

# The full chain passes the output of the extraction chain into the 'specifications' variable for the transformation prompt.
full_chain = ({"specifications": extraction_chain} | prompt_transform | llm | StrOutputParser())

# --- Run the Chain ---
input_text = "The new laptop model featuires a 3.5 GHz octa-core processor, 16 GB of RAM, and a 1 TB NVMe SSD."

# Execute the chain with the input text dictionary
final_result = full_chain.invoke({"text_input": input_text})

print("\n--- Final JSON Output ---")
print(final_result)
