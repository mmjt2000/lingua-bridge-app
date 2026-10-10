"""
Lingua Bridge - Module IA Vocal
Conversation libre + Mode cours guide
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
# TRANSCRIPTION (audio -> texte)
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
def llm_conversation(user_text, history, level="intermediaire"):
    client = get_groq_client()

    system_prompt = f"""
You are an English conversation tutor for a Spanish-speaking student named Ingrid.
Her English level: {level}.

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
# IA - MODE COURS
# ============================================================
def llm_play_slide(slide, user_input, history):
    client = get_groq_client()

    slide_num = slide.get("slide_num", "?")
    title = slide.get("title", "")
    role = slide.get("role", "")
    script = slide.get("script", "")

    system_prompt = f"""
You are Ingrid's English teacher, following a STRICT lesson plan.

Slide {slide_num}: {title}
Role: {role}
Instructions: {script}

Rules:
- If COVER/OVERVIEW: read it, greet her, set the objective. Ask if she's ready.
- If WARM-UP: ask the warm-up questions one by one, wait for her answers.
- If VOCABULARY: say the word, ask her to repeat. Then ask her to use it in a sentence.
- If COMMON MISTAKES: show the mistake, ask "Is this correct?", wait for her answer.
- If GRAMMAR: explain briefly, give 2 examples, ask her to make 2 sentences.
- If EXERCISES/YOUR TURN: give the first exercise, wait for her answer.
- Always end with a QUESTION or a REQUEST for her to speak.

Start by asking your first question or saying your first line. Keep it SHORT.
""".strip()

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-6:]:
        messages.append(h)
    if user_input:
        messages.append({"role": "user", "content": user_input})
    else:
        messages.append({"role": "user", "content": "(start the slide)"})

    try:
        response = client.chat.completions.create(
            model=MODEL_LLM,
            messages=messages,
            temperature=0.6,
            max_tokens=400,
        )
        reply = response.choices[0].message.content
        should_advance = "next slide" in reply.lower() or "move on" in reply.lower()
        return reply, should_advance
    except Exception as e:
        return f"[Erreur LLM: {e}]", False


# ============================================================
# TTS
# ============================================================
def text_to_speech(text, voice=VOICE_TTS):
    import edge_tts

    # Nettoie emojis et markdown
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
        # DEBUG temporaire
                try:
            st.write("**Debug 1** — clés:", list(st.secrets.keys()))
            st.write("**Debug 2** — type secrets:", type(st.secrets).__name__)
            # Test d'accès direct
            try:
                v1 = st.secrets["GROQ_KEY_1"]
                st.write("**Debug 3** — GROQ_KEY_1 valeur brute:", repr(v1))
            except KeyError:
                st.write("**Debug 3** — GROQ_KEY_1 : KeyError")
            except Exception as e2:
                st.write("**Debug 3** — erreur:", str(e2))
        except Exception as e:
            st.write("Erreur lecture secrets :", str(e))
        return

    mode = st.radio(
        "**Elige el modo:**",
        ["💬 Conversación libre", "📚 Lección del día"],
        horizontal=True,
        key="voice_mode",
    )

    if mode == "💬 Conversación libre":
        render_free_conversation()
    else:
        render_guided_lesson()


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
                    reply = llm_conversation(user_text, st.session_state.conv_history, "intermediaire")
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


def render_guided_lesson():
    st.markdown("### 📚 Lección del día")

    lessons = load_lessons()
    if not lessons:
        st.warning("⚠️ No se encontró lessons.json.")
        return

    lesson_keys = sorted(lessons.keys())
    lesson_labels = [f"Class {lessons[k]['class_num']:02d}" for k in lesson_keys]
    selected_idx = st.selectbox(
        "**Elige una lección:**",
        range(len(lesson_keys)),
        format_func=lambda i: lesson_labels[i],
        key="guided_lesson",
    )
    lesson_key = lesson_keys[selected_idx]
    lesson = lessons[lesson_key]
    slides = lesson["slides"]

    state_key = f"guided_{lesson_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {"slide_idx": 0, "history": [], "started": False}

    state = st.session_state[state_key]
    slide_idx = state["slide_idx"]

    if slide_idx >= len(slides):
        st.success("🎉 ¡Lección completada! Excelente trabajo, Ingrid.")
        if st.button("🔄 Empezar de nuevo"):
            st.session_state[state_key] = {"slide_idx": 0, "history": [], "started": False}
            st.rerun()
        return

    slide = slides[slide_idx]
    progress = (slide_idx + 1) / len(slides)
    st.progress(progress, text=f"Slide {slide_idx+1}/{len(slides)} - {slide.get('title', '')}")
    st.info(f"**Slide {slide_idx+1}** · Role: {slide.get('role', '')} · Duration: {slide.get('duration', '')}")

    for msg in state["history"][-6:]:
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"]):
            st.markdown(f"{role_icon} {msg['content']}")

    if not state.get("started"):
        if st.button("▶️ Empezar esta slide", key=f"start_{slide_idx}"):
            with st.spinner("La IA empieza..."):
                reply, _ = llm_play_slide(slide, "", state["history"])
            state["history"].append({"role": "assistant", "content": reply})
            state["started"] = True
            st.session_state[state_key] = state

            with st.chat_message("assistant"):
                st.markdown(f"🤖 {reply}")
            audio_reply = text_to_speech(reply)
            if audio_reply:
                st.audio(audio_reply, format="audio/mp3", autoplay=True)
            st.rerun()
        return

    st.markdown("**🎤 Tu respuesta:**")
    audio_file = st.audio_input("Graba tu respuesta", key=f"guided_audio_{slide_idx}")

    if audio_file is not None:
        wav_data = audio_file.getvalue()
        if wav_data:
            with st.spinner("Transcribiendo..."):
                user_text = transcribe_audio(wav_data, language="en")

            if user_text and not user_text.startswith("[Erreur"):
                state["history"].append({"role": "user", "content": user_text})
                with st.chat_message("user"):
                    st.markdown(f"🧑 {user_text}")

                with st.spinner("La IA responde..."):
                    reply, _ = llm_play_slide(slide, user_text, state["history"])
                state["history"].append({"role": "assistant", "content": reply})

                with st.chat_message("assistant"):
                    st.markdown(f"🤖 {reply}")

                audio_reply = text_to_speech(reply)
                if audio_reply:
                    st.audio(audio_reply, format="audio/mp3", autoplay=True)

                st.session_state[state_key] = state
                st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Slide précédente", key=f"prev_{slide_idx}") and slide_idx > 0:
            state["slide_idx"] -= 1
            state["started"] = False
            state["history"] = []
            st.session_state[state_key] = state
            st.rerun()
    with col2:
        if st.button("Slide suivante ➡️", key=f"next_{slide_idx}"):
            state["slide_idx"] += 1
            state["started"] = False
            state["history"] = []
            st.session_state[state_key] = state
            st.rerun()