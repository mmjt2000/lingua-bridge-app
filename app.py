# -*- coding: utf-8 -*-
"""LINGUA BRIDGE ACADEMY — App multi-langue (EN / FR)"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

from sheets_db import (get_all_sessions, get_session_by_num, update_session,
                        get_stats, authenticate, save_submission,
                        get_student_submissions, get_pending_submissions,
                        get_all_submissions_with_feedback, save_feedback,
                        change_password, get_lang)

st.set_page_config(
    page_title="Lingua Bridge Academy",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {color: #3D1F5C; font-size: 2.5rem; font-weight: bold;
        text-align: center; padding: 1rem 0;}
    .sub-header {color: #FF6B35; font-size: 1.2rem; text-align: center;
        font-style: italic; margin-bottom: 2rem;}
    .metric-card {background: white; padding: 1rem; border-radius: 10px;
        border-left: 5px solid #3D1F5C; margin: 0.5rem 0;}
    .lesson-banner {background: #3D1F5C; color: white; padding: 1rem;
        border-radius: 10px; font-size: 1.5rem; font-weight: bold;
        text-align: center;}
    .answer-box {background: #F0F8F0; padding: 1rem; border-radius: 8px;
        border-left: 4px solid #2E7D32;}
</style>
""", unsafe_allow_html=True)


# ==================== SESSION STATE ====================
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


# ==================== LOGIN ====================
def page_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #3D1F5C; font-size: 3rem; margin-bottom: 0;'>
                🌉 Lingua Bridge Academy
            </h1>
            <p style='color: #C9A227; font-style: italic; margin-top: 0;'>
                Building bridges through language
            </p>
            <hr style='border: 1px solid #C9A227;'>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 🔐 Iniciar sesión")

        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)

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


# ==================== SIDEBAR ====================
def render_sidebar():
    user = st.session_state.user

    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #3D1F5C; margin-bottom: 0;'>🌉 Lingua Bridge</h2>
            <p style='color: #C9A227; font-style: italic; font-size: 0.8rem;
                      margin-top: 0;'>Building bridges through language</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ===== SÉLECTEUR DE LANGUE =====
        st.markdown("**🌍 Curso / Course**")
        lang_options = {"🇬🇧 English": "en", "🇫🇷 Français": "fr"}
        current_label = "🇫🇷 Français" if st.session_state.lang == "fr" else "🇬🇧 English"
        selected = st.radio("", list(lang_options.keys()),
                             index=list(lang_options.keys()).index(current_label),
                             label_visibility="collapsed", key="lang_selector")
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
                ("📊 Progreso", "progress"),
                ("🎓 Certificado", "certificate"),
                ("🔐 Cambiar contraseña", "change_password"),
            ]
        else:
            menu_items = [
                ("🏠 Inicio", "dashboard"),
                ("📚 Mis lecciones", "lessons"),
                ("✏️ Mis ejercicios", "exercises"),
                ("📊 Mi progreso", "progress"),
                ("📅 Mi calendario", "calendar"),
            ]

        for label, key in menu_items:
            is_active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}",
                          use_container_width=True,
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


# ==================== DASHBOARD PROF ====================
def page_teacher_dashboard():
    lang = get_lang()
    title = "Panel del Profesor" if lang == "en" else "Panel del Profesor — Français"
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)

    stats = get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Sesiones totales", stats["total"])
    with col2:
        st.metric("✅ Asistidas", stats["attended"])
    with col3:
        st.metric("📊 Promedio", f"{stats['avg_score']}/10")
    with col4:
        st.metric("📈 Tasa asistencia", f"{stats['attendance_rate']}%")

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
        col1, col2 = st.columns(2)
        with col1:
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


# ==================== SESSION LIVE ====================
def page_session_live():
    lang = get_lang()
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

    lesson = session["lesson"]
    # Déterminer le préfixe du fichier
    if lesson.startswith("L") and lesson[1:3].isdigit():
        prefix = lesson[:3]  # L01, L02...
        base_path = "fr/"
    else:
        prefix = lesson.replace(" ", "_")  # Class_00
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
            else:
                st.caption(f"⚠️ Falta {pptx}")

            if os.path.exists(notes):
                with open(notes, "rb") as f:
                    st.download_button("⬇️ Descargar Notas", f,
                        file_name=f"{prefix}_Notes.pdf",
                        use_container_width=True)

        with col2:
            st.markdown("### 📘 Material del alumno")
            student = f"{base_path}{prefix}_Cuaderno.pdf"
            if os.path.exists(student):
                with open(student, "rb") as f:
                    st.download_button("⬇️ Descargar Cuaderno", f,
                        file_name=f"{prefix}_Cuaderno.pdf",
                        use_container_width=True)

    st.markdown("---")
    with st.form("session_form"):
        attended = st.checkbox("✅ El alumno asistió",
                                value=bool(session["attended"]))
        score = st.slider("📊 Score (0-10)", 0.0, 10.0, 5.0, 0.5)
        notes = st.text_area("📝 Observaciones",
                              value=session["notes"] or "", height=150)

        if st.form_submit_button("💾 Guardar", use_container_width=True,
                                  type="primary"):
            update_session(session_num, 1 if attended else 0, score, notes)
            st.success("✅ Sesión guardada")
            st.balloons()


