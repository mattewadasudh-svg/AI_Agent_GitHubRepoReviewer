import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

def gh(path, raw=False):
  """Helper: call the GitHub API. Returns JSON/text, or an error string."""
  headers = {}
  if os.getenv("GITHUB_TOKEN"):
    headers["Authorization"] = f"Bearer {os.getenv('GITHUB_TOKEN')}"
  if raw:
    headers["Accept"] = "application/vnd.github.raw+json"

  response = requests.get(f"https://api.github.com/repos/{path}", headers=headers, timeout=15)

  if response.status_code != 200:
    return f"Error {response.status_code}: {response.json().get('message', 'request failed')}"
  return response.text if raw else response.json()

@tool
def get_repo_info(repo: str) -> str:
  """
  Gets basic info of a GitHub repo: description, language, stars, forks, license.
  repo must be in 'owner/name' format, e.g. 'pallets/flask'
  """
  data = gh(repo)
  if isinstance(data, str): return data
  license_name = (data["license"] or {}).get("name")
  return (f"{data['full_name']}: {data['description']} | language: {data['language']} | "
          f"stars: {data['stargazers_count']} | forks: {data['forks_count']} | license: {license_name}")

@tool
def list_files(repo: str, path: str = "") -> str:
  """
  Lists files and folders at a path inside the repo. Use path='' for the root folder.
  """
  data = gh(f"{repo}/contents/{path}")
  if isinstance(data, str): return data
  if isinstance(data, dict): return "This path is a file, use read_file instead."
  return "\n".join(f"{item['type']}: {item['path']}" for item in data[:100])

@tool
def read_file(repo: str, path: str) -> str:
  """
  Reads the text content of one file in the repo (first 4000 characters only).
  """
  return gh(f"{repo}/contents/{path}", raw=True)[:4000]

@tool
def get_commits(repo: str) -> str:
  """
  Gets the 10 most recent commits (date, author, message).
  """
  data = gh(f"{repo}/commits?per_page=10")
  if isinstance(data, str): return data
  return "\n".join(f"{c['commit']['author']['date'][:10]} | {c['commit']['author']['name']} | "
                   f"{c['commit']['message'].splitlines()[0]}" for c in data)

@tool
def get_open_issues(repo: str) -> str:
  """
  Gets up to 10 open issues of the repo (pull requests excluded).
  """
  data = gh(f"{repo}/issues?state=open&per_page=10")
  if isinstance(data, str): return data
  issues = [i for i in data if "pull_request" not in i]
  if not issues: return "No open issues."
  return "\n".join(f"#{i['number']} {i['title']} ({i['comments']} comments)" for i in issues)