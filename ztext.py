import os
#dote env
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