# ==================== SESSIONS ====================
def page_sessions():
    lang = get_lang()
    title = "Todas las Sesiones" if lang == "en" else "Toutes les Sessions — Français"
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)

    sessions = get_all_sessions()
    df = pd.DataFrame(sessions)
    for _, row in df.iterrows():
        status = "✅" if row["attended"] else "⏳"
        with st.expander(f"{status} {row['session_num']} · {row['date']} · "
                          f"{row['lesson']}"):
            st.markdown(f"**Contenido:** {row['content']}")
            st.markdown(f"**Día:** {row['day']} · **Duración:** {row['duration']}")
            if row["score"] is not None:
                st.metric("Score", f"{row['score']}/10")
            if st.button("▶️ Abrir", key=f"open_{row['session_num']}",
                          use_container_width=True):
                st.session_state.current_session = row["session_num"]
                st.session_state.page = "session_live"
                st.rerun()


# ==================== LECONS ====================
def page_lessons():
    user = st.session_state.user
    is_teacher = user["role"] == "teacher"
    lang = get_lang()

    if lang == "fr":
        title = "📚 Leçons — Vue Professeur" if is_teacher else "📚 Mes Leçons"
        lessons = [
            ("L01", "Bonjour !", "A1"),
            ("L02", "Je suis...", "A1"),
            ("L03", "J'ai...", "A1"),
            ("L04", "Le / la / les", "A1"),
            ("L05", "Je parle", "A1"),
            ("L06", "Quelle heure ?", "A1"),
            ("L07", "Je vais, je fais", "A1"),
            ("L08", "Mon / ma / mes", "A1"),
            ("L09", "Je ne... pas", "A1"),
            ("L10", "Est-ce que...?", "A1"),
            ("L11", "Le, la, lui, leur", "A1+"),
            ("L12", "Plus... que", "A1+"),
            ("L13", "J'ai mangé", "A1+"),
            ("L14", "Je suis allé", "A1+"),
            ("L15", "Quand j'étais...", "A1+"),
            ("L16", "Je vais partir", "A1+"),
            ("L17", "Je voudrais", "A1+"),
            ("L18", "Qui, que, où", "A1+"),
            ("L19", "Récapitulons", "A1+"),
        ]
        base_path = "fr/"
        student_suffix = "_Cuaderno.pdf"
    else:
        title = "📚 Lecciones — Vista Profesor" if is_teacher else "📚 Mis Lecciones"
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

    st.markdown(f'<div class="main-header">{title}</div>',
                unsafe_allow_html=True)

    # ============ DOCUMENTS GÉNÉRAUX ============
    if lang == "en":
        st.markdown("### 📁 Documentos generales del curso")
        st.caption("Guías, programa, metodología y recursos complementarios")

        general_docs = [
            ("00- Start_here.pdf", "🚀 Guía de inicio"),
            ("01- Syllabus.pdf", "📅 Programa del curso"),
            ("04- Preambule.pdf", "📖 Preámbulo"),
            ("05- Methodology_Guide.pdf", "🎓 Guía pedagógica"),
        ]
        if is_teacher:
            general_docs.append(
                ("02- Answer_Key_19_Lecons_Course_Slides.pdf", "✅ Corrigés PPTX"))
            general_docs.append(
                ("03- Answer_Key_19_Lecons_Additional_Exercices.pdf", "✅ Corrigés ejercicios"))
            general_docs.append(("Progress_Tracker.xlsx", "📊 Progress Tracker"))

        cols = st.columns(2)
        for i, (filename, label) in enumerate(general_docs):
            with cols[i % 2]:
                if os.path.exists(filename):
                    with open(filename, "rb") as f:
                        st.download_button(f"⬇️ {label}", f,
                            file_name=filename,
                            key=f"doc_{filename}",
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


# ==================== PROGRESO ====================
def page_progress():
    st.markdown('<div class="main-header">📊 Progreso</div>',
                unsafe_allow_html=True)
    sessions = get_all_sessions()
    df = pd.DataFrame(sessions)
    df["Date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df["Score_clean"] = pd.to_numeric(df["score"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📈 Evolución de scores")
        df_s = df.dropna(subset=["Score_clean"])
        if not df_s.empty:
            fig = px.line(df_s, x="Date", y="Score_clean", markers=True,
                          color_discrete_sequence=["#3D1F5C"])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay scores")
    with col2:
        st.markdown("### 📊 Asistencia acumulada")
        df_sorted = df.sort_values("Date").reset_index(drop=True)
        df_sorted["Cumulative"] = df_sorted["attended"].cumsum()
        fig = px.area(df_sorted, x="Date", y="Cumulative",
                      color_discrete_sequence=["#FF6B35"])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# ==================== EXERCICES (élève) ====================
def page_exercises():
    import time
    user = st.session_state.user
    student_id = user["id"]
    lang = get_lang()

    st.markdown('<div class="main-header">✏️ Mis ejercicios</div>',
                unsafe_allow_html=True)

    if lang == "fr":
        lessons_opts = [f"L{i:02d}" for i in range(1, 20)]
    else:
        lessons_opts = [f"Class {i:02d}" for i in range(19)]

    with st.form("submit_exercise"):
        col1, col2 = st.columns(2)
        with col1:
            lesson = st.selectbox("Lección", lessons_opts)
        with col2:
            exercise_num = st.number_input("Número de ejercicio", 1, 20, 1)

        answer = st.text_area("Tu respuesta", height=200,
                              placeholder="Escribe aquí tu respuesta...")

        if st.form_submit_button("📤 Enviar al profesor",
                                  use_container_width=True, type="primary"):
            if answer.strip():
                save_submission(student_id, lesson, exercise_num, answer)
                st.success("✅ Respuesta enviada")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Escribe una respuesta")

    st.markdown("---")
    st.markdown("### 📋 Mis envíos")
    submissions = get_student_submissions(student_id)
    if not submissions:
        st.info("Aún no has enviado ejercicios.")
        return

    for sub in submissions:
        has_fb = sub["feedback"] and sub["feedback"].strip()
        status = "✅ Corregido" if has_fb else "🟡 En espera"
        with st.expander(f"{status} · {sub['lesson']} · Ej. {sub['exercise_num']}"):
            st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
            st.markdown(f'<div class="answer-box">{sub["answer"]}</div>',
                        unsafe_allow_html=True)
            if has_fb:
                st.markdown("**📝 Feedback:**")
                st.success(sub["feedback"])


# ==================== SUBMISSIONS (prof) ====================
def page_submissions():
    import time
    st.markdown('<div class="main-header">📬 Envíos de la estudiante</div>',
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
                    st.markdown(f'<div class="answer-box">{sub["answer"]}</div>',
                                unsafe_allow_html=True)
                    fb = st.text_area("✏️ Tu retroalimentación", height=150,
                                       key=f"fb_{sub['id']}")
                    if st.button("💾 Enviar", key=f"send_{sub['id']}",
                                  use_container_width=True):
                        if fb.strip():
                            save_feedback(sub["id"], fb)
                            st.success("✅ Guardado")
                            time.sleep(1)
                            st.rerun()

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


# ==================== CALENDRIER ====================
def page_calendar():
    st.markdown('<div class="main-header">📅 Mi calendario</div>',
                unsafe_allow_html=True)
    sessions = get_all_sessions()
    weeks = sorted(set(s["week"] for s in sessions))
    for week in weeks:
        wk = [s for s in sessions if s["week"] == week]
        with st.expander(f"**Semana {week}** — {wk[0]['date']} al {wk[-1]['date']}"):
            for s in wk:
                status = "✅" if s["attended"] else "⏳"
                st.markdown(f"{status} **{s['session_num']}** · "
                            f"{s['date']} · {s['lesson']} — {s['content']}")


# ==================== CERTIFICAT ====================
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
        st.success("🎉 Curso completado")
        cert = "06-Certificate.pdf"
        if os.path.exists(cert):
            with open(cert, "rb") as f:
                st.download_button("⬇️ Descargar certificado", f,
                    file_name="Certificate_Ingrid.pdf",
                    use_container_width=True)
    else:
        rem = stats["total"] - stats["attended"]
        st.warning(f"⏳ Faltan {rem} sesiones")


# ==================== CHANGE PASSWORD ====================
def page_change_password():
    import time
    from sheets_db import change_password
    st.markdown('<div class="main-header">🔐 Cambiar contraseña</div>',
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
                time.sleep(2)


# ==================== ROUTER ====================
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
            st.markdown('<div class="main-header">Bienvenida, Ingrid 🌟</div>',
                        unsafe_allow_html=True)
            stats = get_stats()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lecciones", f"{stats['attended']}/{stats['total']}")
            with col2:
                st.metric("Promedio", f"{stats['avg_score']}/10")
            with col3:
                st.metric("Asistencia", f"{stats['attendance_rate']}%")
        elif page == "lessons":
            page_lessons()
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
