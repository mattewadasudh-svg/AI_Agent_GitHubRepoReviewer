from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from tools import get_repo_info, list_files, read_file, get_commits, get_open_issues

load_dotenv()

# Step 1: LLM (Google AI Studio, free tier)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Step 2: Instructions for the agent
system_prompt = """
You are a senior code reviewer. The user gives a GitHub repo URL.
Convert it to 'owner/name' format before calling any tool.

Explore the repo yourself:
1. Call get_repo_info and list_files on the root folder.
2. Read the README and 3-10 important files (entry points, config, core logic). Never read more than 10 files.
3. Call get_commits and get_open_issues.

Then write the final report in Markdown with these sections:
Overview, Tech Stack, Code Quality Issues, Commit Activity, Open Issues, Suggested Improvements, Score (out of 10).

Only state what you actually saw through the tools, and name the files you based your points on.
"""

# Step 3: Create the agent
agent = create_agent(
    model=llm,
    tools=[get_repo_info, list_files, read_file, get_commits, get_open_issues],
    system_prompt=system_prompt
)

# Step 4: Test from the terminal
if __name__ == "__main__":
  response = agent.invoke({"messages": [("user", "Review this repo: https://github.com/pallets/click")]})
  print(response["messages"][-1].content)