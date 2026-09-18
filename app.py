# -*- coding: utf-8 -*-
"""
LINGUA BRIDGE ACADEMY — Application de cours
Streamlit app pour présentation + suivi pédagogique
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

from database import (get_all_sessions, get_session_by_num, update_session,
                       get_stats, authenticate, save_submission,
                       get_student_submissions, get_pending_submissions,
                       get_all_submissions_with_feedback, save_feedback)

# Auto-init de la base de données (pour Streamlit Cloud)
if not os.path.exists("lingua_bridge.db"):
    try:
        from init_data import main as _init_main
        _init_main()
    except Exception:
        pass

# =====================================================================
# CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="Lingua Bridge Academy",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        color: #3D1F5C;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        color: #FF6B35;
        font-size: 1.2rem;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3D1F5C;
        margin: 0.5rem 0;
    }
    .lesson-banner {
        background: #3D1F5C;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
    .answer-box {
        background: #F0F8F0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E7D32;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# SESSION STATE
# =====================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "current_session" not in st.session_state:
    st.session_state.current_session = None


# =====================================================================
# PAGE : LOGIN
# =====================================================================
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


# =====================================================================
# SIDEBAR
# =====================================================================
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
            st.rerun()


# =====================================================================
# PAGE : DASHBOARD PROF
# =====================================================================
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
    else:
        st.info("Todas las sesiones están completadas")
def page_change_password():
    st.markdown('<div class="main-header">🔐 Cambiar contraseña</div>',
                unsafe_allow_html=True)

    with st.form("change_pwd"):
        new_pwd = st.text_input("Nueva contraseña", type="password")
        confirm = st.text_input("Confirmar contraseña", type="password")

        if st.form_submit_button("Cambiar", type="primary"):
            if new_pwd != confirm:
                st.error("Las contraseñas no coinciden")
            elif len(new_pwd) < 6:
                st.error("Mínimo 6 caracteres")
            else:
                change_password(st.session_state.user["username"], new_pwd)
                st.success("✅ Contraseña cambiada")
                st.info("Cierra sesión y vuelve a entrar con la nueva contraseña.")

# =====================================================================
# PAGE : SESSION LIVE
# =====================================================================
def page_session_live():
    session_num = st.session_state.current_session
    if not session_num:
        st.error("No hay sesión seleccionada")
        if st.button("← Volver al panel"):
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
    class_prefix = lesson.replace(" ", "_") if lesson.startswith("Class") else None

    if class_prefix:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📄 Material del profesor")
            pptx_path = f"{class_prefix}_PPT.pptx"
            notes_path = f"{class_prefix}_Notes.pdf"

            if os.path.exists(pptx_path):
                with open(pptx_path, "rb") as f:
                    st.download_button("⬇️ Descargar PPTX", f,
                                        file_name=f"{class_prefix}_PPT.pptx",
                                        use_container_width=True)
            else:
                st.caption(f"⚠️ No encontrado: {pptx_path}")

            if os.path.exists(notes_path):
                with open(notes_path, "rb") as f:
                    st.download_button("⬇️ Descargar Notas", f,
                                        file_name=f"{class_prefix}_Notes.pdf",
                                        use_container_width=True)

        with col2:
            st.markdown("### 📘 Material del alumno")
            student_path = f"{class_prefix}_Student.pdf"
            if os.path.exists(student_path):
                with open(student_path, "rb") as f:
                    st.download_button("⬇️ Descargar Cuaderno", f,
                                        file_name=f"{class_prefix}_Student.pdf",
                                        use_container_width=True)

    st.markdown("---")

    with st.form("session_form"):
        attended = st.checkbox("✅ El alumno asistió",
                                value=bool(session["attended"]))
        score = st.slider("📊 Score (0-10)", 0.0, 10.0, 5.0, 0.5)
        notes = st.text_area("📝 Observaciones", value=session["notes"] or "",
                              height=150)

        if st.form_submit_button("💾 Guardar", use_container_width=True,
                                  type="primary"):
            update_session(session_num, 1 if attended else 0, score, notes)
            st.success("✅ Sesión guardada")
            st.balloons()


# =====================================================================
# PAGE : SESSIONS
# =====================================================================
def page_sessions():
    st.markdown('<div class="main-header">Todas las Sesiones</div>',
                unsafe_allow_html=True)

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


# =====================================================================
# PAGE : LECONS (SÉCURISÉ PAR RÔLE)
# =====================================================================
def page_lessons():
    user = st.session_state.user
    is_teacher = user["role"] == "teacher"

    if is_teacher:
        st.markdown('<div class="main-header">📚 Lecciones — Vista Profesor</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="main-header">📚 Mis Lecciones</div>',
                    unsafe_allow_html=True)
      # ============ DEBUG TEMPORAIRE ============
    with st.expander("🔧 DEBUG — Fichiers détectés"):
        all_files = sorted(os.listdir("."))
        st.write(f"**{len(all_files)} fichiers/dossiers :**")
        for f in all_files:
            exists = os.path.isfile(f)
            st.code(f"{'📄' if exists else '📁'} {f}")
    # ============ FIN DEBUG ============
      # ============ DOCUMENTOS GENERALES ============
    st.markdown("### 📁 Documentos generales del curso")
    st.caption("Guías, programa, metodología y recursos complementarios")

    general_docs = [
        ("00-Start_here.pdf", "🚀 Guía de inicio"),
        ("01-Syllabus.pdf", "📅 Programa del curso"),
        ("04-Preambule.pdf", "📖 Preámbulo"),
        ("05-Methodology_Guide.pdf", "🎓 Guía pedagógica"),
    ]

    if is_teacher:
        general_docs.append(
            ("02-Answer_Key_19_Leçons_Course_Slides.pdf", "✅ Corrigés PPTX")
        )
        general_docs.append(
            ("03-Answer_Key_19_Leçons_Additional_Exercises.pdf", "✅ Corrigés ejercicios")
        )
        general_docs.append(
            ("Progress_Tracker.xlsx", "📊 Progress Tracker")
        )

    cols = st.columns(2)
    for i, (filename, label) in enumerate(general_docs):
        with cols[i % 2]:
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    st.download_button(
                        f"⬇️ {label}",
                        f,
                        file_name=filename,
                        key=f"doc_{filename}",
                        use_container_width=True
                    )

    st.markdown("---")
    st.markdown("### 📚 Lecciones individuales")

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

    for class_name, title, level in lessons:
        with st.expander(f"📖 **{class_name}** — {title} ({level})"):
            prefix = class_name.replace(" ", "_")

            if is_teacher:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**📄 Material del profesor**")

                    pptx = f"{prefix}_PPT.pptx"
                    notes = f"{prefix}_Notes.pdf"

                    if os.path.exists(pptx):
                        with open(pptx, "rb") as f:
                            st.download_button("⬇️ PPTX", f,
                                file_name=f"{prefix}_PPT.pptx",
                                key=f"pptx_{prefix}",
                                use_container_width=True)
                    else:
                        st.caption(f"⚠️ Falta {pptx}")

                    if os.path.exists(notes):
                        with open(notes, "rb") as f:
                            st.download_button("⬇️ Notas del profesor", f,
                                file_name=f"{prefix}_Notes.pdf",
                                key=f"notes_{prefix}",
                                use_container_width=True)
                    else:
                        st.caption(f"⚠️ Falta {notes}")

                with col2:
                    st.markdown("**📘 Material del alumno**")
                    student = f"{prefix}_Student.pdf"
                    if os.path.exists(student):
                        with open(student, "rb") as f:
                            st.download_button("⬇️ Cuaderno", f,
                                file_name=f"{prefix}_Student.pdf",
                                key=f"student_{prefix}",
                                use_container_width=True)
                    else:
                        st.caption(f"⚠️ Falta {student}")
            else:
                st.markdown("**📘 Mi cuaderno de trabajo**")
                st.caption("Descarga el cuaderno para esta lección")
                student = f"{prefix}_Student.pdf"
                if os.path.exists(student):
                    with open(student, "rb") as f:
                        st.download_button(
                            f"⬇️ Descargar cuaderno — {class_name}",
                            f,
                            file_name=f"{prefix}_Student.pdf",
                            key=f"student_{prefix}",
                            use_container_width=True)
                else:
                    st.info("El cuaderno estará disponible pronto")


# =====================================================================
# PAGE : PROGRESO
# =====================================================================
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
        df_scores = df.dropna(subset=["Score_clean"])
        if not df_scores.empty:
            fig = px.line(df_scores, x="Date", y="Score_clean", markers=True,
                          color_discrete_sequence=["#3D1F5C"])
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay scores registrados")

    with col2:
        st.markdown("### 📊 Asistencia acumulada")
        df_sorted = df.sort_values("Date").reset_index(drop=True)
        df_sorted["Cumulative"] = df_sorted["attended"].cumsum()
        fig = px.area(df_sorted, x="Date", y="Cumulative",
                      color_discrete_sequence=["#FF6B35"])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================================
# PAGE : EXERCICES (élève)
# =====================================================================
def page_exercises():
    import time
    user = st.session_state.user
    student_id = user["id"]

    st.markdown('<div class="main-header">✏️ Mis ejercicios</div>',
                unsafe_allow_html=True)
    st.markdown("📌 Escribe tus respuestas y envíalas al profesor")

    with st.form("submit_exercise"):
        col1, col2 = st.columns(2)
        with col1:
            lesson = st.selectbox("Lección",
                                    [f"Class {i:02d}" for i in range(19)])
        with col2:
            exercise_num = st.number_input("Número de ejercicio",
                                             1, 20, 1)

        answer = st.text_area("Tu respuesta", height=200,
                                placeholder="Escribe aquí tu respuesta...")

        if st.form_submit_button("📤 Enviar al profesor",
                                  use_container_width=True, type="primary"):
            if answer.strip():
                save_submission(student_id, lesson, exercise_num, answer)
                st.success("✅ Respuesta enviada. El profesor la revisará pronto.")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.warning("⚠️ Escribe una respuesta antes de enviar")

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
            st.markdown("**Tu respuesta:**")
            st.markdown(f'<div class="answer-box">{sub["answer"]}</div>',
                        unsafe_allow_html=True)
            if has_fb:
                st.markdown("**📝 Feedback del profesor:**")
                st.success(sub["feedback"])
            else:
                st.caption("⏳ El profesor aún no ha corregido este ejercicio.")


# =====================================================================
# PAGE : SOUMISSIONS (prof)
# =====================================================================
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
            st.markdown(f"**{len(pending)} envío(s) pendiente(s)**")
            for sub in pending:
                with st.expander(f"🟡 {sub['full_name']} · {sub['lesson']} · "
                                  f"Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
                    st.markdown("**Respuesta de la estudiante:**")
                    st.markdown(f'<div class="answer-box">{sub["answer"]}</div>',
                                unsafe_allow_html=True)

                    fb = st.text_area("✏️ Tu retroalimentación", height=150,
                                       key=f"fb_{sub['id']}",
                                       placeholder="Excelente uso de... "
                                                   "Atención a...")

                    if st.button("💾 Enviar retroalimentación",
                                  key=f"send_{sub['id']}",
                                  use_container_width=True):
                        if fb.strip():
                            save_feedback(sub["id"], fb)
                            st.success("✅ Retroalimentación guardada")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("⚠️ Escribe una retroalimentación")

    with tab2:
        corrected = get_all_submissions_with_feedback()
        if not corrected:
            st.info("Aún no hay envíos corregidos")
        else:
            st.markdown(f"**{len(corrected)} envío(s) corregido(s)**")
            for sub in corrected:
                with st.expander(f"✅ {sub['full_name']} · {sub['lesson']} · "
                                  f"Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
                    st.markdown(f"**Respuesta:** {sub['answer']}")
                    st.markdown("**📝 Tu retroalimentación:**")
                    st.success(sub["feedback"])


# =====================================================================
# PAGE : CALENDRIER (élève)
# =====================================================================
def page_calendar():
    st.markdown('<div class="main-header">📅 Mi calendario</div>',
                unsafe_allow_html=True)

    sessions = get_all_sessions()
    for week in range(1, 14):
        wk = [s for s in sessions if s["week"] == week]
        if not wk:
            continue
        with st.expander(f"**Semana {week}** — {wk[0]['date']} al "
                          f"{wk[-1]['date']}"):
            for s in wk:
                status = "✅" if s["attended"] else "⏳"
                st.markdown(f"{status} **{s['session_num']}** · "
                            f"{s['date']} · {s['lesson']} — {s['content']}")


# =====================================================================
# PAGE : CERTIFICAT
# =====================================================================
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
        st.warning(f"⏳ Faltan {rem} sesiones para completar el curso")


# =====================================================================
# ROUTER
# =====================================================================
def page_change_password():
    import time
    from database import change_password

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
            st.markdown('<div class="sub-header">'
                        'Lingua Bridge Academy · English Course</div>',
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
