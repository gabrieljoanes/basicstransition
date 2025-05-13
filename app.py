import streamlit as st
from openai import OpenAI
import json                                        # **ADD**: to parse JSONL

# **ADD**: load your JSONL of examples
@st.cache_data
def load_transitions(path="transitions.jsonl"):
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            examples.append(json.loads(line)["transition"])
    return examples

# **UPDATE**: point at your local file
transition_examples = load_transitions("transitions.jsonl")

# initialize the OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Multi-Transition Generator (GPT-4)")
st.markdown(
    "Paste your text with one or more `TRANSITION` markers. "
    "The app will suggest a 5–10 word phrase for each and rebuild the text."
)

text_input = st.text_area("📝 Text with TRANSITION placeholders", height=300)

if st.button("✨ Generate Transitions"):
    if "TRANSITION" not in text_input:
        st.warning("No `TRANSITION` markers found. Please add at least one.")
    else:
        parts = text_input.split("TRANSITION")
        suggestions = []
        rebuilt = parts[0]

        for i in range(len(parts) - 1):
            prev_ctx = parts[i].strip().split("\n")[-1]
            next_ctx = parts[i+1].lstrip().split("\n")[0]

            # **UPDATE**: build a richer system prompt using your JSONL examples
            system_prompt = (
                "You are a French news assistant that replaces the word TRANSITION "
                "with a short, natural and context-aware phrase (5–10 words) that logically "
                "connects the two sentences. Here are some examples of good transitions:\n"
                + "\n".join(f"- {t}" for t in transition_examples[:10])  # pick first 10
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prev_ctx}\nTRANSITION\n{next_ctx}"}
            ]

            try:
                resp = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=20
                )
                trans = resp.choices[0].message.content.strip()

                # ── **INSERT DUPLICATE-ARTICLE FILTER HERE** ──
                lower_ctx = prev_ctx.lower()
                for art in ("la", "le", "l'", "les"):
                    if lower_ctx.endswith(f" {art}") and trans.lower().startswith(f"{art}"):
                        # remove the leading article + any following space
                        trans = trans[len(art):].lstrip()
            except Exception as e:
                st.error(f"Error generating transition #{i+1}: {e}")
                trans = "[ERROR]"

            suggestions.append(trans)
            rebuilt += trans + parts[i+1]

        st.subheader("✅ Suggested Transitions")
        for idx, trans in enumerate(suggestions, start=1):
            st.markdown(f"{idx}. **{trans}**")

        st.subheader("📄 Final Text")
        st.text_area("Result", rebuilt, height=300)
