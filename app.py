# -*- coding: utf-8 -*-
"""LINGUA BRIDGE ACADEMY — App multi-langue (EN / FR)"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import streamlit.components.v1 as components

from pronunciation_data import PRONUNCIATION_DATA
from sheets_db import (
    get_all_sessions, get_session_by_num, update_session, get_stats,
    authenticate, save_submission, get_student_submissions,
    get_pending_submissions, get_all_submissions_with_feedback,
    save_feedback, change_password, get_lang, save_audio_submission
)

st.set_page_config(
    page_title="Lingua Bridge Academy",
    page_icon=":bridge_at_night:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ============ GOOGLE FONTS ============ */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    /* ============ GLOBAL ============ */
    html, body, [class*="css"] {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #E2EFDA 0%, #F5F9F2 100%);
    }

    /* ============ HEADERS ============ */
    .main-header {
        color: #3D1F5C;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(61, 31, 92, 0.08);
    }

    .sub-header {
        color: #FF6B35;
        font-size: 1.1rem;
        text-align: center;
        font-weight: 400;
        font-style: italic;
        margin-bottom: 2rem;
        opacity: 0.9;
    }

    /* ============ CARDS ============ */
    .metric-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #FAFCF8 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #3D1F5C;
        margin: 0.75rem 0;
        box-shadow: 0 4px 20px rgba(61, 31, 92, 0.08);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(61, 31, 92, 0.15);
    }

    /* ============ LESSON BANNER ============ */
    .lesson-banner {
        background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 16px;
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 6px 24px rgba(61, 31, 92, 0.3);
        letter-spacing: 0.5px;
    }

    /* ============ ANSWER BOX ============ */
    .answer-box {
        background: linear-gradient(135deg, #F0F8F0 0%, #E8F5E9 100%);
        padding: 1rem 1.25rem;
        border-radius: 12px;
        border-left: 4px solid #2E7D32;
        box-shadow: inset 0 1px 3px rgba(46, 125, 50, 0.1);
        color: #1B5E20;
    }

    /* ============ METRICS ============ */
    div[data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.25rem;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(61, 31, 92, 0.06);
        border-top: 3px solid #FF6B35;
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15);
        border-top-color: #3D1F5C;
    }

    div[data-testid="stMetricValue"] {
        color: #3D1F5C;
        font-weight: 700;
        font-size: 2rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #666;
        font-weight: 500;
    }

    /* ============ BUTTONS ============ */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.25s ease !important;
        border: 1.5px solid transparent !important;
        padding: 0.5rem 1rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(61, 31, 92, 0.2) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(61, 31, 92, 0.25) !important;
    }

    /* ============ DOWNLOAD BUTTONS ============ */
    .stDownloadButton > button {
        background: white !important;
        color: #3D1F5C !important;
        border: 1.5px solid #3D1F5C !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }

    .stDownloadButton > button:hover {
        background: #3D1F5C !important;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(61, 31, 92, 0.2) !important;
    }

    /* ============ EXPANDERS ============ */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        border: 1px solid #E0E7DC !important;
        transition: all 0.2s ease !important;
    }

    .streamlit-expanderHeader:hover {
        background: #FAFCF8 !important;
        border-color: #3D1F5C !important;
    }

    /* ============ SIDEBAR ============ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F5F9F2 100%);
        border-right: 1px solid #E0E7DC;
    }

    section[data-testid="stSidebar"] .stButton > button {
        border-radius: 10px !important;
        font-size: 0.95rem !important;
    }

    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 6px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(61, 31, 92, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        font-family: 'Poppins', sans-serif;
    }

    /* ============ INPUTS ============ */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px !important;
        border: 1.5px solid #E0E7DC !important;
        transition: all 0.2s ease !important;
        font-family: 'Poppins', sans-serif !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3D1F5C !important;
        box-shadow: 0 0 0 3px rgba(61, 31, 92, 0.1) !important;
    }

    /* ============ FORMS ============ */
    .stForm {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(61, 31, 92, 0.06);
    }

    /* ============ INFO BOXES ============ */
    .stAlert {
        border-radius: 12px !important;
        border-left-width: 5px !important;
    }

    /* ============ TTS CARDS ============ */
    .tts-card {
        background: white !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        border-left: 5px solid #3D1F5C !important;
        box-shadow: 0 4px 16px rgba(61, 31, 92, 0.08) !important;
        transition: all 0.25s ease !important;
    }

    .tts-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(61, 31, 92, 0.15) !important;
        border-left-color: #FF6B35 !important;
    }

    .tts-btn {
        background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%) !important;
        box-shadow: 0 4px 12px rgba(61, 31, 92, 0.25) !important;
    }

    .tts-btn:hover {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8A5B 100%) !important;
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.35) !important;
    }

    /* ============ DIVIDERS ============ */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E0E7DC, transparent);
        margin: 1.5rem 0;
    }

    /* ============ ANIMATIONS ============ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .main-header, .metric-card, .lesson-banner {
        animation: fadeIn 0.4s ease-out;
    }

    /* ============ SCROLLBAR ============ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #F0F5EC;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8A5B 100%);
    }
</style>
""", unsafe_allow_html=True)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "current_session" not in st.session_state:
    st.session_state.current_session = None
