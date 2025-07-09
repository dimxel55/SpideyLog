import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

img_path = "spideylog.jpg"  # path to your local image
img_base64 = get_base64_of_bin_file(img_path)

st.markdown(
    f"""
    <style>
    /* Φόντο με εικόνα fullscreen */
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Διαφάνεια και padding στο κυρίως περιεχόμενο */
    .css-18e3th9 {{
        background-color: rgba(255, 248, 220, 0.85);  /* φωτεινό, ζεστό κίτρινο */
        padding: 25px 40px 40px 40px;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(255, 223, 186, 0.7);
    }}

    /* Τίτλοι */
    .css-1v0mbdj h1, .css-1v0mbdj h2, .css-1v0mbdj h3 {{
        color: #ff6f61;  /* ζεστό κοραλί */
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }}

    /* Κουμπιά */
    button[kind="primary"] {{
        background-color: #ff6f61 !important;
        color: white !important;
        font-weight: bold;
    }}

    /* Slider mood */
    .stSlider > div > div {{
        color: #ff8a65 !important;
        font-weight: bold;
    }}
    
     .stMarkdown, .stTextInput, .stTextArea, .stSelectbox, .stDateInput {{
        border: 1px solid rgba(255, 105, 97, 0.3);  /* απαλή ροζ γραμμή */
        border-radius: 12px;
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.3);  /* πολύ απαλή λευκή βάση */
        box-shadow: 0 0 10px rgba(255, 182, 193, 0.2);  /* διακριτική ροζ σκιά */
    }}
    </style>
    """,
    unsafe_allow_html=True
)


SUPABASE_PROJECT_ID = "ugcfrznzgfghywncmtok"
SUPABASE_URL = "https://ugcfrznzgfghywncmtok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVnY2Zyem56Z2ZnaHl3bmNtdG9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyMTc3MTgsImV4cCI6MjA2Njc5MzcxOH0.7xkABOFGdLFLuNoAFNHX1cLCvdHXntcTEvnHvXhtL0U"
supabase: Client  = create_client(SUPABASE_URL, SUPABASE_KEY) #variable called supabase, and it will be a Client object (from Supabase).

def login():
    st.title(" Συνδεθείτε στο ημερολόγιο ")

    username = st.text_input("Όνομα χρήστη")
    password = st.text_input("Κωδικός")

    if st.button("Σύνδεση"):
        response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
        if response.data:
            st.session_state["user"] = username
            st.success(f"καλωσήρθες {st.session_state['user']}!")
        else:
            st.error("Σφάλμα σύνδεσης. Ξαναπροσπαθήστε")

#------------ Σημείο που θα βάζει δεδομένα -------------

def spideylog():
    st.header("Σημερινή καταγραφή :) ")

    #----επιλογή ημερομηνίας----
    date_of_log = st.date_input("Ποια μέρα καταχωρούμε;")
    date_of_log_string = date_of_log.strftime("%Y-%m-%d")


    spideyUsername = st.session_state["user"]

       # 2. Get user_id
    findUser = supabase.table("users").select("id").eq("username", spideyUsername).execute()
    user_id = findUser.data[0]["id"] if findUser.data else None


    existing = supabase.table("logs").select("*").eq("user_name", spideyUsername).eq("date", date_of_log_string).execute()


    if existing.data:
        existing_log = existing.data[0]

        #---Προβολή Logs παλιών ημερών
        st.markdown("Εκείνη την ημέρα...")
        st.write(f"**Καταχώρηση:** {existing_log['content']}")
        if existing_log.get("song"):
            st.write(f"**Τραγούδι**: {existing_log['song']}")
        else: 
            st.write("Δεν είχες καταχωρήσει κάποιο τραγούδι")
    else:
        st.write(f"Δεν έχετε κάνει καταχώρηση για την ημερομηνία {date_of_log_string}")
        st.write("Καταχωρήστε τώρα...")
    content = st.text_area("Τι έκανα σήμερα")
    song = st.text_input("Τραγούδι της ημέρας")
    mood = st.slider("Πώς ήταν η διάθεσή σου;", min_value=0, max_value=10, value=existing_log.get("mood") if existing.data else 5)

    #----υποβολή----

    if st.button("Υποβολή"):
        if not content:
            st.warning("Δεν έγραψες κάποια κατραχώρηση για την ημέρα αυτήν")
            return
        

        with st.spinner("Αποθήκευση..."):
          data = { 
              "user_name": spideyUsername,
              "date": date_of_log_string,
              "content": content,
              "song": song if song else None,
              "user_id": user_id,
              "mood": mood
            }

        try:
                if existing.data:
                    # Update
                    log_id = existing_log["id"]
                    response = supabase.table("logs").update(data).eq("id", log_id).execute()
                    st.success("🔄 Η καταχώρηση ενημερώθηκε!")
                else:
                    # Insert
                    response = supabase.table("logs").insert(data).execute()
                    st.success("✅ Επιτυχής υποβολή!")

                    st.write("📦 Δεδομένα που στάλθηκαν:", data)

        except Exception as e:
            st.error(f"❌ Database error: {e}")

if "user" not in st.session_state:
    login()
else:
    spideylog()

        




