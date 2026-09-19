# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from sheets_db import get_all_sessions, get_session_by_num, update_session, get_stats, authenticate, save_submission, get_student_submissions, get_pending_submissions, get_all_submissions_with_feedback, save_feedback, change_password, get_lang, save_audio_submission

st.set_page_config(page_title="Lingua Bridge Academy", page_icon=":bridge_at_night:", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(135deg, #E2EFDA 0%, #F5F9F2 100%); }
    .main-header { color: #3D1F5C; font-size: 2.5rem; font-weight: 700; text-align: center; padding: 1.5rem 0 1rem 0; }
    .sub-header { color: #FF6B35; font-size: 1.1rem; text-align: center; font-style: italic; margin-bottom: 2rem; }
    .metric-card { background: white; padding: 1.25rem 1.5rem; border-radius: 16px; border-left: 5px solid #3D1F5C; margin: 0.75rem 0; box-shadow: 0 4px 20px rgba(61, 31, 92, 0.08); }
    .lesson-banner { background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%); color: white; padding: 1.25rem; border-radius: 16px; font-size: 1.5rem; font-weight: 600; text-align: center; }
    .answer-box { background: #F0F8F0; padding: 1rem 1.25rem; border-radius: 12px; border-left: 4px solid #2E7D32; color: #1B5E20; }
    .stButton > button { border-radius: 12px !important; font-weight: 600 !important; }
    .stDownloadButton > button { background: white !important; color: #3D1F5C !important; border: 1.5px solid #3D1F5C !important; border-radius: 12px !important; }
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
        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
        st.markdown("""<div style='text-align: center;'><h1 style='color: #3D1F5C; font-size: 3rem; margin-bottom: 0;'>Lingua Bridge Academy</h1><p style='color: #C9A227; font-style: italic; margin-top: 0;'>Building bridges through language</p><hr style='border: 1px solid #C9A227;'></div>""", unsafe_allow_html=True)
        st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
        st.markdown("### Iniciar sesion")
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contrasena", type="password")
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
                        st.error("Usuario o contrasena incorrectos")


def render_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown("""<div style='text-align: center; padding: 1rem 0;'><h2 style='color: #3D1F5C; margin-bottom: 0;'>Lingua Bridge</h2><p style='color: #C9A227; font-style: italic; font-size: 0.8rem; margin-top: 0;'>Building bridges through language</p></div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Curso**")
        lang_options = {"Ingles": "en", "Frances": "fr"}
        current_label = "Frances" if st.session_state.lang == "fr" else "Ingles"
        selected = st.radio("", list(lang_options.keys()), index=list(lang_options.keys()).index(current_label), label_visibility="collapsed", key="lang_selector")
        new_lang = lang_options[selected]
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.session_state.current_session = None
            st.rerun()
        st.markdown("---")
        role_label = "Profesor" if user["role"] == "teacher" else "Estudiante"
        st.markdown(f"""<div style='padding: 0.6rem; background: linear-gradient(135deg, #3D1F5C 0%, #5A2F8A 100%); border-radius: 10px; margin: 0.5rem 0 1rem 0;'><div style='color: white; font-size: 0.85rem; font-weight: 600;'>{user['full_name']}</div><div style='color: #FFD54F; font-size: 0.7rem; font-weight: 600;'>{role_label}</div></div>""", unsafe_allow_html=True)
        if user["role"] == "teacher":
            menu_items = [("Panel", "dashboard"), ("Envios", "submissions"), ("Sesiones", "sessions"), ("Lecciones", "lessons"), ("Pronunciacion", "pronunciation"), ("Progreso", "progress"), ("Certificado", "certificate"), ("Cambiar contrasena", "change_password")]
        else:
            menu_items = [("Inicio", "dashboard"), ("Mis lecciones", "lessons"), ("Pronunciacion", "pronunciation"), ("Mis ejercicios", "exercises"), ("Mi progreso", "progress"), ("Mi calendario", "calendar")]
        for label, key in menu_items:
            is_active = st.session_state.page == key
            if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state.page = key
                st.rerun()
        st.markdown("---")
        if st.button("Cerrar sesion", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.session_state.lang = "en"
            st.rerun()


def page_teacher_dashboard():
    st.markdown('<div class="main-header">Panel del Profesor</div>', unsafe_allow_html=True)
    stats = get_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sesiones totales", stats["total"])
    with col2:
        st.metric("Asistidas", stats["attended"])
    with col3:
        st.metric("Promedio", f"{stats['avg_score']}/10")
    with col4:
        st.metric("Tasa de asistencia", f"{stats['attendance_rate']}%")
    st.markdown("---")
    sessions = get_all_sessions()
    next_session = next((s for s in sessions if not s["attended"]), None)
    if next_session:
        st.markdown("### Proxima sesion")
        st.markdown(f"""<div class="metric-card"><h3 style='color: #3D1F5C; margin: 0;'>{next_session['session_num']} - {next_session['lesson']}</h3><p style='color: #666;'>{next_session['date']} ({next_session['day']}) - {next_session['duration']}</p><p>{next_session['content']}</p></div>""", unsafe_allow_html=True)
        if st.button("Iniciar sesion", type="primary", use_container_width=True):
            st.session_state.current_session = next_session["session_num"]
            st.session_state.page = "session_live"
            st.rerun()


def page_session_live():
    session_num = st.session_state.current_session
    if not session_num:
        st.error("No hay sesion seleccionada")
        if st.button("Volver"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    session = get_session_by_num(session_num)
    if not session:
        st.error(f"Sesion {session_num} no encontrada")
        return
    st.markdown(f'<div class="lesson-banner">{session["session_num"]} - {session["lesson"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**Contenido:** {session['content']} - **Duracion:** {session['duration']}")
    if st.button("Volver", use_container_width=True):
        st.session_state.page = "dashboard"
        st.rerun()
    st.markdown("---")
    lang = get_lang()
    lesson = session["lesson"]
    prefix = lesson[:3] if (lang == "fr" and lesson.startswith("L")) else lesson.replace(" ", "_")
    base_path = "fr/" if lang == "fr" else ""
    if prefix:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Material del profesor")
            pptx = f"{base_path}{prefix}_PPT.pptx"
            notes = f"{base_path}{prefix}_Notes.pdf"
            if os.path.exists(pptx):
                with open(pptx, "rb") as f:
                    st.download_button("Descargar PPTX", f, file_name=f"{prefix}_PPT.pptx", use_container_width=True)
            if os.path.exists(notes):
                with open(notes, "rb") as f:
                    st.download_button("Descargar Notas", f, file_name=f"{prefix}_Notes.pdf", use_container_width=True)
        with col2:
            st.markdown("### Material del alumno")
            suffix = "_Cuaderno.pdf" if lang == "fr" else "_Student.pdf"
            student = f"{base_path}{prefix}{suffix}"
            if os.path.exists(student):
                with open(student, "rb") as f:
                    st.download_button("Descargar Cuaderno", f, file_name=f"{prefix}{suffix}", use_container_width=True)
    st.markdown("---")
    with st.form("session_form"):
        attended = st.checkbox("El alumno asistio", value=bool(session["attended"]))
        score = st.slider("Puntuacion (0-10)", 0.0, 10.0, 5.0, 0.5)
        notes = st.text_area("Observaciones", value=session["notes"] or "", height=150)
        if st.form_submit_button("Guardar", use_container_width=True, type="primary"):
            update_session(session_num, 1 if attended else 0, score, notes)
            st.success("Sesion guardada")


def page_sessions():
    st.markdown('<div class="main-header">Todas las Sesiones</div>', unsafe_allow_html=True)
    sessions = get_all_sessions()
    for row in sessions:
        status = "[OK]" if row["attended"] else "[--]"
        with st.expander(f"{status} {row['session_num']} - {row['date']} - {row['lesson']}"):
            st.markdown(f"**Contenido:** {row['content']}")
            if st.button("Abrir", key=f"open_{row['session_num']}", use_container_width=True):
                st.session_state.current_session = row["session_num"]
                st.session_state.page = "session_live"
                st.rerun()


def page_lessons():
    user = st.session_state.user
    is_teacher = user["role"] == "teacher"
    lang = get_lang()
    if lang == "fr":
        title = "Lecciones - Vista Profesor" if is_teacher else "Mis Lecciones"
        lessons = [("L01", "Bonjour !", "A1"), ("L02", "Je suis", "A1"), ("L03", "J'ai", "A1"), ("L04", "Le/la/les", "A1"), ("L05", "Je parle", "A1"), ("L06", "Quelle heure", "A1"), ("L07", "Je vais, je fais", "A1"), ("L08", "Mon/ma/mes", "A1"), ("L09", "Je ne pas", "A1"), ("L10", "Est-ce que", "A1"), ("L11", "Le, la, lui, leur", "A1+"), ("L12", "Plus que", "A1+"), ("L13", "J'ai mange", "A1+"), ("L14", "Je suis alle", "A1+"), ("L15", "Quand j'etais", "A1+"), ("L16", "Je vais partir", "A1+"), ("L17", "Je voudrais", "A1+"), ("L18", "Qui, que, ou", "A1+"), ("L19", "Recapitulons", "A1+")]
        base_path = "fr/"
        student_suffix = "_Cuaderno.pdf"
    else:
        title = "Lecciones - Vista Profesor" if is_teacher else "Mis Lecciones"
        lessons = [("Class 00", "Revision Class", "A1"), ("Class 01", "My Daily Routine", "A1"), ("Class 02", "Yesterday & Last Weekend", "A2"), ("Class 03", "My Last Weekend", "A2"), ("Class 04", "My Future Plans", "A2"), ("Class 05", "My Week", "A2"), ("Class 06", "My Life Experiences", "B1"), ("Class 07", "How Long Have You", "B1"), ("Class 08", "What Have You Been Doing", "B1"), ("Class 09", "What Were You Doing", "B1"), ("Class 10", "I Was Walking When", "B1"), ("Class 11", "I Used To", "B1"), ("Class 12", "If It Rains, I Will", "B2"), ("Class 13", "What Would You Do If", "B2"), ("Class 14", "It Was Built In 1990", "B2"), ("Class 15", "She Said That", "B2"), ("Class 16", "The Person Who", "B2"), ("Class 17", "You Must Be Tired", "B2"), ("Class 18", "By Next Year, I Will Have", "B2")]
        base_path = ""
        student_suffix = "_Student.pdf"
    st.markdown(f'<div class="main-header">{title}</div>', unsafe_allow_html=True)
    st.markdown("### Documentos generales del curso")
    if lang == "fr":
        docs = [("fr/syllabus_fr.pdf", "Programa del curso"), ("fr/methodology_guide_fr.pdf", "Guia pedagogica")]
        if is_teacher:
            docs.append(("fr/progress_tracker_fr.xlsx", "Progress Tracker FR"))
            docs.append(("fr/corriges_fr.pdf", "Corriges"))
    else:
        docs = [("00- Start_here.pdf", "Guia de inicio"), ("01- Syllabus.pdf", "Programa del curso"), ("04- Preambule.pdf", "Preambulo"), ("05- Methodology_Guide.pdf", "Guia pedagogica")]
        if is_teacher:
            docs.append(("02- Answer_Key_19_Lecons_Course_Slides.pdf", "Corriges PPTX"))
            docs.append(("03- Answer_Key_19_Lecons_Additional_Exercices.pdf", "Corriges ejercicios"))
            docs.append(("Progress_Tracker.xlsx", "Progress Tracker"))
    cols = st.columns(2)
    for i, (filename, label) in enumerate(docs):
        with cols[i % 2]:
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    st.download_button(f"Descargar - {label}", f, file_name=filename.split("/")[-1], key=f"doc_{lang}_{filename}", use_container_width=True)
    st.markdown("---")
    st.markdown("### Lecciones individuales")
    for class_name, title_l, level in lessons:
        with st.expander(f"**{class_name}** - {title_l} ({level})"):
            prefix = class_name.replace(" ", "_")
            if is_teacher:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Material del profesor**")
                    pptx = f"{base_path}{prefix}_PPT.pptx"
                    notes = f"{base_path}{prefix}_Notes.pdf"
                    if os.path.exists(pptx):
                        with open(pptx, "rb") as f:
                            st.download_button("Descargar PPTX", f, file_name=f"{prefix}_PPT.pptx", key=f"pptx_{prefix}_{lang}", use_container_width=True)
                    if os.path.exists(notes):
                        with open(notes, "rb") as f:
                            st.download_button("Descargar Notas", f, file_name=f"{prefix}_Notes.pdf", key=f"notes_{prefix}_{lang}", use_container_width=True)
                with col2:
                    st.markdown("**Material del alumno**")
                    student = f"{base_path}{prefix}{student_suffix}"
                    if os.path.exists(student):
                        with open(student, "rb") as f:
                            st.download_button("Descargar Cuaderno", f, file_name=f"{prefix}{student_suffix}", key=f"student_{prefix}_{lang}", use_container_width=True)
            else:
                student = f"{base_path}{prefix}{student_suffix}"
                if os.path.exists(student):
                    with open(student, "rb") as f:
                        st.download_button(f"Descargar cuaderno - {class_name}", f, file_name=f"{prefix}{student_suffix}", key=f"student_{prefix}_{lang}", use_container_width=True)


def page_pronunciation():
    lang = get_lang()
    st.markdown('<div class="main-header">Pronunciacion</div>', unsafe_allow_html=True)
    try:
        from pronunciation_data import PRONUNCIATION_DATA
        data = PRONUNCIATION_DATA.get(lang, {})
        if not data:
            st.warning("Contenido no disponible.")
            return
        lessons_list = [f"L{i:02d}" for i in range(1, 20)] if lang == "fr" else [f"Class {i:02d}" for i in range(19)]
        available = [l for l in lessons_list if l in data]
        if not available:
            st.warning("No hay datos disponibles.")
            return
        selected = st.selectbox("Leccion", available, index=0)
        lesson_data = data[selected]
        st.markdown(f"## {lesson_data['title']}")
        st.info(f"Consejo: {lesson_data['tip']}")
        st.markdown("### Palabras para practicar")
        for word in lesson_data["words"]:
            st.markdown(f"- {word}")
        st.markdown("### Frases completas")
        for phrase in lesson_data["phrases"]:
            st.markdown(f"- {phrase}")
    except ImportError:
        st.info("Seccion en construccion")


def page_progress():
    st.markdown('<div class="main-header">Mi Progreso</div>', unsafe_allow_html=True)
    sessions = get_all_sessions()
    df = pd.DataFrame(sessions)
    df["Date"] = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
    df["Score_clean"] = pd.to_numeric(df["score"], errors="coerce")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Evolucion de puntuaciones")
        df_s = df.dropna(subset=["Score_clean"])
        if not df_s.empty:
            fig = px.line(df_s, x="Date", y="Score_clean", markers=True, color_discrete_sequence=["#3D1F5C"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay puntuaciones aun")
    with col2:
        st.markdown("### Asistencia acumulada")
        df_sorted = df.sort_values("Date").reset_index(drop=True)
        df_sorted["Cumulative"] = df_sorted["attended"].cumsum()
        fig = px.area(df_sorted, x="Date", y="Cumulative", color_discrete_sequence=["#FF6B35"])
        st.plotly_chart(fig, use_container_width=True)


def page_exercises():
    import time
    user = st.session_state.user
    student_id = user["id"]
    lang = get_lang()
    st.markdown('<div class="main-header">Mis Ejercicios</div>', unsafe_allow_html=True)
    lessons_opts = [f"L{i:02d}" for i in range(1, 20)] if lang == "fr" else [f"Class {i:02d}" for i in range(19)]
    tab_text, tab_audio = st.tabs(["Escrito", "Audio"])
    with tab_text:
        with st.form("submit_text"):
            col1, col2 = st.columns(2)
            with col1:
                lesson = st.selectbox("Leccion", lessons_opts, key="lesson_text")
            with col2:
                exercise_num = st.number_input("Numero", 1, 20, 1, key="ex_text")
            answer = st.text_area("Tu respuesta", height=200, key="answer_text")
            if st.form_submit_button("Enviar al profesor", use_container_width=True, type="primary"):
                if answer.strip():
                    save_submission(student_id, lesson, exercise_num, answer)
                    st.success("Respuesta enviada")
                    time.sleep(1)
                    st.rerun()
    with tab_audio:
        st.markdown("**Graba o sube tu audio**")
        col1, col2 = st.columns(2)
        with col1:
            lesson_audio = st.selectbox("Leccion", lessons_opts, key="lesson_audio")
        with col2:
            exercise_num_audio = st.number_input("Numero", 1, 20, 1, key="ex_audio")
        audio_value = st.audio_input("Graba tu audio", key="recorder")
        uploaded_file = st.file_uploader("O sube un archivo", type=["wav", "mp3", "m4a", "ogg"], key="uploader")
        audio_bytes = None
        if audio_value is not None:
            audio_bytes = audio_value.getvalue()
        if uploaded_file is not None:
            audio_bytes = uploaded_file.getvalue()
        if audio_bytes is not None:
            if st.button("Enviar audio", use_container_width=True, type="primary"):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{lang.upper()}_{lesson_audio}_Ej{exercise_num_audio}_{timestamp}.wav"
                    save_audio_submission(student_id, lesson_audio, exercise_num_audio, audio_bytes, filename)
                    st.success("Audio enviado")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("### Mis envios")
    submissions = get_student_submissions(student_id)
    if not submissions:
        st.info("No hay envios aun")
        return
    for sub in submissions:
        has_fb = sub["feedback"] and sub["feedback"].strip()
        status = "Corregido" if has_fb else "En espera"
        with st.expander(f"{status} - {sub['lesson']} - Ej. {sub['exercise_num']}"):
            st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
            st.markdown(f'<div class="answer-box">{sub["answer"]}</div>', unsafe_allow_html=True)
            if has_fb:
                st.success(sub["feedback"])


def page_submissions():
    import time
    st.markdown('<div class="main-header">Envios de la estudiante</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["En espera", "Corregidas"])
    with tab1:
        pending = get_pending_submissions()
        if not pending:
            st.success("No hay envios pendientes")
        else:
            for sub in pending:
                with st.expander(f"{sub['full_name']} - {sub['lesson']} - Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Enviado:** {sub['submitted_at'][:16]}")
                    st.markdown(f'<div class="answer-box">{sub["answer"]}</div>', unsafe_allow_html=True)
                    fb = st.text_area("Retroalimentacion", height=150, key=f"fb_{sub['id']}")
                    if st.button("Enviar", key=f"send_{sub['id']}", use_container_width=True):
                        if fb.strip():
                            save_feedback(sub["id"], fb)
                            st.success("Guardado")
                            time.sleep(1)
                            st.rerun()
    with tab2:
        corrected = get_all_submissions_with_feedback()
        if not corrected:
            st.info("No hay envios corregidos")
        else:
            for sub in corrected:
                with st.expander(f"{sub['full_name']} - {sub['lesson']} - Ej. {sub['exercise_num']}"):
                    st.markdown(f"**Respuesta:** {sub['answer']}")
                    st.success(sub["feedback"])


def page_calendar():
    st.markdown('<div class="main-header">Mi Calendario</div>', unsafe_allow_html=True)
    sessions = get_all_sessions()
    weeks = sorted(set(s["week"] for s in sessions))
    for week in weeks:
        wk = [s for s in sessions if s["week"] == week]
        with st.expander(f"**Semana {week}** - {wk[0]['date']} al {wk[-1]['date']}"):
            for s in wk:
                status = "[OK]" if s["attended"] else "[--]"
                st.markdown(f"{status} **{s['session_num']}** - {s['date']} - {s['lesson']} - {s['content']}")


def page_certificate():
    st.markdown('<div class="main-header">Certificado</div>', unsafe_allow_html=True)
    stats = get_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Progreso", f"{stats['attended']}/{stats['total']}")
    with col2:
        st.metric("Promedio", f"{stats['avg_score']}/10")
    with col3:
        st.metric("Asistencia", f"{stats['attendance_rate']}%")
    if stats["attended"] >= stats["total"]:
        st.success("Curso completado")
    else:
        rem = stats["total"] - stats["attended"]
        st.warning(f"Faltan {rem} sesiones")


def page_change_password():
    import time
    st.markdown('<div class="main-header">Cambiar Contrasena</div>', unsafe_allow_html=True)
    with st.form("change_pwd"):
        new_pwd = st.text_input("Nueva contrasena", type="password")
        confirm = st.text_input("Confirmar contrasena", type="password")
        if st.form_submit_button("Cambiar", type="primary", use_container_width=True):
            if new_pwd != confirm:
                st.error("Las contrasenas no coinciden")
            elif len(new_pwd) < 6:
                st.error("Minimo 6 caracteres")
            else:
                change_password(st.session_state.user["username"], new_pwd)
                st.success("Contrasena cambiada")
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
            st.markdown('<div class="main-header">Bienvenida, Ingrid</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-header">Lingua Bridge Academy - Ingles y Frances</div>', unsafe_allow_html=True)
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
