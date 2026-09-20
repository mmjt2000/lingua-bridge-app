# -*- coding: utf-8 -*-
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


@st.cache_resource
def get_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


@st.cache_resource(ttl=60)
def _get_spreadsheet():
    client = get_client()
    sheet_id = st.secrets["google_sheet"]["sheet_id"]
    return client.open_by_key(sheet_id)


def get_lang():
    return st.session_state.get("lang", "en")


def get_sheet(name):
    spreadsheet = _get_spreadsheet()
    lang = get_lang()
    if lang == "fr":
        if name == "sessions":
            name = "sessions_fr"
        elif name == "submissions":
            name = "submissions_fr"
    return spreadsheet.worksheet(name)


def authenticate(username, password):
    sheet = get_sheet("users")
    for r in sheet.get_all_records():
                if str(r["username"]) == username and str(r["password"]) == password:
                    return {
                        "id": int(r["id"]),
                        "username": r["username"],
                        "password": r["password"],
                        "role": r["role"],
                        "full_name": r["full_name"],
                        "email": r.get("email", ""),
                        "app_url": r.get("app_url", "")
            }
    return None


def change_password(username, new_password):
    sheet = get_sheet("users")
    for i, r in enumerate(sheet.get_all_records(), start=2):
        if str(r["username"]) == username:
            sheet.update_cell(i, 3, new_password)
            return True
    return False


def get_all_users():
    sheet = get_sheet("users")
    return [{"id": int(r["id"]), "username": r["username"], "role": r["role"], "full_name": r["full_name"]} for r in sheet.get_all_records()]


@st.cache_data(ttl=10)
def get_all_sessions():
    sheet = get_sheet("sessions")
    sessions = []
    for r in sheet.get_all_records():
        sessions.append({
            "session_num": r["session_num"],
            "week": int(r["week"]) if r["week"] != "" else 0,
            "date": r["date"],
            "day": r["day"],
            "lesson": r["lesson"],
            "content": r["content"],
            "duration": r["duration"],
            "attended": int(r["attended"]) if r["attended"] != "" else 0,
            "score": float(r["score"]) if r["score"] != "" else None,
            "notes": r["notes"] if r["notes"] != "" else None
        })
    return sessions


def get_session_by_num(session_num):
    for s in get_all_sessions():
        if s["session_num"] == session_num:
            return s
    return None


def update_session(session_num, attended, score=None, notes=None):
    sheet = get_sheet("sessions")
    for i, r in enumerate(sheet.get_all_records(), start=2):
        if r["session_num"] == session_num:
            sheet.update_cell(i, 8, attended)
            sheet.update_cell(i, 9, score if score else "")
            sheet.update_cell(i, 10, notes if notes else "")
            return True
    return False


@st.cache_data(ttl=10)
def get_stats():
    sessions = get_all_sessions()
    total = len(sessions)
    attended = sum(1 for s in sessions if s["attended"] == 1)
    scores = [s["score"] for s in sessions if s["score"] is not None]
    avg = round(sum(scores) / len(scores), 1) if scores else 0
    rate = round(attended / total * 100, 1) if total else 0
    return {"total": total, "attended": attended, "avg_score": avg, "attendance_rate": rate}


def save_submission(student_id, lesson, exercise_num, answer):
    sheet = get_sheet("submissions")
    records = sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        if int(r["student_id"]) == student_id and r["lesson"] == lesson and int(r["exercise_num"]) == exercise_num:
            sheet.update_cell(i, 5, answer)
            sheet.update_cell(i, 6, datetime.now().strftime("%Y-%m-%d %H:%M"))
            sheet.update_cell(i, 7, "")
            return True
    sheet.append_row([len(records) + 1, student_id, lesson, exercise_num, answer, datetime.now().strftime("%Y-%m-%d %H:%M"), ""])
    return True


def get_student_submissions(student_id):
    sheet = get_sheet("submissions")
    return [{"id": int(r["id"]), "student_id": int(r["student_id"]), "lesson": r["lesson"], "exercise_num": int(r["exercise_num"]), "answer": r["answer"], "submitted_at": r["submitted_at"], "feedback": r["feedback"] if r["feedback"] != "" else None} for r in sheet.get_all_records() if int(r["student_id"]) == student_id]


def get_pending_submissions():
    sheet = get_sheet("submissions")
    users = get_all_users()
    result = []
    for r in sheet.get_all_records():
        if r["feedback"] == "" or r["feedback"] is None:
            student = next((u for u in users if u["id"] == int(r["student_id"])), None)
            result.append({"id": int(r["id"]), "full_name": student["full_name"] if student else "?", "lesson": r["lesson"], "exercise_num": int(r["exercise_num"]), "answer": r["answer"], "submitted_at": r["submitted_at"], "feedback": None})
    return result


def get_all_submissions_with_feedback():
    sheet = get_sheet("submissions")
    users = get_all_users()
    result = []
    for r in sheet.get_all_records():
        if r["feedback"] and r["feedback"] != "":
            student = next((u for u in users if u["id"] == int(r["student_id"])), None)
            result.append({"id": int(r["id"]), "full_name": student["full_name"] if student else "?", "lesson": r["lesson"], "exercise_num": int(r["exercise_num"]), "answer": r["answer"], "submitted_at": r["submitted_at"], "feedback": r["feedback"]})
    return result


def save_feedback(submission_id, feedback):
    sheet = get_sheet("submissions")
    for i, r in enumerate(sheet.get_all_records(), start=2):
        if int(r["id"]) == submission_id:
            sheet.update_cell(i, 7, feedback)
            return True
    return False


def save_audio_submission(student_id, lesson, exercise_num, audio_bytes, filename):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    import io
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    folder_name = "Lingua Bridge Audios"
    response = drive_service.files().list(q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'", spaces='drive', fields='files(id, name)').execute()
    if response.get('files'):
        folder_id = response['files'][0]['id']
    else:
        folder_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder['id']
    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(audio_bytes), mimetype='audio/wav', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    drive_service.permissions().create(fileId=file['id'], body={'role': 'reader', 'type': 'anyone'}).execute()
    audio_link = file.get('webViewLink', '')
    sheet = get_sheet("submissions")
    records = sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        if int(r["student_id"]) == student_id and r["lesson"] == lesson and int(r["exercise_num"]) == exercise_num:
            sheet.update_cell(i, 5, f"Audio: {audio_link}")
            sheet.update_cell(i, 6, datetime.now().strftime("%Y-%m-%d %H:%M"))
            sheet.update_cell(i, 7, "")
            return True
    sheet.append_row([len(records) + 1, student_id, lesson, exercise_num, f"Audio: {audio_link}", datetime.now().strftime("%Y-%m-%d %H:%M"), ""])
    return True
