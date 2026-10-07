import streamlit as st
from agent import agent

def get_text(content):
  """Gemini may return a list of blocks; this joins them into plain text."""
  if isinstance(content, list):
    return "".join(block.get("text", "") for block in content if isinstance(block, dict))
  return content

st.title("GitHub Repo Reviewer Agent")
st.caption("Paste a public GitHub repo. The agent explores it on its own and writes a review.")

url = st.text_input("GitHub repo URL", placeholder="https://github.com/owner/repo")

if st.button("Review repo") and url:
  steps = st.status("Agent is working...", expanded=True)
  report = ""

  try:
    for chunk in agent.stream({"messages": [("user", f"Review this repo: {url}")]},
                              stream_mode="values", config={"recursion_limit": 40}):
      msg = chunk["messages"][-1]

      if msg.type == "ai" and msg.tool_calls:
        for call in msg.tool_calls:
          steps.write(f"--> `{call['name']}` {call['args']}")
      elif msg.type == "ai":
        report = get_text(msg.content)

    steps.update(label="Review complete", state="complete", expanded=False)
    st.markdown(report)

  except Exception as e:
    steps.update(label="Something went wrong", state="error")
    st.error(str(e))