if "lang" not in st.session_state:
    st.session_state.lang = "en"


def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdst.markdown("""own("<div style='height: 3rem;'></div>",
                    unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #3D1F5C; font-size: 3rem; margin-bottom: 0;'>
                Lingua Bridge Academy
            </h1>
            <p style='color: #C9A227; font-style: italic; margin-top: 0;'>
                Building bridges through language
            </p>
            <hr style='border: 1px solid #C9A227;'>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 2rem;'></div>",
                    unsafe_allow_html=True)
        st.markdown("### 🔐 Iniciar sesión")
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar",
                                             use_container_width=True)
            if submit:
                if not username or not password:
                    st.error("Completa todos los campos")
                else:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = dict(user)
                        st.session_state.page = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")


def render_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #3D1F5C; margin-bottom: 0;'> Lingua Bridge</h2>
            <p style='color: #C9A227; font-style: italic; font-size: 0.8rem;
                      margin-top: 0;'>Building bridges through language</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("**🌍 Curso**")
        lang_options = {"🇬🇧 Inglés": "en", "🇫🇷 Francés": "fr"}
        current_label = ("🇫🇷 Francés" if st.session_state.lang == "fr"
                          else "🇬🇧 Inglés")
        selected = st.radio("", list(lang_options.keys()),
                             index=list(lang_options.keys()).index(current_label),
                             label_visibility="collapsed",
                             key="lang_selector")
        new_lang = lang_options[selected]
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.session_state.current_session = None
            st.rerun()

        st.markdown("---")

        role_emoji = "👨‍🏫" if user["role"] == "teacher" else "👩‍🎓"
        role_label = "Profesor" if user["role"] == "teacher" else "Estudiante"
        st.markdown(f"""
        <div style='padding: 0.5rem; background: white; border-radius: 8px;
                    border-left: 4px solid #FF6B35;'>
            <b>{role_emoji} {user['full_name']}</b><br>
            <small style='color: #666;'>{role_label}</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        if user["role"] == "teacher":
            menu_items = [
                ("🏠 Panel", "dashboard"),
                ("📬 Envíos", "submissions"),
                ("📅 Sesiones", "sessions"),
                ("📚 Lecciones", "lessons"),
                ("🎤 Pronunciación", "pronunciation"),
                ("📊 Progreso", "progress"),
                ("🎓 Certificado", "certificate"),
                ("🔐 Cambiar contraseña", "change_password"),
            ]
        else:
            menu_items = [
                ("🏠 Inicio", "dashboard"),
                ("📚 Mis lecciones", "lessons"),
                ("🎤 Pronunciación", "pronunciation"),
                ("✏️ Mis ejercicios", "exercises"),
                ("📊 Mi progreso", "progress"),
                ("📅 Mi calendario", "calendar"),
            ]

        for label, key in menu_items:
            is_active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}", use_container_width=True,
                          type="primary" if is_active else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.lang = "en"
            st.rerun()


