import streamlit as st
from openai import OpenAI

# initialize the new client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Transition Generator (GPT-4)")
st.markdown("Enter two paragraphs. The app will generate a short, natural transition between them.")

para_a = st.text_area("🅰️ Paragraph A", height=150)
para_b = st.text_area("🅱️ Paragraph B", height=150)

if st.button("✨ Generate Transition"):
    prompt = f"{para_a}\nTRANSITION\n{para_b}"
    messages = [
        {"role": "system", "content": "You are a French news assistant that replaces the word TRANSITION with a short, natural and context-aware phrase (5–10 words) that logically connects the two paragraphs."},
        {"role": "user", "content": "Le club de tennis de Rennes a organisé un tournoi pour les jeunes.\nTRANSITION\nUn incendie s’est déclaré dans un entrepôt du centre-ville."},
        {"role": "assistant", "content": "Dans l’actualité locale, un"},
        {"role": "user", "content": "Le marché de Noël d’Arras a accueilli des milliers de visiteurs.\nTRANSITION\nLe conseil municipal a débattu d’un plan pour les transports publics."},
        {"role": "assistant", "content": "Sur le plan politique local, le"},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=20
        )
        transition = response.choices[0].message.content.strip()
        st.success("✅ Suggested Transition:")
        st.markdown(f"**{transition}**")
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
