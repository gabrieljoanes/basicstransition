import streamlit as st
from openai import OpenAI
import json
import re

@st.cache_data
def load_transitions(path="transitions.jsonl"):
    examples = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            examples.append(json.loads(line)["transition"])
    return examples

transition_examples = load_transitions("transitions.jsonl")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Multi-Transition Generator (GPT-4)")
st.markdown(
    "Paste your text with one or more `TRANSITION` markers. "
    "The app will suggest a 5–10 word phrase for each, apply post-processing rules, "
    "and rebuild the text with grammar & punctuation checks."
)

text_input = st.text_area("📝 Text with TRANSITION placeholders", height=300)

if st.button("✨ Generate Transitions"):
    if "TRANSITION" not in text_input:
        st.warning("No `TRANSITION` markers found. Please add at least one.")
    else:
        parts = text_input.split("TRANSITION")
        suggestions = []
        rebuilt = parts[0]

        used_keywords = set()
        used_transitions = set()

        for i in range(len(parts) - 1):
            prev_ctx = parts[i].strip().split("\n")[-1]
            next_ctx = parts[i+1].lstrip().split("\n")[0]

            # Special header handling: pass through after double line-break
            if prev_ctx.strip() == "A savoir également dans votre département":
                # Remove any trailing whitespace, add two line breaks, then the next content
                rebuilt = rebuilt.rstrip() + "\n\n" + parts[i+1]
                continue

            # Build system prompt with example transitions
            system_prompt = (
                "You are a French news assistant that replaces the word TRANSITION "
                "with a short, natural and context-aware phrase (5–10 words) that logically "
                "connects the two sentences. Here are some examples:\n"
                + "\n".join(f"- {t}" for t in transition_examples[:10])
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
            except Exception as e:
                st.error(f"Error generating transition #{i+1}: {e}")
                trans = "[ERROR]"

            # 1) Remove duplicate trailing article
            lower_ctx = prev_ctx.lower()
            for art in ("la", "le", "l'", "les"):
                if lower_ctx.endswith(f" {art}") and trans.lower().startswith(f"{art}"):
                    trans = trans[len(art):].lstrip()
                    break

            # 2) Lowercase after comma
            if "," in trans:
                head, tail = trans.split(",", 1)
                tail = tail.lstrip()
                if tail:
                    tail = tail[0].lower() + tail[1:]
                trans = f"{head}, {tail}"

            # 3) “Enfin” only as the last transition
            is_last = (i == len(parts) - 2)
            if trans.lower().startswith("enfin") and not is_last:
                trans = trans.replace("Enfin", "De plus", 1)

            # 4) “Par ailleurs” only once
            if "par ailleurs" in trans.lower():
                if "par ailleurs" in used_keywords:
                    trans = trans.replace("Par ailleurs", "De plus", 1)
                else:
                    used_keywords.add("par ailleurs")

            # 5) Avoid exact repeats
            norm = trans.lower()
            if norm in used_transitions:
                trans = trans + " (suite)"
            used_transitions.add(norm)

            suggestions.append(trans)
            rebuilt += trans + parts[i+1]

        # === FINAL CLEANUP ON FULL TEXT ===
        # a) Lowercase article after any comma
        rebuilt = re.sub(
            r',\s+(Le|La|L\')',
            lambda m: ', ' + m.group(1).lower(),
            rebuilt
        )
        # b) Fix duplicated “et de Les” → “et les”
        rebuilt = re.sub(r'\bet de Les\b', 'et les', rebuilt)
        # c) Collapse multiple spaces
        rebuilt = re.sub(r'\s{2,}', ' ', rebuilt)

        st.subheader("✅ Suggested Transitions")
        for idx, t in enumerate(suggestions, start=1):
            st.markdown(f"{idx}. **{t}**")

        st.subheader("📄 Final Text")
        st.text_area("Result", rebuilt, height=300)