def page_teacher_dashboard():
    st.markdown('<div class="main-header">Panel del Profesor</div>',
                unsafe_allow_html=True)
    stats = get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Sesiones totales", stats["total"])
    with col2:
        st.metric("✅ Asistidas", stats["attended"])
    with col3:
        st.metric("📊 Promedio", f"{stats['avg_score']}/10")
    with col4:
        st.metric("📈 Tasa de asistencia", f"{stats['attendance_rate']}%")
    st.markdown("---")
    sessions = get_all_sessions()
    next_session = next((s for s in sessions if not s["attended"]), None)
    if next_session:
        st.markdown("### 🎯 Próxima sesión")
        st.markdown(f"""
        <div class="metric-card">
            <h3 style='color: #3D1F5C; margin: 0;'>
                {next_session['session_num']} — {next_session['lesson']}
            </h3>
            <p style='color: #666; margin: 0.5rem 0;'>
                📅 {next_session['date']} ({next_session['day']}) ·
                ⏱ {next_session['duration']}
            </p>
            <p style='margin: 0;'>{next_session['content']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("▶️ Iniciar sesión", type="primary",
                      use_container_width=True):
            st.session_state.current_session = next_session["session_num"]
            st.session_state.page = "session_live"
            st.rerun()
    else:
        st.success("🎉 ¡Todas las sesiones están completadas!")
    st.markdown("---")
    st.markdown("### 📋 Próximas sesiones")
    df = pd.DataFrame(sessions)
    upcoming = df[df["attended"] == 0].head(5)
    if not upcoming.empty:
        for _, row in upcoming.iterrows():
            st.markdown(f"- **{row['session_num']}** · {row['date']} · "
                        f"{row['lesson']} — {row['content']}")


def page_session_live():
    session_num = st.session_state.current_session
    if not session_num:
        st.error("No hay sesión seleccionada")
        if st.button("← Volver"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    session = get_session_by_num(session_num)
    if not session:
        st.error(f"Sesión {session_num} no encontrada")
        return
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"""
        <div class="lesson-banner">
            {session['session_num']} — {session['lesson']}
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"**📅 {session['date']}**")
        st.markdown(f"*{session['day']}*")
    with col3:
        if st.button("← Volver", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    st.markdown(f"**Contenido:** {session['content']} · "
                f"**Duración:** {session['duration']}")
    st.markdown("---")

    lang = get_lang()
    lesson = session["lesson"]
    if lang == "fr" and lesson.startswith("L"):
        prefix = lesson[:3]
        base_path = "fr/"
    else:
        prefix = lesson.replace(" ", "_")
        base_path = ""

    if prefix:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📄 Material del profesor")
            pptx = f"{base_path}{prefix}_PPT.pptx"
            notes = f"{base_path}{prefix}_Notes.pdf"
            if os.path.exists(pptx):
                with open(pptx, "rb") as f:
                    st.download_button("⬇️ Descargar PPTX", f,
                        file_name=f"{prefix}_PPT.pptx",
                        use_container_width=True)
            if os.path.exists(notes):
                with open(notes, "rb") as f:
                    st.download_button("⬇️ Descargar Notas", f,
                        file_name=f"{prefix}_Notes.pdf",
                        use_container_width=True)
        with col2:
            st.markdown("### 📘 Material del alumno")
            suffix = "_Cuaderno.pdf" if lang == "fr" else "_Student.pdf"
            student = f"{base_path}{prefix}{suffix}"
            if os.path.exists(student):
                with open(student, "rb") as f:
                    st.download_button("⬇️ Descargar Cuaderno", f,
                        file_name=f"{prefix}{suffix}",
                        use_container_width=True)

    st.markdown("---")
    with st.form("session_form"):
        attended = st.checkbox("✅ El alumno asistió",
                                value=bool(session["attended"]))
        score = st.slider("📊 Puntuación (0-10)", 0.0, 10.0, 5.0, 0.5)
        notes = st.text_area("📝 Observaciones",
                              value=session["notes"] or "", height=150)
        if st.form_submit_button("💾 Guardar", use_container_width=True,
                                  type="primary"):
            update_session(session_num, 1 if attended else 0, score, notes)
            st.success("✅ Sesión guardada")
            st.balloons()


def page_sessions():
    st.markdown('<div class="main-header">Todas las Sesiones</div>',
                unsafe_allow_html=True)
    sessions = get_all_sessions()
    for row in sessions:
        status = "✅" if row["attended"] else "⏳"
        with st.expander(f"{status} {row['session_num']} · {row['date']} · "
                          f"{row['lesson']}"):
            st.markdown(f"**Contenido:** {row['content']}")
            st.markdown(f"**Día:** {row['day']} · "
                        f"**Duración:** {row['duration']}")
            if row["score"] is not None:
                st.metric("Puntuación", f"{row['score']}/10")
            if st.button("▶️ Abrir", key=f"open_{row['session_num']}",
                          use_container_width=True):
                st.session_state.current_session = row["session_num"]
                st.session_state.page = "session_live"
                st.rerun()


def page_lessons():
    user = st.session_state.user
    is_teacher = user["role"] == "teacher"
    lang = get_lang()

    if lang == "fr":
        title = "📚 Lecciones — Vista Profesor" if is_teacher else "📚 Mis Lecciones"
        lessons = [
            ("L01", "Bonjour !", "A1"), ("L02", "Je suis...", "A1"),
            ("L03", "J'ai...", "A1"), ("L04", "Le / la / les", "A1"),
            ("L05", "Je parle", "A1"), ("L06", "Quelle heure ?", "A1"),
            ("L07", "Je vais, je fais", "A1"), ("L08", "Mon / ma / mes", "A1"),
            ("L09", "Je ne... pas", "A1"), ("L10", "Est-ce que...?", "A1"),
            ("L11", "Le, la, lui, leur", "A1+"), ("L12", "Plus... que", "A1+"),
            ("L13", "J'ai mangé", "A1+"), ("L14", "Je suis allé", "A1+"),
            ("L15", "Quand j'étais...", "A1+"), ("L16", "Je vais partir", "A1+"),
            ("L17", "Je voudrais", "A1+"), ("L18", "Qui, que, où", "A1+"),
            ("L19", "Récapitulons", "A1+"),
        ]
        base_path = "fr/"
        student_suffix = "_Cuaderno.pdf"
        docs_title = "📁 Documentos generales del curso de francés"
        docs_caption = "Programa, metodología y recursos"
    else:
        title = ("📚 Lecciones — Vista Profesor" if is_teacher
                 else "📚 Mis Lecciones")
        lessons = [
            ("Class 00", "Revision Class", "A1"),
            ("Class 01", "My Daily Routine", "A1"),
            ("Class 02", "Yesterday & Last Weekend", "A2"),
            ("Class 03", "My Last Weekend", "A2"),
            ("Class 04", "My Future Plans", "A2"),
            ("Class 05", "My Week", "A2"),
            ("Class 06", "My Life Experiences", "B1"),
            ("Class 07", "How Long Have You...?", "B1"),
            ("Class 08", "What Have You Been Doing?", "B1"),
            ("Class 09", "What Were You Doing?", "B1"),
            ("Class 10", "I Was Walking When...", "B1"),
            ("Class 11", "I Used To...", "B1"),
            ("Class 12", "If It Rains, I Will...", "B2"),
            ("Class 13", "What Would You Do If...?", "B2"),
            ("Class 14", "It Was Built In 1990", "B2"),
            ("Class 15", "She Said That...", "B2"),
            ("Class 16", "The Person Who...", "B2"),
            ("Class 17", "You Must Be Tired!", "B2"),
            ("Class 18", "By Next Year, I Will Have...", "B2"),
        ]
        base_path = ""
        student_suffix = "_Student.pdf"
        docs_title = "📁 Documentos generales del curso de inglés"
        docs_caption = "Guías, programa, metodología y recursos complementarios"

    st.markdown(f'<div class="main-header">{title}</div>',
                unsafe_allow_html=True)

    # ============ DOCUMENTS GÉNÉRAUX ============
    st.markdown(f"### {docs_title}")
    st.caption(docs_caption)

    if lang == "fr":
        general_docs = [
            ("fr/syllabus_fr.pdf", "📅 Programa del curso"),
            ("fr/methodology_guide_fr.pdf", "🎓 Guía pedagógica"),
        ]
        if is_teacher:
            general_docs.append(
                ("fr/progress_tracker_fr.xlsx", "📊 Progress Tracker FR"))
            general_docs.append(
                ("fr/corriges_fr.pdf", "✅ Corrigés des exercices"))
    else:
        general_docs = [
            ("00- Start_here.pdf", "🚀 Guía de inicio"),
            ("01- Syllabus.pdf", "📅 Programa del curso"),
            ("04- Preambule.pdf", "📖 Preámbulo"),
            ("05- Methodology_Guide.pdf", "🎓 Guía pedagógica"),
        ]
        if is_teacher:
            general_docs.append(
                ("02- Answer_Key_19_Lecons_Course_Slides.pdf",
                 "✅ Corrigés PPTX"))
            general_docs.append(
                ("03- Answer_Key_19_Lecons_Additional_Exercices.pdf",
                 "✅ Corrigés ejercicios"))
            general_docs.append(
                ("Progress_Tracker.xlsx", "📊 Progress Tracker"))

    cols = st.columns(2)
    for i, (filename, label) in enumerate(general_docs):
        with cols[i % 2]:
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    st.download_button(f"⬇️ {label}", f,
                        file_name=filename.split("/")[-1],
                        key=f"doc_{lang}_{filename}",
                        use_container_width=True)
    st.markdown("---")

    st.markdown("### 📚 Lecciones individuales")

    for class_name, title_l, level in lessons:
        with st.expander(f"📖 **{class_name}** — {title_l} ({level})"):
            prefix = class_name.replace(" ", "_")
            if is_teacher:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📄 Material del profesor**")
                    pptx = f"{base_path}{prefix}_PPT.pptx"
                    notes = f"{base_path}{prefix}_Notes.pdf"
                    if os.path.exists(pptx):
                        with open(pptx, "rb") as f:
                            st.download_button("⬇️ PPTX", f,
                                file_name=f"{prefix}_PPT.pptx",
                                key=f"pptx_{prefix}_{lang}",
                                use_container_width=True)
                    else:
                        st.caption(f"⚠️ Falta {pptx}")
                    if os.path.exists(notes):
                        with open(notes, "rb") as f:
                            st.download_button("⬇️ Notas del profesor", f,
                                file_name=f"{prefix}_Notes.pdf",
                                key=f"notes_{prefix}_{lang}",
                                use_container_width=True)
                with col2:
                    st.markdown("**📘 Material del alumno**")
                    student = f"{base_path}{prefix}{student_suffix}"
                    if os.path.exists(student):
                        with open(student, "rb") as f:
                            st.download_button("⬇️ Cuaderno", f,
                                file_name=f"{prefix}{student_suffix}",
                                key=f"student_{prefix}_{lang}",
                                use_container_width=True)
            else:
                st.markdown("**📘 Mi cuaderno de trabajo**")
                student = f"{base_path}{prefix}{student_suffix}"
                if os.path.exists(student):
                    with open(student, "rb") as f:
                        st.download_button(
                            f"⬇️ Descargar cuaderno — {class_name}",
                            f,
                            file_name=f"{prefix}{student_suffix}",
                            key=f"student_{prefix}_{lang}",
                            use_container_width=True)
                else:
                    st.info("El cuaderno estará disponible pronto")


def tts_block(items, lang_code="en-US", cols=2):
    html_items = ""
    for item in items:
        safe = item.replace("'", "\\'").replace('"', "&quot;")
        html_items += f'''
        <div class="tts-card">
            <span class="tts-word">{item}</span>
            <button class="tts-btn" onclick="speak('{safe}')">🔊</button>
        </div>
        '''
    html = f"""
    <html><head><style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; }}
        .grid {{ display: grid;
            grid-template-columns: repeat({cols}, 1fr); gap: 10px; }}
        .tts-card {{ display: flex; align-items: center;
            justify-content: space-between; background: white;
            border-radius: 8px; padding: 12px 16px;
            border-left: 4px solid #3D1F5C;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .tts-word {{ font-size: 16px; color: #333; font-weight: 500; }}
        .tts-btn {{ background: #3D1F5C; color: white; border: none;
            border-radius: 50%; width: 40px; height: 40px;
            cursor: pointer; font-size: 18px; flex-shrink: 0;
            transition: all 0.2s; }}
        .tts-btn:hover {{ background: #FF6B35; transform: scale(1.1); }}
        .tts-btn:active {{ transform: scale(0.95); }}
    </style></head><body>
    <div class="grid">{html_items}</div>
    <script>
    function speak(text) {{
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = '{lang_code}'; u.rate = 0.8; u.pitch = 1.0; u.volume = 1.0;
        speechSynthesis.speak(u);
    }}
    </script></body></html>
    """
    rows = (len(items) + cols - 1) // cols
    height = rows * 70 + 20
    components.html(html, height=height)


def page_pronunciation():
    user = st.session_state.user
    lang = get_lang()
    st.markdown('<div class="main-header">🎤 Pronunciación</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">'
                'Escucha y practica los sonidos clave</div>',
                unsafe_allow_html=True)
    st.info("👉 **Cómo usar:** Haz clic en 🔊 para escuchar. "
            "Repite en voz alta. Vuelve a escuchar. "
            "Usa auriculares para mejor calidad.")

    data = PRONUNCIATION_DATA.get(lang, {})
    if not data:
        st.warning("Contenido no disponible.")
        return

    if lang == "fr":
        lessons_list = [f"L{i:02d}" for i in range(1, 20)]
        base_label = "Lección"
        voice_lang = "fr-FR"
    else:
        lessons_list = [f"Class {i:02d}" for i in range(19)]
        base_label = "Lección"
        voice_lang = "en-US"

    available = [l for l in lessons_list if l in data]
    if not available:
        st.warning("Aún no hay datos de pronunciación disponibles.")
        return

    selected = st.selectbox(f"📚 {base_label}", available, index=0,
                              key="pron_lesson")
    lesson_data = data[selected]

    st.markdown("---")
    st.markdown(f"## 🔊 {lesson_data['title']}")
    st.info(f"💡 **Consejo:** {lesson_data['tip']}")

    st.markdown("### 📝 Palabras para practicar")
    tts_block(lesson_data["words"], lang_code=voice_lang, cols=2)

    st.markdown("---")
    st.markdown("### 💬 Frases completas")
    tts_block(lesson_data["phrases"], lang_code=voice_lang, cols=1)

    st.markdown("---")
    st.markdown("### 🎯 ¡Tu turno!")
    st.markdown("**Repite cada palabra 3 veces en voz alta.**")
    st.markdown("**Luego grábalo en 'Mis ejercicios' → pestaña Audio.**")

    if user["role"] == "teacher":
        st.markdown("---")
        st.markdown("### 👨‍🏫 Notas del profesor")
        st.caption("Observar la precisión. Corregir máximo 2 sonidos por sesión.")


def page_progress():
    st.markdown('<div class="main-header">📊 Mi Progreso</div>',
                unsafe_allow_html=True)
    sessions = get_all_sessions()
    df = pd.DataFrame(sessions)
    df["Date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df["Score_clean"] = pd.to_numeric(df["score"], errors="coerce")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Evolución de puntuaciones")
        df_s = df.dropna(subset=["Score_clean"])
        if not df_s.empty:
            fig = px.line(df_s, x="Date", y="Score_clean", markers=True,
                          color_discrete_sequence=["#3D1F5C"])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay puntuaciones registradas")
    with col2:
        st.markdown("### 📊 Asistencia acumulada")
        df_sorted = df.sort_values("Date").reset_index(drop=True)
        df_sorted["Cumulative"] = df_sorted["attended"].cumsum()
        fig = px.area(df_sorted, x="Date", y="Cumulative",
                      color_discrete_sequence=["#FF6B35"])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def page_exercises():
    import time
    user = st.session_state.user
    student_id = user["id"]
    lang = get_lang()

    st.markdown('<div class="main-header">✏️ Mis Ejercicios</div>',
                unsafe_allow_html=True)
    if lang == "fr":
        lessons_opts = [f"L{i:02d}" for i in range(1, 20)]
    else:
        lessons_opts = [f"Class {i:02d}" for i in range(19)]

    tab_text, tab_audio = st.tabs(["📝 Escrito", "🎤 Audio"])

    with tab_text:
        with st.form("submit_text"):
            col1, col2 = st.columns(2)
            with col1:
                lesson = st.selectbox("Lección", lessons_opts,
                                       key="lesson_text")
            with col2:
                exercise_num = st.number_input("Número de ejercicio",
                                                1, 20, 1, key="ex_text")
            answer = st.text_area("Tu respuesta", height=200,
                                   placeholder="Escribe aquí tu respuesta...",
                                   key="answer_text")
            if st.form_submit_button("📤 Enviar al profesor",
                                      use_container_width=True,
                                      type="primary"):
                if answer.strip():
                    save_submission(student_id, lesson, exercise_num, answer)
                    st.success("✅ Respuesta enviada")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("⚠️ Escribe una respuesta antes de enviar")

    with tab_audio:
        st.markdown("**🎤 Graba tu audio directamente aquí**")
        st.caption("O sube un archivo grabado con tu teléfono")
        col1, col2 = st.columns(2)
        with col1:
            lesson_audio = st.selectbox("Lección", lessons_opts,
                                          key="lesson_audio")
        with col2:
            exercise_num_audio = st.number_input("Número de ejercicio",
                                                   1, 20, 1, key="ex_audio")

        st.markdown("**🎤 Opción 1: Graba directamente**")
        audio_value = st.audio_input("🎤 Graba tu audio", key="recorder")

        st.markdown("---")
        st.markdown("**📁 Opción 2: Sube un audio grabado**")
        st.caption("Graba con tu teléfono y súbelo aquí")
        uploaded_file = st.file_uploader("Selecciona tu archivo de audio",
                                           type=["wav", "mp3", "m4a", "ogg"],
                                           key="uploader")

        audio_bytes = None
        if audio_value is not None:
            st.audio(audio_value)
            audio_bytes = audio_value.getvalue()
        if uploaded_file is not None:
            st.audio(uploaded_file)
            audio_bytes = uploaded_file.getvalue()

        if audio_bytes is not None:
            if st.button("📤 Enviar audio al profesor",
                          use_container_width=True, type="primary"):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    if lang == "fr":
                        filename = (f"FR_{lesson_audio}_"
                                    f"Ej{exercise_num_audio}_{timestamp}.wav")
                    else:
                        filename = (f"EN_{lesson_audio.replace(' ', '')}_"
                                    f"Ej{exercise_num_audio}_{timestamp}.wav")
                    save_audio_submission(student_id, lesson_audio,
                                            exercise_num_audio,
                                            audio_bytes, filename)
                    st.success("✅ Audio enviado al profesor")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al enviar: {e}")

    st.markdown("---")
    st.markdown("### 📋 Mis envíos")
    submissions = get_student_submissions(student_id)
    if not submissions:
        st.info("Aún no has enviado ejercicios.")
        return
    for sub in submissions:
        has_fb = sub["feedback"] and sub["feedback"].strip()
        status = "✅ Corregido" if has_fb else "🟡 En espera"
        with st.expander(f"{status} · {sub['lesson']} · "
                          f"Ej. {sub['exercise_num']}"):
            st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
            if sub["answer"].startswith("🎤 Audio:"):
                link = sub["answer"].replace("🎤 Audio: ", "")
                st.markdown(f"🎤 **Audio enviado** — "
                            f"[Abrir en Google Drive]({link})")
            else:
                st.markdown(f'<div class="answer-box">{sub["answer"]}</div>',
                            unsafe_allow_html=True)
            if has_fb:
                st.markdown("**📝 Retroalimentación del profesor:**")
                st.success(sub["feedback"])
            else:
                st.caption("⏳ Pendiente de corrección")


def page_submissions():
    import time
    st.markdown('<div class="main-header">'
                '📬 Envíos de la estudiante</div>',
                unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🟡 En espera", "✅ Corregidas"])
    with tab1:
        pending = get_pending_submissions()
        if not pending:
            st.success("🎉 No hay envíos pendientes")
        else:
            for sub in pending:
                with st.expander(f"🟡 {sub['full_name']} · {sub['lesson']} · "
                                  f"Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
                    if sub["answer"].startswith("🎤 Audio:"):
                        link = sub["answer"].replace("🎤 Audio: ", "")
                        st.markdown(f"🎤 **Audio** — "
                                    f"[Abrir en Google Drive]({link})")
                    else:
                        st.markdown(
                            f'<div class="answer-box">{sub["answer"]}</div>',
                            unsafe_allow_html=True)
                    fb = st.text_area("✏️ Tu retroalimentación", height=150,
                                       key=f"fb_{sub['id']}",
                                       placeholder="Excelente uso de... "
                                                   "Atención a...")
                    if st.button("💾 Enviar", key=f"send_{sub['id']}",
                                  use_container_width=True):
                        if fb.strip():
                            save_feedback(sub["id"], fb)
                            st.success("✅ Guardado")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("⚠️ Escribe una retroalimentación")
    with tab2:
        corrected = get_all_submissions_with_feedback()
        if not corrected:
            st.info("Aún no hay envíos corregidos")
        else:
            for sub in corrected:
                with st.expander(f"✅ {sub['full_name']} · {sub['lesson']} · "
                                  f"Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Respuesta:** {sub['answer']}")
                    st.markdown("**📝 Tu retroalimentación:**")
                    st.success(sub["feedback"])


def page_calendar():
    st.markdown('<div class="main-header">📅 Mi Calendario</div>',
                unsafe_allow_html=True)
    sessions = get_all_sessions()
    weeks = sorted(set(s["week"] for s in sessions))
    for week in weeks:
        wk = [s for s in sessions if s["week"] == week]
        with st.expander(f"**Semana {week}** — {wk[0]['date']} "
                          f"al {wk[-1]['date']}"):
            for s in wk:
                status = "✅" if s["attended"] else "⏳"
                st.markdown(f"{status} **{s['session_num']}** · "
                            f"{s['date']} · {s['lesson']} — {s['content']}")


def page_certificate():
    st.markdown('<div class="main-header">🎓 Certificado</div>',
                unsafe_allow_html=True)
    stats = get_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Progreso", f"{stats['attended']}/{stats['total']}")
    with col2:
        st.metric("Promedio", f"{stats['avg_score']}/10")
    with col3:
        st.metric("Asistencia", f"{stats['attendance_rate']}%")
    st.markdown("---")
    if stats["attended"] >= stats["total"]:
        st.success("🎉 ¡Curso completado!")
        cert = "06-Certificate.pdf"
        if os.path.exists(cert):
            with open(cert, "rb") as f:
                st.download_button("⬇️ Descargar certificado", f,
                    file_name="Certificate_Ingrid.pdf",
                    use_container_width=True)
    else:
        rem = stats["total"] - stats["attended"]
        st.warning(f"⏳ Faltan {rem} sesiones para completar el curso")


def page_change_password():
    import time
    st.markdown('<div class="main-header">🔐 Cambiar Contraseña</div>',
                unsafe_allow_html=True)
    with st.form("change_pwd"):
        new_pwd = st.text_input("Nueva contraseña", type="password")
        confirm = st.text_input("Confirmar contraseña", type="password")
        if st.form_submit_button("Cambiar", type="primary",
                                  use_container_width=True):
            if new_pwd != confirm:
                st.error("Las contraseñas no coinciden")
            elif len(new_pwd) < 6:
                st.error("Mínimo 6 caracteres")
            else:
                change_password(st.session_state.user["username"], new_pwd)
                st.success("✅ Contraseña cambiada")
                st.info("Cierra sesión y vuelve a entrar con la nueva contraseña.")
                time.sleep(2)


def main():
    if not st.session_state.logged_in:
        page_login()
        return

    render_sidebar()
    user = st.session_state.user
    page = st.session_state.page

    if user["role"] == "teacher":
        if page == "dashboard":
            page_teacher_dashboard()
        elif page == "submissions":
            page_submissions()
        elif page == "session_live":
            page_session_live()
        elif page == "sessions":
            page_sessions()
        elif page == "lessons":
            page_lessons()
        elif page == "pronunciation":
            page_pronunciation()
        elif page == "progress":
            page_progress()
        elif page == "certificate":
            page_certificate()
        elif page == "change_password":
            page_change_password()
        else:
            page_teacher_dashboard()
    else:
        if page == "dashboard":
            st.markdown('<div class="main-header">'
                        '¡Bienvenida, Ingrid! 🌟</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="sub-header">'
                        'Lingua Bridge Academy · Inglés y Francés</div>',
                        unsafe_allow_html=True)
            stats = get_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lecciones completadas",
                          f"{stats['attended']}/{stats['total']}")
            with col2:
                st.metric("Promedio", f"{stats['avg_score']}/10")
            with col3:
                st.metric("Asistencia", f"{stats['attendance_rate']}%")

            st.markdown("---")
            st.markdown("### 🎯 Siguiente lección")
            sessions = get_all_sessions()
            next_s = next((s for s in sessions if not s["attended"]), None)
            if next_s:
                st.markdown(f"""
                <div class="metric-card">
                    <h3 style='color: #3D1F5C; margin: 0;'>
                        {next_s['lesson']} — {next_s['content']}
                    </h3>
                    <p style='color: #666;'>
                        📅 {next_s['date']} ({next_s['day']})
                    </p>
                </div>
                """, unsafe_allow_html=True)
        elif page == "lessons":
            page_lessons()
        elif page == "pronunciation":
            page_pronunciation()
        elif page == "exercises":
            page_exercises()
        elif page == "progress":
            page_progress()
        elif page == "calendar":
            page_calendar()
        else:
            page_lessons()


if __name__ == "__main__":
    main()
