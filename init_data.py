# -*- coding: utf-8 -*-
"""
Initialise la base de données avec :
- Les 2 utilisateurs (prof + élève)
- Les 39 sessions
"""
from database import init_database, create_user, get_connection

SESSIONS_DATA = [
    ("S01", 1, "21/09/2026", "Lun", "Class 00", "Revision Class", "60 min"),
    ("S02", 1, "23/09/2026", "Mié", "Class 01", "My Daily Routine (p1)", "60 min"),
    ("S03", 1, "25/09/2026", "Vie", "Class 01", "My Daily Routine (p2) + Repaso", "60 min"),
    ("S04", 2, "28/09/2026", "Lun", "Class 02", "Yesterday & Last Weekend (p1)", "60 min"),
    ("S05", 2, "30/09/2026", "Mié", "Class 02", "Yesterday & Last Weekend (p2)", "60 min"),
    ("S06", 2, "02/10/2026", "Vie", "Class 03", "My Last Weekend (p1)", "60 min"),
    ("S07", 3, "05/10/2026", "Lun", "Class 03", "My Last Weekend (p2) + Repaso", "60 min"),
    ("S08", 3, "07/10/2026", "Mié", "Class 04", "My Future Plans (p1)", "60 min"),
    ("S09", 3, "09/10/2026", "Vie", "Class 04", "My Future Plans (p2)", "60 min"),
    ("S10", 4, "12/10/2026", "Lun", "Class 05", "My Week (p1)", "60 min"),
    ("S11", 4, "14/10/2026", "Mié", "Class 05", "My Week (p2) + Repaso", "60 min"),
    ("S12", 4, "16/10/2026", "Vie", "Class 06", "Life Experiences (p1)", "60 min"),
    ("S13", 5, "19/10/2026", "Lun", "Class 06", "Life Experiences (p2) + Repaso", "60 min"),
    ("S14", 5, "21/10/2026", "Mié", "Class 07", "How Long Have You...? (p1)", "60 min"),
    ("S15", 5, "23/10/2026", "Vie", "Class 07", "How Long Have You...? (p2)", "60 min"),
    ("S16", 6, "26/10/2026", "Lun", "Class 08", "What Have You Been Doing? (p1)", "60 min"),
    ("S17", 6, "28/10/2026", "Mié", "Class 08", "What Have You Been Doing? (p2)", "60 min"),
    ("S18", 6, "30/10/2026", "Vie", "Class 09", "What Were You Doing? (p1)", "60 min"),
    ("S19", 7, "03/11/2026", "Mar", "Class 09", "What Were You Doing? (p2) + Repaso", "60 min"),
    ("S20", 7, "04/11/2026", "Mié", "REPASO", "Bloque 1 (Class 00-09)", "60 min"),
    ("S21", 7, "06/11/2026", "Vie", "Class 10", "I Was Walking When... (p1)", "60 min"),
    ("S22", 8, "09/11/2026", "Lun", "Class 10", "I Was Walking When... (p2)", "60 min"),
    ("S23", 8, "11/11/2026", "Mié", "Class 11", "I Used To... (p1)", "60 min"),
    ("S24", 8, "13/11/2026", "Vie", "Class 11", "I Used To... (p2) + Repaso", "60 min"),
    ("S25", 9, "17/11/2026", "Mar", "Class 12", "If It Rains, I Will... (p1)", "60 min"),
    ("S26", 9, "18/11/2026", "Mié", "Class 12", "If It Rains, I Will... (p2)", "60 min"),
    ("S27", 9, "20/11/2026", "Vie", "Class 13", "What Would You Do If...? (p1)", "60 min"),
    ("S28", 10, "23/11/2026", "Lun", "Class 13", "What Would You Do If...? (p2) + Repaso", "60 min"),
    ("S29", 10, "25/11/2026", "Mié", "Class 14", "It Was Built In 1990 (p1)", "60 min"),
    ("S30", 10, "27/11/2026", "Vie", "Class 14", "It Was Built In 1990 (p2)", "60 min"),
    ("S31", 11, "30/11/2026", "Lun", "Class 15", "She Said That... (p1)", "60 min"),
    ("S32", 11, "02/12/2026", "Mié", "Class 15", "She Said That... (p2) + Repaso", "60 min"),
    ("S33", 11, "04/12/2026", "Vie", "Class 16", "The Person Who... (p1)", "60 min"),
    ("S34", 12, "07/12/2026", "Lun", "Class 16", "The Person Who... (p2) + Repaso", "60 min"),
    ("S35", 12, "09/12/2026", "Mié", "Class 17", "You Must Be Tired! (p1)", "60 min"),
    ("S36", 12, "11/12/2026", "Vie", "Class 17", "You Must Be Tired! (p2)", "60 min"),
    ("S37", 13, "14/12/2026", "Lun", "Class 18", "By Next Year, I Will Have... (p1)", "60 min"),
    ("S38", 13, "16/12/2026", "Mié", "Class 18", "By Next Year, I Will Have... (p2) + REPASO FINAL", "60 min"),
    ("S39", 13, "18/12/2026", "Vie", "FINAL", "Proyecto final + Certificado", "60 min"),
]


def init_sessions():
    conn = get_connection()
    c = conn.cursor()
    for s in SESSIONS_DATA:
        try:
            c.execute("""
                INSERT INTO sessions (session_num, week, date, day, lesson, content, duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, s)
        except Exception as e:
            print(f"Session {s[0]} déjà présente")
    conn.commit()
    conn.close()
    print(f"OK - {len(SESSIONS_DATA)} sessions importées")


def main():
    print("=" * 60)
    print("INITIALISATION DE LA BASE DE DONNÉES")
    print("=" * 60)

    init_database()
    print("OK - Tables créées")

    # Créer le prof
    if create_user("jean", "lingua2026", "teacher",
                   "Jean Thomas MONTREUIL", "jean@linguabridge.com"):
        print("OK - Prof créé : jean / lingua2026")
    else:
        print("Info - Prof déjà existant")

    # Créer l'élève
    if create_user("ingrid", "english2026", "student",
                   "Ingrid Sanchez Hermosa", "ingrid@email.com"):
        print("OK - Élève créée : ingrid / english2026")
    else:
        print("Info - Élève déjà existante")

    init_sessions()

    print("=" * 60)
    print("INITIALISATION TERMINÉE")
    print("=" * 60)


if __name__ == "__main__":
    main()