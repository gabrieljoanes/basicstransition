import streamlit as st
from openai import OpenAI

# initialize the OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Multi-Transition Generator (GPT-4)")
st.markdown(
    "Paste your text with one or more `TRANSITION` markers. "
    "The app will suggest a 5–10 word phrase for each and rebuild the text."
)

# single text area for the full text
text_input = st.text_area("📝 Text with TRANSITION placeholders", height=300)

if st.button("✨ Generate Transitions"):
    if "TRANSITION" not in text_input:
        st.warning("No `TRANSITION` markers found. Please add at least one.")
    else:
        parts = text_input.split("TRANSITION")
        suggestions = []
        rebuilt = parts[0]

        for i in range(len(parts) - 1):
            # grab the end of the previous chunk and the start of the next
            prev_ctx = parts[i].strip().split("\n")[-1]
            next_ctx = parts[i+1].lstrip().split("\n")[0]

            # ask GPT-4 for a single transition
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a French news assistant that replaces the "
                        "word TRANSITION with a short, natural and context-aware "
                        "phrase (5–10 words) that logically connects the two sentences."
                    )
                },
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

            suggestions.append(trans)
            # stitch it back together
            rebuilt += trans + parts[i+1]

        # show each suggestion
        st.subheader("✅ Suggested Transitions")
        for idx, trans in enumerate(suggestions, start=1):
            st.markdown(f"{idx}. **{trans}**")

        # show final rebuilt text
        st.subheader("📄 Final Text")
        st.text_area("Result", rebuilt, height=300)
