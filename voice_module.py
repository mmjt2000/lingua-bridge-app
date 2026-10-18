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

# Config par langue
LANG_CONFIG = {
    "en": {
        "voice": "en-US-AriaNeural",
        "stt_lang": "en",
        "title": "🎤 Práctica con IA",
        "subtitle": "*Habla en inglés, la IA te escucha, corrige y responde con voz.*",
        "prompt": """You are an English conversation tutor for a Spanish-speaking student named {student_name}.
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
- Never lecture. Keep it conversational.""",
        "error_key": "GROQ_API_KEY n'est pas configurée.",
        "start_msg": "**🎤 Habla:**",
        "recording_msg": "Graba tu respuesta",
        "transcribing": "Transcribiendo...",
        "thinking": "La IA está pensando...",
        "new_conv": "🔄 Nueva conversación",
        "free_conv_title": "### 💬 Conversación libre",
    },
    "fr": {
        "voice": "fr-FR-DeniseNeural",
        "stt_lang": "fr",
        "title": "🎤 Pratique avec IA",
        "subtitle": "*Parle en français, l'IA t'écoute, corrige et répond avec sa voix.*",
        "prompt": """Tu es un tuteur de conversation en français pour une étudiante hispanophone nommée {student_name}.
Son niveau de français : {level}.

CONTEXTE IMPORTANT :
- L'étudiante peut être Ingrid, Maryse ou Laeticia (toutes hispanophones, niveau intermédiaire).
- Adapte ton vocabulaire et tes sujets à son niveau.

Règles :
- Réponds TOUJOURS en français.
- Garde tes réponses COURTES (2-4 phrases max).
- Termine ta réponse par une QUESTION OUVERTE pour continuer la conversation.
- Si elle fait une erreur de grammaire, corrige-la gentiment : "Bravo ! Petite correction : ... Mieux : ..."
- Si elle parle en espagnol, traduis en français et encourage-la à répéter.
- Sois chaleureux, encourageant, naturel - comme un tuteur amical.
- Ne fais jamais de cours magistral. Reste conversationnel.""",
        "error_key": "GROQ_API_KEY n'est pas configurée.",
        "start_msg": "**🎤 Parle :**",
        "recording_msg": "Enregistre ta réponse",
        "transcribing": "Transcription en cours...",
        "thinking": "L'IA réfléchit...",
        "new_conv": "🔄 Nouvelle conversation",
        "free_conv_title": "### 💬 Conversation libre",
    },
}

VOICE_TTS = LANG_CONFIG["en"]["voice"]  # default

# ============================================================
# CONFIG PAR NIVEAU — Adapte la pédagogie de l'IA
# ============================================================
LEVEL_CONFIG = {
    "beginner": {
        "en": {
            "vocab": "very simple, 500 most common words",
            "sentences": "max 5-7 words per sentence",
            "corrections": "only critical errors (not minor mistakes)",
            "encouragement": "very frequent (every response)",
            "questions": "yes/no or 2-option questions",
            "style": "speak slowly, use repetition, lots of emojis 😊",
        },
        "fr": {
            "vocab": "très simple, 500 mots les plus courants",
            "sentences": "max 5-7 mots par phrase",
            "corrections": "seulement les erreurs critiques (pas les fautes mineures)",
            "encouragement": "très fréquent (chaque réponse)",
            "questions": "questions fermées (oui/non) ou 2 options",
            "style": "parle lentement, répète, beaucoup d'emojis 😊",
        },
    },
    "intermediate": {
        "en": {
            "vocab": "everyday vocabulary (2000 words)",
            "sentences": "max 10-15 words per sentence",
            "corrections": "correct grammar + vocabulary errors",
            "encouragement": "regular (every 2-3 responses)",
            "questions": "open-ended questions (why, how, what do you think)",
            "style": "natural pace, conversational, use idioms occasionally",
        },
        "fr": {
            "vocab": "vocabulaire courant (2000 mots)",
            "sentences": "max 10-15 mots par phrase",
            "corrections": "corriger grammaire + vocabulaire",
            "encouragement": "régulier (toutes les 2-3 réponses)",
            "questions": "questions ouvertes (pourquoi, comment, que penses-tu)",
            "style": "rythme naturel, conversationnel, utiliser des expressions",
        },
    },
    "advanced": {
        "en": {
            "vocab": "rich vocabulary (5000+ words)",
            "sentences": "no limit",
            "corrections": "correct subtle errors (style, register)",
            "encouragement": "occasional",
            "questions": "challenging questions (debate, opinion, hypothetical)",
            "style": "native pace, use idioms, complex structures",
        },
        "fr": {
            "vocab": "vocabulaire riche (5000+ mots)",
            "sentences": "pas de limite",
            "corrections": "corriger les erreurs subtiles (style, registre)",
            "encouragement": "occasionnel",
            "questions": "questions stimulantes (débat, opinion, hypothèse)",
            "style": "rythme natif, expressions idiomatiques, structures complexes",
        },
    },
}


