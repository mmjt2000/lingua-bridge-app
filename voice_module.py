"""
Lingua Bridge - Module IA Vocal
Conversation libre (mode cours retire - trop bugge)
STT: Groq Whisper | LLM: Groq | TTS: edge-tts
"""
import os
import io
import json
import tempfile
import asyncio
import re
from pathlib import Path

import streamlit as st
from groq import Groq


# ============================================================
# CONFIG
# ============================================================
def _get_groq_key():
    """Lit la cle Groq depuis 3 parties OU env OU secrets."""
    # 1. Variable d'environnement (local)
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if key:
        return key
    # 2. Secrets Streamlit - 3 parties
    try:
        p1 = st.secrets.get("GROQ_KEY_1", "")
        p2 = st.secrets.get("GROQ_KEY_2", "")
        p3 = st.secrets.get("GROQ_KEY_3", "")
        if p1 and p2 and p3:
            return (p1 + p2 + p3).strip()
    except Exception:
        pass
    # 3. Secrets Streamlit - cle complete
    try:
        key = st.secrets.get("GROQ_API_KEY", "").strip()
        if key:
            return key
    except Exception:
        pass
    return ""


GROQ_API_KEY = _get_groq_key()

MODEL_LLM = "openai/gpt-oss-120b"
MODEL_STT = "whisper-large-v3"
VOICE_TTS = "en-US-AriaNeural"

LESSONS_FILE = Path(__file__).parent / "lessons.json"


# ============================================================
# GROQ CLIENT
# ============================================================
def get_groq_client():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY manquante")
    return Groq(api_key=GROQ_API_KEY)


# ============================================================
# TRANSCRIPTION
# ============================================================
def transcribe_audio(audio_bytes, language="en"):
    if not audio_bytes:
        return ""

    client = get_groq_client()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(
                file=(Path(tmp_path).name, f.read()),
                model=MODEL_STT,
                language=language,
                response_format="text",
            )
        return result.strip() if isinstance(result, str) else getattr(result, "text", "").strip()
    except Exception as e:
        return f"[Erreur transcription: {e}]"
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# ============================================================
# IA - CONVERSATION LIBRE
# ============================================================
def llm_conversation(user_text, history, level="intermediaire", student_name="Student"):
    client = get_groq_client()

    system_prompt = f"""
You are an English conversation tutor for a Spanish-speaking student named {student_name}.
Her English level: {level}.

IMPORTANT CONTEXT:
- The student may be Ingrid, Maryse, or Laeticia (all Spanish-speaking, intermediate level).
- Adapt your vocabulary and topics to her level.

Rules:
- ALWAYS respond in English.
- Keep responses SHORT (2-4 sentences max).
- End your reply with an OPEN QUESTION to keep the conversation going.
- If she makes a grammar mistake, gently correct it: "Nice! Small correction: ... Better: ..."
- If she says something in Spanish, translate it to English and encourage her to repeat.
- Be warm, encouraging, natural - like a friendly tutor.
- Never lecture. Keep it conversational.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-10:]:
        messages.append(h)
    messages.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model=MODEL_LLM,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Erreur LLM: {e}]"


# ============================================================
# TTS
# ============================================================
def text_to_speech(text, voice=VOICE_TTS):
    import edge_tts

    text = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "", text)
    text = text.replace("**", "").replace("__", "").replace("*", "").replace("_", "")

    async def _gen():
        communicate = edge_tts.Communicate(text, voice)
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_path = tmp.name
        tmp.close()
        await communicate.save(tmp_path)
        return tmp_path

    try:
        path = asyncio.run(_gen())
        with open(path, "rb") as f:
            data = f.read()
        os.unlink(path)
        return data
    except Exception as e:
        print(f"[TTS ERREUR] {e}")
        return None


# ============================================================
# LOAD LESSONS
# ============================================================
def load_lessons():
    if not LESSONS_FILE.exists():
        return {}
    with open(LESSONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# UI
# ============================================================
def render_voice_module():
    st.markdown("---")
    st.markdown("## 🎤 Práctica con IA")
    st.markdown("*Habla en inglés, la IA te escucha, corrige y responde con voz.*")

    if not GROQ_API_KEY:
        st.error("⚠️ GROQ_API_KEY n'est pas configurée.")
        try:
            st.write("**Debug** — clés dispo :", list(st.secrets.keys()))
            try:
                v1 = st.secrets["GROQ_KEY_1"]
                st.write("GROQ_KEY_1 =", repr(v1))
            except Exception as e1:
                st.write("GROQ_KEY_1 erreur :", str(e1))
        except Exception as e:
            st.write("Erreur secrets :", str(e))
        return

    # Mode unique : Conversation libre (Lección del día retirée - trop buggée)
    render_free_conversation()


def render_free_conversation():
    st.markdown("### 💬 Conversación libre")

    if "conv_history" not in st.session_state:
        st.session_state.conv_history = []
    if "conv_last_audio" not in st.session_state:
        st.session_state.conv_last_audio = None

    for msg in st.session_state.conv_history[-8:]:
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"]):
            st.markdown(f"{role_icon} {msg['content']}")

    st.markdown("**🎤 Habla:**")
    audio_file = st.audio_input("Graba tu respuesta", key="conv_audio")

    if audio_file is not None:
        wav_data = audio_file.getvalue()
        if wav_data and wav_data != st.session_state.conv_last_audio:
            st.session_state.conv_last_audio = wav_data

            with st.spinner("Transcribiendo..."):
                user_text = transcribe_audio(wav_data, language="en")

            if user_text and not user_text.startswith("[Erreur"):
                st.session_state.conv_history.append({"role": "user", "content": user_text})
                with st.chat_message("user"):
                    st.markdown(f"🧑 {user_text}")

                with st.spinner("La IA está pensando..."):
                    user_info = st.session_state.get("user", {})
                    student_name = user_info.get("full_name", "Student").split()[0]
                    reply = llm_conversation(
                        user_text,
                        st.session_state.conv_history,
                        "intermediaire",
                        student_name=student_name,
                    )
                st.session_state.conv_history.append({"role": "assistant", "content": reply})

                with st.chat_message("assistant"):
                    st.markdown(f"🤖 {reply}")

                audio_reply = text_to_speech(reply)
                if audio_reply:
                    st.audio(audio_reply, format="audio/mp3", autoplay=True)

    if st.button("🔄 Nueva conversación", key="conv_reset"):
        st.session_state.conv_history = []
        st.session_state.conv_last_audio = None
        st.rerun()