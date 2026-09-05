import streamlit as st
import sqlite3
from datetime import datetime
import os

# Set page configuration to wide mode for side-by-side panels
st.set_page_config(
    page_title="Writer's Desk",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE SETUP ---
DB_FILE = "writers_desk.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database with tblWork schema from the Writer's Desk design."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tblWork (
            WorkID INTEGER PRIMARY KEY AUTOINCREMENT,
            OriginalTitle TEXT NOT NULL,
            FinalTitle TEXT,
            CreationDate TEXT,
            Language TEXT DEFAULT 'Polish',
            Genre TEXT,
            Status TEXT DEFAULT 'Draft',
            WorkText TEXT,
            Notes TEXT,
            Tags TEXT,
            WorkCode TEXT,
            CreatedAt TEXT,
            UpdatedAt TEXT
        )
    """)
    # Add some sample data if the table is empty so the user can see it in action
    cursor.execute("SELECT COUNT(*) FROM tblWork")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sample_works = [
            (
                "Deszcz jesienny", 
                "Cienie we mgle", 
                "2026-09-01", 
                "Polish", 
                "Poetry", 
                "Draft",
                "O szyby deszcz dzwoni, deszcz dzwoni jesienny\nI pluszcze jednaki, miarowy, niezmienny,\nKiedyś o zmierzchu w szarym pokoju\nCzekałem na ciebie w cichym niepokoju...",
                "Inspiracja klasycznym wierszem Staffa. Dopracować rytm w trzeciej strofie.",
                "deszcz, nostalgia, jesień",
                "POEM-001",
                now,
                now
            ),
            (
                "Katedra ze światła", 
                "Katedra", 
                "2026-08-15", 
                "Polish", 
                "Sci-Fi Short Story", 
                "Completed",
                "Stali przed wrotami wzniesionymi z czystego, spolaryzowanego światła. \n- Czy to tutaj? - zapytał młodszy inżynier, poprawiając gogle ochronne. \n- Tutaj - odparła, nie odrywając wzroku od mieniących się struktur.",
                "Opowiadanie inspirowane architekturą gotycką i fizyką kwantową.",
                "fantastyka, kosmos, architektura",
                "SF-002",
                now,
                now
            )
        ]
        cursor.executemany("""
            INSERT INTO tblWork (
                OriginalTitle, FinalTitle, CreationDate, Language, Genre, Status, 
                WorkText, Notes, Tags, WorkCode, CreatedAt, UpdatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_works)
        conn.commit()
    conn.close()

# Initialize the database immediately
init_db()

# --- DATABASE CRUD OPERATIONS ---
def fetch_all_works(search_query=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        cursor.execute(
            "SELECT * FROM tblWork WHERE OriginalTitle LIKE ? OR FinalTitle LIKE ? OR Tags LIKE ? ORDER BY WorkID DESC",
            (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")
        )
    else:
        cursor.execute("SELECT * FROM tblWork ORDER BY WorkID DESC")
    works = cursor.fetchall()
    conn.close()
    return works

def fetch_work_by_id(work_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tblWork WHERE WorkID = ?", (work_id,))
    work = cursor.fetchone()
    conn.close()
    return work

def insert_work(original_title, final_title, creation_date, language, genre, status, work_text, notes, tags, work_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO tblWork (
            OriginalTitle, FinalTitle, CreationDate, Language, Genre, Status, 
            WorkText, Notes, Tags, WorkCode, CreatedAt, UpdatedAt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (original_title, final_title, creation_date, language, genre, status, work_text, notes, tags, work_code, now, now))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def update_work(work_id, original_title, final_title, creation_date, language, genre, status, work_text, notes, tags, work_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE tblWork SET 
            OriginalTitle = ?, FinalTitle = ?, CreationDate = ?, Language = ?, 
            Genre = ?, Status = ?, WorkText = ?, Notes = ?, Tags = ?, 
            WorkCode = ?, UpdatedAt = ?
        WHERE WorkID = ?
    """, (original_title, final_title, creation_date, language, genre, status, work_text, notes, tags, work_code, now, work_id))
    conn.commit()
    conn.close()

def delete_work(work_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblWork WHERE WorkID = ?", (work_id,))
    conn.commit()
    conn.close()

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    /* Styling for the Writer's Desk App */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .writer-header {
        font-family: 'Georgia', serif;
        font-weight: 700;
        color: #2E4057;
        border-bottom: 2px solid #D1D5DB;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .read-panel-title {
        font-family: 'Georgia', serif;
        color: #1F2937;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .read-panel-subtitle {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #6B7280;
        font-size: 0.95rem;
        margin-bottom: 20px;
    }
    .read-panel-paper {
        background-color: #FCFBF7;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 30px;
        font-family: 'Georgia', serif;
        font-size: 1.15rem;
        line-height: 1.8;
        color: #2D3748;
        white-space: pre-wrap; /* Keeps line breaks */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        min-height: 400px;
        margin-bottom: 15px;
    }
    .meta-tag {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    .sidebar-title {
        font-family: 'Georgia', serif;
        font-weight: bold;
        font-size: 1.3rem;
        color: #1F2937;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'selected_work_id' not in st.session_state:
    st.session_state.selected_work_id = None
if 'mode' not in st.session_state:
    st.session_state.mode = 'view' # modes: 'view', 'add'

# Callback to change selected work
def select_work(work_id):
    st.session_state.selected_work_id = work_id
    st.session_state.mode = 'view'

# Callback to switch to "Add New Work" mode
def set_add_mode():
    st.session_state.mode = 'add'
    st.session_state.selected_work_id = None

# --- SIDEBAR: NAVIGATOR & SEARCH ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">✍️ Writer\'s Desk Navigator</div>', unsafe_allow_html=True)
    
    # 1. Search Box (Equivalent to txtSearch)
    search_query = st.text_input("Wyszukaj utwór... (Search Title / Tag)", value="", placeholder="Tytuł lub tag...")
    
    # "Add New" Button
    st.button("➕ Nowy utwór (Add New)", on_click=set_add_mode, use_container_width=True, type="primary")
    
    st.markdown("---")
    st.markdown("**Lista utworów / Works List**")
    
    # Fetch works based on search query
    works_list = fetch_all_works(search_query)
    
    if works_list:
        for idx, work in enumerate(works_list):
            title = work['OriginalTitle']
            genre = work['Genre'] or "Brak gatunku"
            status = work['Status'] or "Draft"
            work_id = work['WorkID']
            
            # Determine visual indication for the selected work
            is_selected = (st.session_state.selected_work_id == work_id)
            btn_label = f"📖 {title} ({genre})" if is_selected else f"{title} ({genre})"
            
            # Clicking a work select it
            st.button(
                btn_label, 
                key=f"sidebar_btn_{work_id}_{idx}", 
                on_click=select_work, 
                args=(work_id,), 
                use_container_width=True
            )
    else:
        st.info("Brak utworów pasujących do kryteriów.")

# Set default selection if none and works exist
if st.session_state.selected_work_id is None and st.session_state.mode == 'view' and works_list:
    st.session_state.selected_work_id = works_list[0]['WorkID']

# --- MAIN WORKSPACE ---
st.markdown('<h1 class="writer-header">Writer’s Desk &mdash; Open-Source Edition</h1>', unsafe_allow_html=True)

# ----------------- MODE: VIEW / EDIT (DUAL PANELS) -----------------
if st.session_state.mode == 'view' and st.session_state.selected_work_id is not None:
    work = fetch_work_by_id(st.session_state.selected_work_id)
    
    if work:
        # Create the two columns for side-by-side reading and editing
        col_read, col_edit = st.columns([1, 1], gap="large")
        
        # --- LEFT PANEL: READ PANEL ---
        with col_read:
            st.subheader("📖 Read Panel (Podgląd utworu)")
            
            title_disp = work['FinalTitle'] if work['FinalTitle'] else work['OriginalTitle']
            st.markdown(f'<div class="read-panel-title">{title_disp}</div>', unsafe_allow_html=True)
            
            # Subtitle metadata row
            creation_str = f"Powstał: {work['CreationDate']}" if work['CreationDate'] else "Brak daty powstania"
            st.markdown(f'<div class="read-panel-subtitle">{work["Genre"]} | {creation_str} | Status: **{work["Status"]}**</div>', unsafe_allow_html=True)
            
            # Display formatted poetry or text
            text_disp = work['WorkText'] if work['WorkText'] else "*Utwór nie zawiera jeszcze tekstu.*"
            st.markdown(f'<div class="read-panel-paper">{text_disp}</div>', unsafe_allow_html=True)
            
            # Display Tags and Notes
            if work['Tags']:
                st.markdown("**Tagi:**")
                tags_list = [t.strip() for t in work['Tags'].split(',') if t.strip()]
                for tag in tags_list:
                    st.markdown(f'<span class="meta-tag">#{tag}</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
            if work['Notes']:
                st.info(f"**Notatki autora:**\n\n{work['Notes']}")
                
            st.caption(f"ID: {work['WorkID']} | Utworzono: {work['CreatedAt']} | Zmodyfikowano: {work['UpdatedAt']}")

        # --- RIGHT PANEL: EDIT PANEL ---
        with col_edit:
            st.subheader("✏️ Edit Panel (Edycja utworu)")
            
            # Use a form to capture all updates
            with st.form(key=f"edit_form_{work['WorkID']}"):
                edit_orig_title = st.text_input("Tytuł roboczy (Original Title) *", value=work['OriginalTitle'])
                edit_final_title = st.text_input("Tytuł ostateczny (Final Title)", value=work['FinalTitle'] or "")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    edit_genre = st.text_input("Gatunek (Genre)", value=work['Genre'] or "")
                with c2:
                    # Date picking - handle potential string errors gracefully
                    default_date = datetime.today()
                    if work['CreationDate']:
                        try:
                            default_date = datetime.strptime(work['CreationDate'], "%Y-%m-%d")
                        except ValueError:
                            pass
                    edit_creation_date = st.date_input("Data powstania (Creation Date)", value=default_date).strftime("%Y-%m-%d")
                with c3:
                    status_options = ["Draft", "In Progress", "Completed", "Submitted", "Published", "Archived"]
                    current_status_idx = status_options.index(work['Status']) if work['Status'] in status_options else 0
                    edit_status = st.selectbox("Status", options=status_options, index=current_status_idx)
                
                c4, c5 = st.columns(2)
                with c4:
                    edit_language = st.text_input("Język oryginału (Language)", value=work['Language'] or "Polish")
                with c5:
                    edit_code = st.text_input("Kod utworu (Work Code)", value=work['WorkCode'] or "")
                
                edit_text = st.text_area("Tekst utworu (Work Text)", value=work['WorkText'] or "", height=250)
                edit_notes = st.text_area("Notatki (Notes)", value=work['Notes'] or "", height=100)
                edit_tags = st.text_input("Tagi (rozdzielone przecinkami)", value=work['Tags'] or "")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.form_submit_button(label="Zapisz zmiany (Save Changes)", use_container_width=True)
                
                if submit_button:
                    if not edit_orig_title.strip():
                        st.error("Tytuł roboczy jest wymagany!")
                    else:
                        update_work(
                            work['WorkID'],
                            edit_orig_title.strip(),
                            edit_final_title.strip() if edit_final_title.strip() else None,
                            edit_creation_date,
                            edit_language.strip(),
                            edit_genre.strip(),
                            edit_status,
                            edit_text,
                            edit_notes,
                            edit_tags,
                            edit_code.strip()
                        )
                        st.success("Zmiany zostały pomyślnie zapisane!")
                        st.rerun()
                                # Przycisk usuwania wewnątrz formularza
                delete_button = st.form_submit_button(label="🗑️ Usuń utwór (Delete Work)", use_container_width=True)

                if delete_button:
                    delete_work(work['WorkID'])
                    # Resetujemy wybór utworu, aby aplikacja nie szukała usuniętego rekordu
                    st.session_state.selected_work_id = None
                    st.success("Utwór został pomyślnie usunięty!")
                    st.rerun()


# ----------------- MODE: ADD NEW (INJECTION FORM) -----------------
elif st.session_state.mode == 'add':
    st.subheader("➕ Inject New Work to Database (Dodaj nowy utwór)")
    
    with st.form(key="add_new_work_form"):
        new_orig_title = st.text_input("Tytuł roboczy (Original Title) *", placeholder="Np. Jesienne liście")
        new_final_title = st.text_input("Tytuł ostateczny (Final Title)", placeholder="Pozostaw puste, jeśli nie znasz ostatecznego")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            new_genre = st.text_input("Gatunek (Genre)", placeholder="Np. Poetry, Short Story")
        with c2:
            new_creation_date = st.date_input("Data powstania (Creation Date)", value=datetime.today()).strftime("%Y-%m-%d")
        with c3:
            new_status = st.selectbox("Status", options=["Draft", "In Progress", "Completed", "Submitted", "Published", "Archived"])
            
        c4, c5 = st.columns(2)
        with c4:
            new_language = st.text_input("Język oryginału (Language)", value="Polish")
        with c5:
            new_code = st.text_input("Kod utworu (Work Code)", placeholder="Np. POEM-003")
            
        new_text = st.text_area("Tekst utworu (Work Text)", placeholder="Wpisz lub wklej swój tekst tutaj...", height=300)
        new_notes = st.text_area("Notatki (Notes)", placeholder="Notatki o inspiracji, poprawkach, strukturze...", height=100)
        new_tags = st.text_input("Tagi / Słowa kluczowe (rozdzielone przecinkami)", placeholder="Np. wiatr, las, wieczór")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_cancel, col_save = st.columns([1, 1])
        
        with col_cancel:
            cancel_button = st.form_submit_button(label="Anuluj (Cancel)", use_container_width=True)
            if cancel_button:
                st.session_state.mode = 'view'
                st.rerun()
                
        with col_save:
            save_button = st.form_submit_button(label="Zapisz i wyświetl (Save & Load)", use_container_width=True)
            if save_button:
                if not new_orig_title.strip():
                    st.error("Tytuł roboczy jest wymagany!")
                else:
                    new_id = insert_work(
                        new_orig_title.strip(),
                        new_final_title.strip() if new_final_title.strip() else None,
                        new_creation_date,
                        new_language.strip(),
                        new_genre.strip(),
                        new_status,
                        new_text,
                        new_notes,
                        new_tags,
                        new_code.strip()
                    )
                    st.session_state.selected_work_id = new_id
                    st.session_state.mode = 'view'
                    st.success("Dodano nowy utwór!")
                    st.rerun()