def get_adaptive_prompt(student_name, level, lang):
    """
    Construit un prompt adapté au niveau de l'étudiant.
    """
    level_key = level.lower() if level.lower() in LEVEL_CONFIG else "intermediate"
    level_rules = LEVEL_CONFIG[level_key][lang]
    
    if lang == "fr":
        base = f"""Tu es un tuteur de conversation en français pour une étudiante hispanophone nommée {student_name}.
Son niveau de français : {level_key}.

RÈGLES ADAPTÉES À SON NIVEAU :
- Vocabulaire : {level_rules['vocab']}
- Longueur : {level_rules['sentences']}
- Corrections : {level_rules['corrections']}
- Encouragements : {level_rules['encouragement']}
- Questions : {level_rules['questions']}
- Style : {level_rules['style']}

INSTRUCTIONS GÉNÉRALES :
- Réponds TOUJOURS en français.
- Termine par UNE SEULE question pour continuer la conversation.
- Si elle parle en espagnol, traduis en français et encourage-la à répéter.
- Ne fais JAMAIS de cours magistral. Reste conversationnel.
- Sois chaleureux, encourageant, naturel - comme un tuteur amical."""
    else:
        base = f"""You are an English conversation tutor for a Spanish-speaking student named {student_name}.
Her English level: {level_key}.

RULES ADAPTED TO HER LEVEL:
- Vocabulary: {level_rules['vocab']}
- Sentence length: {level_rules['sentences']}
- Corrections: {level_rules['corrections']}
- Encouragement: {level_rules['encouragement']}
- Questions: {level_rules['questions']}
- Style: {level_rules['style']}

GENERAL INSTRUCTIONS:
- ALWAYS respond in English.
- End with ONE question to keep the conversation going.
- If she speaks Spanish, translate it to English and encourage her to repeat.
- NEVER lecture. Keep it conversational.
- Be warm, encouraging, natural - like a friendly tutor."""
    
    return base.strip()

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
def llm_conversation(user_text, history, level="intermediate", student_name="Student", lang="en"):
    client = get_groq_client()
    
    # Utiliser le prompt adaptatif selon le niveau
    system_prompt = get_adaptive_prompt(student_name, level, lang)
    
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
    lang = st.session_state.get("lang", "en")
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])

    st.markdown("---")
    st.markdown(f"## {cfg['title']}")
    st.markdown(cfg["subtitle"])

    if not GROQ_API_KEY:
        st.error(f"⚠️ {cfg['error_key']}")
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
    lang = st.session_state.get("lang", "en")
    cfg = LANG_CONFIG.get(lang, LANG_CONFIG["en"])

    st.markdown(cfg["free_conv_title"])

    if "conv_history" not in st.session_state:
        st.session_state.conv_history = []
    if "conv_last_audio" not in st.session_state:
        st.session_state.conv_last_audio = None
    if "conv_lang" not in st.session_state:
        st.session_state.conv_lang = lang

    # Reset conversation si on change de langue
    if st.session_state.conv_lang != lang:
        st.session_state.conv_history = []
        st.session_state.conv_last_audio = None
        st.session_state.conv_lang = lang

    for msg in st.session_state.conv_history[-8:]:
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"]):
            st.markdown(f"{role_icon} {msg['content']}")

    st.markdown(cfg["start_msg"])
    audio_file = st.audio_input(cfg["recording_msg"], key="conv_audio")

    if audio_file is not None:
        wav_data = audio_file.getvalue()
        if wav_data and wav_data != st.session_state.conv_last_audio:
            st.session_state.conv_last_audio = wav_data

            with st.spinner(cfg["transcribing"]):
                user_text = transcribe_audio(wav_data, language=cfg["stt_lang"])

            if user_text and not user_text.startswith("[Erreur"):
                st.session_state.conv_history.append({"role": "user", "content": user_text})
                with st.chat_message("user"):
                    st.markdown(f"🧑 {user_text}")

                with st.spinner(cfg["thinking"]):
                    user_info = st.session_state.get("user", {})
                    student_name = user_info.get("full_name", "Student").split()[0]
                    # Récupérer le niveau selon la langue
                    level_key = "french_level" if lang == "fr" else "english_level"
                    student_level = user_info.get(level_key, "intermediate")
                    reply = llm_conversation(
                        user_text,
                        st.session_state.conv_history,
                        student_level,
                        student_name=student_name,
                        lang=lang,
                    )
                st.session_state.conv_history.append({"role": "assistant", "content": reply})

                with st.chat_message("assistant"):
                    st.markdown(f"🤖 {reply}")

                audio_reply = text_to_speech(reply, voice=cfg["voice"])
                if audio_reply:
                    st.audio(audio_reply, format="audio/mp3", autoplay=True)

    if st.button(cfg["new_conv"], key="conv_reset"):
        st.session_state.conv_history = []
        st.session_state.conv_last_audio = None
        st.rerun()