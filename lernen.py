import streamlit as st
import random
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Somatoforme Störungen Lernapp",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für ADHS-freundliches Design
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .flashcard {
        background: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        text-align: center;
        min-height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .flashcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .flashcard h2 {
        color: #667eea;
        margin-bottom: 20px;
    }
    
    .flashcard p {
        font-size: 1.2em;
        line-height: 1.6;
        color: #4a5568;
    }
    
    .quiz-option {
        background: #f7fafc;
        padding: 15px 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .quiz-option:hover {
        background: #e2e8f0;
        transform: translateX(5px);
    }
    
    .correct {
        background: #c6f6d5 !important;
        border-color: #48bb78 !important;
    }
    
    .incorrect {
        background: #fed7d7 !important;
        border-color: #f56565 !important;
    }
    
    .achievement {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
        border-left: 4px solid #667eea;
    }
    
    .memory-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        min-height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .memory-card:hover {
        transform: scale(1.05);
    }
    
    .memory-card.flipped {
        background: white;
        color: #4a5568;
        border: 2px solid #e2e8f0;
    }
    
    .memory-card.matched {
        background: #e2e8f0;
        color: #718096;
        cursor: default;
        opacity: 0.7;
    }
    
    .stProgress > div > div {
        background-color: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    }
    
    .stat-card h3 {
        color: #667eea;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_card = 0
    st.session_state.card_flipped = False
    st.session_state.quiz_score = 0
    st.session_state.quiz_current = 0
    st.session_state.quiz_answered = False
    st.session_state.memory_cards = []
    st.session_state.memory_flipped = []
    st.session_state.memory_matched = []
    st.session_state.memory_moves = 0
    st.session_state.achievements = []
    st.session_state.progress = 0
    st.session_state.start_time = datetime.now()
    st.session_state.cards_studied = set()
    st.session_state.quiz_completed = False
    st.session_state.memory_completed = False

# Lerninhalt Datenbank
flashcards = [
    {
        "question": "Somatisierungsstörung",
        "answer": "Multiple und häufig wechselnde körperliche Symptome (mindestens 6 Symptome) über mehr als 2 Jahre ohne ausreichende somatische Erklärung"
    },
    {
        "question": "Hypochondrische Störung",
        "answer": "Anhaltende Überzeugung vom Vorhandensein einer oder mehrerer ernsthafter körperlicher Erkrankungen (Dauer: 6 Monate) oder anhaltende Beschäftigung mit einer vermuteten Entstellung"
    },
    {
        "question": "Somatoforme autonome Funktionsstörung",
        "answer": "Symptome eines vegetativ innervierten Organs (kardiovaskulär, respiratorisch, gastrointestinal) + vegetative Dysregulation + intensive Beschäftigung mit vermuteter Erkrankung"
    },
    {
        "question": "Anhaltende somatoforme Schmerzstörung",
        "answer": "Anhaltender, schwerer und quälender Schmerz ohne ausreichende Erklärung durch physiologische Prozesse, tritt in Verbindung mit emotionalen/psychosozialen Belastungen auf"
    },
    {
        "question": "ICD-11: Körperliche Belastungsstörung",
        "answer": "Körperliche Symptome + übermäßige Aufmerksamkeit + wiederholte Kontakte mit Gesundheitsdienstleistern + Persistenz über mehrere Monate"
    },
    {
        "question": "DSM-5: Somatic Symptom Disorder (SSD)",
        "answer": "Belastende somatische Symptome + exzessive Gedanken/Gefühle/Verhalten bezüglich der Symptome + Chronizität >6 Monate"
    },
    {
        "question": "Illness Anxiety Disorder (DSM-5)",
        "answer": "Sorge vor ernsthafter Erkrankung + keine/milde Symptome + starke Angst + exzessive gesundheitsbezogene Aktivitäten + 6 Monate"
    },
    {
        "question": "Conversion Disorder (DSM-5)",
        "answer": "Gestörte motorische oder sensorische Funktion ohne neurologischen Zusammenhang + deutliches Leiden und Einschränkungen"
    },
    {
        "question": "Wichtige Warnung (Cave!)",
        "answer": "Iatrogene Fixierung und Chronifizierung durch wiederholte Untersuchungen trotz negativer Befunde vermeiden!"
    },
    {
        "question": "7 Screening-Symptome",
        "answer": "Erbrechen, Unterleibsschmerzen, Übelkeit, Blähungen, Diarrhoe, Speisen-Unverträglichkeit, Schmerzen - 2+ Symptome zeigen hohe Wahrscheinlichkeit"
    }
]

quiz_questions = [
    {
        "question": "Wie lange müssen die Symptome bei einer Somatisierungsstörung mindestens bestehen?",
        "options": ["6 Monate", "1 Jahr", "2 Jahre", "3 Jahre"],
        "correct": 2,
        "explanation": "Bei der Somatisierungsstörung müssen die Symptome über mehr als 2 Jahre bestehen."
    },
    {
        "question": "Wie viele Symptome sind für eine Somatisierungsstörung mindestens erforderlich?",
        "options": ["3 Symptome", "4 Symptome", "5 Symptome", "6 Symptome"],
        "correct": 3,
        "explanation": "Für die Diagnose einer Somatisierungsstörung sind mindestens 6 Symptome erforderlich."
    },
    {
        "question": "Was ist KEIN Synonym für funktionelle Störungen?",
        "options": ["Psychovegetative Störung", "Vegetative Dystonie", "Bipolare Störung", "Organneurose"],
        "correct": 2,
        "explanation": "Bipolare Störung ist eine affektive Störung und kein Synonym für funktionelle Störungen."
    },
    {
        "question": "Welche Dauer gilt für die Hypochondrische Störung?",
        "options": ["3 Monate", "6 Monate", "12 Monate", "24 Monate"],
        "correct": 1,
        "explanation": "Die Hypochondrische Störung muss mindestens 6 Monate bestehen."
    },
    {
        "question": "Was charakterisiert die Conversion Disorder?",
        "options": ["Nur Schmerzen", "Gestörte motorische/sensorische Funktion", "Nur Angst", "Nur vegetative Symptome"],
        "correct": 1,
        "explanation": "Die Conversion Disorder ist durch gestörte motorische oder sensorische Funktionen charakterisiert."
    },
    {
        "question": "Welches Organsystem ist NICHT typisch für die somatoforme autonome Funktionsstörung?",
        "options": ["Kardiovaskulär", "Respiratorisch", "Gastrointestinal", "Muskuloskeletal"],
        "correct": 3,
        "explanation": "Das muskuloskeletale System ist nicht typisch für die somatoforme autonome Funktionsstörung."
    },
    {
        "question": "Was ist die Mindestanzahl von Screening-Symptomen für eine hohe Wahrscheinlichkeit?",
        "options": ["1 Symptom", "2 Symptome", "3 Symptome", "4 Symptome"],
        "correct": 1,
        "explanation": "2 oder mehr der 7 kursiven Screening-Symptome zeigen eine hohe Wahrscheinlichkeit an."
    },
    {
        "question": "Welche Störung wurde früher als hypochondrische Störung bezeichnet?",
        "options": ["Somatic Symptom Disorder", "Illness Anxiety Disorder", "Conversion Disorder", "Factitious Disorder"],
        "correct": 1,
        "explanation": "Die Illness Anxiety Disorder (DSM-5) entspricht der früheren hypochondrischen Störung."
    }
]

memory_pairs = [
    ("Somatisierung", ">2 Jahre, 6+ Symptome"),
    ("Hypochondrie", "6 Monate Krankheitsangst"),
    ("Autonome Störung", "Vegetative Symptome"),
    ("Schmerzstörung", "Quälender Schmerz"),
    ("ICD-11", "Körperliche Belastung"),
    ("DSM-5 SSD", "Exzessive Gedanken"),
    ("Conversion", "Motor./sensor. Störung"),
    ("Cave!", "Iatrogene Fixierung")
]

# Helper Functions
def add_achievement(title, description):
    achievement = {"title": title, "description": description, "time": datetime.now()}
    if title not in [a["title"] for a in st.session_state.achievements]:
        st.session_state.achievements.append(achievement)
        st.success(f"🏆 Achievement freigeschaltet: {title}")
        st.balloons()

def update_progress():
    # Calculate progress based on activities
    card_progress = len(st.session_state.cards_studied) / len(flashcards) * 30
    quiz_progress = (st.session_state.quiz_score / len(quiz_questions) * 35) if st.session_state.quiz_completed else 0
    memory_progress = 35 if st.session_state.memory_completed else 0
    
    st.session_state.progress = min(100, card_progress + quiz_progress + memory_progress)
    
    # Check for achievements
    if st.session_state.progress >= 25 and st.session_state.progress < 50:
        add_achievement("Erste Schritte", "25% Fortschritt erreicht!")
    elif st.session_state.progress >= 50 and st.session_state.progress < 75:
        add_achievement("Halbzeit", "50% Fortschritt erreicht!")
    elif st.session_state.progress >= 75 and st.session_state.progress < 100:
        add_achievement("Fast geschafft", "75% Fortschritt erreicht!")
    elif st.session_state.progress >= 100:
        add_achievement("Meister der Somatoformen Störungen", "100% abgeschlossen!")

# Sidebar
with st.sidebar:
    st.title("🧠 Somatoforme Störungen")
    st.markdown("### Lernapp für Medizinstudierende")
    
    # Progress
    st.markdown("---")
    st.markdown("### 📊 Dein Fortschritt")
    progress_bar = st.progress(st.session_state.progress / 100)
    st.write(f"{st.session_state.progress:.0f}% abgeschlossen")
    
    # Study time
    study_time = datetime.now() - st.session_state.start_time
    st.write(f"⏱️ Lernzeit: {study_time.seconds // 60} Minuten")
    
    # Achievements
    st.markdown("---")
    st.markdown("### 🏆 Achievements")
    if st.session_state.achievements:
        for achievement in st.session_state.achievements[-3:]:  # Show last 3
            st.markdown(f"**{achievement['title']}**")
            st.caption(achievement['description'])
    else:
        st.info("Noch keine Achievements freigeschaltet")
    
    # Navigation
    st.markdown("---")
    st.markdown("### 🎯 Lernmodus wählen")
    mode = st.radio(
        "Wähle deinen Lernmodus:",
        ["📇 Karteikarten", "🕸️ Mindmap", "❓ Quiz", "🎮 Memory-Spiel", "📈 Statistiken"],
        label_visibility="collapsed"
    )

# Main content
st.title("🧠 Somatoforme Störungen Lernapp")
st.markdown("*ADHS-freundlich gestaltet mit visuellen Elementen und Gamification*")

# Karteikarten Mode
if mode == "📇 Karteikarten":
    st.header("📇 Karteikarten")
    st.write("Klicke auf die Karte zum Umdrehen!")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("⬅️ Zurück", use_container_width=True):
            st.session_state.current_card = (st.session_state.current_card - 1) % len(flashcards)
            st.session_state.card_flipped = False
    
    with col2:
        current_card = flashcards[st.session_state.current_card]
        
        # Flip button
        if st.button("🔄 Karte umdrehen", use_container_width=True):
            st.session_state.card_flipped = not st.session_state.card_flipped
            st.session_state.cards_studied.add(st.session_state.current_card)
            update_progress()
        
        # Display card
        if not st.session_state.card_flipped:
            st.markdown(f"""
            <div class="flashcard">
                <div>
                    <h2>{current_card['question']}</h2>
                    <p style="color: #718096; margin-top: 30px;">Klicke zum Umdrehen</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="flashcard">
                <div>
                    <h3 style="color: #667eea;">{current_card['question']}</h3>
                    <p>{current_card['answer']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Weiter ➡️", use_container_width=True):
            st.session_state.current_card = (st.session_state.current_card + 1) % len(flashcards)
            st.session_state.card_flipped = False
            
            # Check if all cards viewed
            if len(st.session_state.cards_studied) == len(flashcards):
                add_achievement("Kartei-Meister", "Alle Karteikarten durchgearbeitet!")
    
    # Progress indicator
    st.markdown(f"**Karte {st.session_state.current_card + 1} von {len(flashcards)}**")
    
    # Quick navigation
    st.markdown("---")
    st.markdown("### 🎯 Schnellzugriff")
    quick_nav_cols = st.columns(5)
    for i in range(min(5, len(flashcards))):
        with quick_nav_cols[i]:
            if st.button(f"Karte {i+1}", key=f"quick_{i}"):
                st.session_state.current_card = i
                st.session_state.card_flipped = False

# Mindmap Mode
elif mode == "🕸️ Mindmap":
    st.header("🕸️ Interaktive Mindmap")
    st.write("Erkunde die Zusammenhänge zwischen den verschiedenen somatoformen Störungen!")
    
    # Create interactive mindmap with Plotly
    fig = go.Figure()
    
    # Central node
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers+text',
        marker=dict(size=80, color='#667eea'),
        text=['Somatoforme<br>Störungen'],
        textposition="middle center",
        textfont=dict(size=16, color='white'),
        hoverinfo='text',
        hovertext='Zentrale Kategorie aller somatoformen Störungen'
    ))
    
    # Sub-nodes
    nodes = [
        ("Somatisierungsstörung", ">2 Jahre, 6+ Symptome"),
        ("Hypochondrische Störung", "6 Monate Krankheitsangst"),
        ("Autonome Funktionsstörung", "Vegetative Symptome"),
        ("Schmerzstörung", "Quälender Schmerz"),
        ("ICD-11: Körperliche Belastung", "Übermäßige Aufmerksamkeit"),
        ("DSM-5: SSD", "Exzessive Gedanken"),
        ("Illness Anxiety", "Sorge vor Erkrankung"),
        ("Conversion Disorder", "Motor./sensor. Störung")
    ]
    
    import math
    for i, (title, desc) in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes)
        x = 3 * math.cos(angle)
        y = 3 * math.sin(angle)
        
        # Add connection line
        fig.add_trace(go.Scatter(
            x=[0, x], y=[0, y],
            mode='lines',
            line=dict(color='#e2e8f0', width=2),
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Add node
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=60, color='white', line=dict(color='#667eea', width=3)),
            text=[f"{title}<br><span style='font-size:10px'>{desc}</span>"],
            textposition="middle center",
            textfont=dict(size=12),
            hoverinfo='text',
            hovertext=f"{title}: {desc}",
            showlegend=False
        ))
    
    fig.update_layout(
        height=600,
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Info boxes
    col1, col2 = st.columns(2)
    with col1:
        st.info("💡 **Tipp**: Alle Störungen haben gemeinsam, dass körperliche Symptome ohne ausreichende somatische Erklärung auftreten.")
    with col2:
        st.warning("⚠️ **Cave**: Iatrogene Fixierung und Chronifizierung vermeiden!")

# Quiz Mode
elif mode == "❓ Quiz":
    st.header("❓ Interaktives Quiz")
    st.write("Teste dein Wissen über somatoforme Störungen!")
    
    if st.session_state.quiz_current < len(quiz_questions):
        current_q = quiz_questions[st.session_state.quiz_current]
        
        st.markdown(f"### Frage {st.session_state.quiz_current + 1} von {len(quiz_questions)}")
        st.markdown(f"**{current_q['question']}**")
        
        # Display options
        for i, option in enumerate(current_q['options']):
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                if st.button(f"{chr(65+i)}", key=f"opt_{i}", disabled=st.session_state.quiz_answered):
                    st.session_state.quiz_answered = True
                    if i == current_q['correct']:
                        st.success("✅ Richtig!")
                        st.session_state.quiz_score += 1
                        add_achievement("Quiz-Talent", "Erste richtige Antwort!")
                    else:
                        st.error(f"❌ Leider falsch. Richtig wäre: {current_q['options'][current_q['correct']]}")
                    st.info(f"💡 {current_q['explanation']}")
            with col2:
                st.write(option)
        
        if st.session_state.quiz_answered:
            if st.button("Nächste Frage ➡️", type="primary"):
                st.session_state.quiz_current += 1
                st.session_state.quiz_answered = False
                st.rerun()
    
    else:
        # Quiz completed
        st.session_state.quiz_completed = True
        update_progress()
        
        st.success(f"🎉 Quiz abgeschlossen!")
        st.markdown(f"### Dein Ergebnis: {st.session_state.quiz_score}/{len(quiz_questions)} Punkten")
        
        percentage = (st.session_state.quiz_score / len(quiz_questions)) * 100
        if percentage == 100:
            add_achievement("Perfektionist", "100% im Quiz erreicht!")
            st.balloons()
        elif percentage >= 80:
            add_achievement("Quiz-Experte", "Über 80% im Quiz erreicht!")
        
        # Results visualization
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = percentage,
            title = {'text': "Erfolgsquote"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "#fed7d7"},
                    {'range': [50, 80], 'color': "#fef3c7"},
                    {'range': [80, 100], 'color': "#c6f6d5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        if st.button("Quiz wiederholen 🔄"):
            st.session_state.quiz_current = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_answered = False
            st.session_state.quiz_completed = False
            st.rerun()

# Memory Game Mode
elif mode == "🎮 Memory-Spiel":
    st.header("🎮 Memory-Spiel")
    st.write("Finde die passenden Paare von Begriffen und ihren Definitionen!")
    
    # Initialize memory game
    if not st.session_state.memory_cards:
        cards = []
        for i, (term, definition) in enumerate(memory_pairs):
            cards.append({"id": i, "content": term, "type": "term"})
            cards.append({"id": i, "content": definition, "type": "definition"})
        random.shuffle(cards)
        st.session_state.memory_cards = cards
        st.session_state.memory_flipped = [False] * len(cards)
        st.session_state.memory_matched = [False] * len(cards)
    
    # Game stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Züge", st.session_state.memory_moves)
    with col2:
        matches = sum(st.session_state.memory_matched) // 2
        st.metric("Gefundene Paare", f"{matches}/{len(memory_pairs)}")
    with col3:
        if st.button("Neu starten 🔄"):
            st.session_state.memory_cards = []
            st.session_state.memory_flipped = []
            st.session_state.memory_matched = []
            st.session_state.memory_moves = 0
            st.session_state.memory_completed = False
            st.rerun()
    
    # Display cards in grid
    cols = st.columns(4)
    for i, card in enumerate(st.session_state.memory_cards):
        with cols[i % 4]:
            if st.session_state.memory_matched[i]:
                st.markdown(f"""
                <div class="memory-card matched">
                    {card['content']}
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.memory_flipped[i]:
                st.markdown(f"""
                <div class="memory-card flipped">
                    {card['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button("?", key=f"mem_{i}", 
                           disabled=st.session_state.memory_matched[i] or st.session_state.memory_flipped[i],
                           use_container_width=True):
                    
                    # Flip card
                    st.session_state.memory_flipped[i] = True
                    flipped_indices = [j for j, f in enumerate(st.session_state.memory_flipped) 
                                     if f and not st.session_state.memory_matched[j]]
                    
                    if len(flipped_indices) == 2:
                        st.session_state.memory_moves += 1
                        idx1, idx2 = flipped_indices
                        card1, card2 = st.session_state.memory_cards[idx1], st.session_state.memory_cards[idx2]
                        
                        # Check for match
                        if card1['id'] == card2['id'] and card1['type'] != card2['type']:
                            st.session_state.memory_matched[idx1] = True
                            st.session_state.memory_matched[idx2] = True
                            
                            # Check if game completed
                            if all(st.session_state.memory_matched):
                                st.session_state.memory_completed = True
                                update_progress()
                                add_achievement("Memory-Meister", f"Alle Paare in {st.session_state.memory_moves} Zügen gefunden!")
                                st.balloons()
                        else:
                            # No match - flip back after delay
                            time.sleep(1)
                            st.session_state.memory_flipped[idx1] = False
                            st.session_state.memory_flipped[idx2] = False
                    
                    st.rerun()

# Statistics Mode
elif mode == "📈 Statistiken":
    st.header("📈 Deine Lernstatistiken")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>📇</h3>
            <h2>{}/{}</h2>
            <p>Karten gelernt</p>
        </div>
        """.format(len(st.session_state.cards_studied), len(flashcards)), unsafe_allow_html=True)
    
    with col2:
        quiz_percentage = (st.session_state.quiz_score / len(quiz_questions) * 100) if st.session_state.quiz_completed else 0
        st.markdown(f"""
        <div class="stat-card">
            <h3>❓</h3>
            <h2>{quiz_percentage:.0f}%</h2>
            <p>Quiz-Erfolg</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        matches = sum(st.session_state.memory_matched) // 2 if st.session_state.memory_matched else 0
        st.markdown(f"""
        <div class="stat-card">
            <h3>🎮</h3>
            <h2>{matches}/{len(memory_pairs)}</h2>
            <p>Memory Paare</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h3>🏆</h3>
            <h2>{len(st.session_state.achievements)}</h2>
            <p>Achievements</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress over time chart
    st.markdown("---")
    st.subheader("📊 Lernfortschritt")
    
    # Create sample progress data
    progress_data = pd.DataFrame({
        'Bereich': ['Karteikarten', 'Quiz', 'Memory', 'Gesamt'],
        'Fortschritt': [
            len(st.session_state.cards_studied) / len(flashcards) * 100,
            quiz_percentage,
            (matches / len(memory_pairs) * 100) if len(memory_pairs) > 0 else 0,
            st.session_state.progress
        ]
    })
    
    fig = px.bar(progress_data, x='Bereich', y='Fortschritt', 
                 color='Fortschritt', color_continuous_scale='viridis',
                 title='Fortschritt nach Lernbereich')
    fig.update_layout(showlegend=False, yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    
    # Learning tips
    st.markdown("---")
    st.subheader("💡 Personalisierte Lerntipps")
    
    if len(st.session_state.cards_studied) < len(flashcards) / 2:
        st.info("📇 **Karteikarten**: Du hast erst wenige Karten durchgearbeitet. Versuche täglich 3-5 Karten zu lernen!")
    
    if st.session_state.quiz_completed and quiz_percentage < 70:
        st.warning("❓ **Quiz**: Wiederhole das Quiz, um dein Wissen zu festigen. Ziel: mindestens 70%!")
    
    if not st.session_state.memory_completed:
        st.info("🎮 **Memory**: Das Memory-Spiel hilft dir, Begriffe und Definitionen zu verknüpfen!")
    
    # Achievement overview
    st.markdown("---")
    st.subheader("🏆 Alle Achievements")
    
    if st.session_state.achievements:
        for achievement in st.session_state.achievements:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown("🏆")
            with col2:
                st.markdown(f"**{achievement['title']}**")
                st.caption(f"{achievement['description']} - {achievement['time'].strftime('%H:%M Uhr')}")
    else:
        st.info("Noch keine Achievements freigeschaltet. Beginne mit den Karteikarten!")
    
    # Study recommendations
    st.markdown("---")
    st.subheader("📚 Empfohlene Lernreihenfolge")
    
    recommendations = [
        "1️⃣ **Karteikarten**: Grundlegendes Verständnis aufbauen",
        "2️⃣ **Mindmap**: Zusammenhänge visualisieren",
        "3️⃣ **Quiz**: Wissen testen und vertiefen",
        "4️⃣ **Memory**: Begriffe und Definitionen festigen"
    ]
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Export option
    st.markdown("---")
    if st.button("📥 Lernfortschritt exportieren", type="primary"):
        summary = f"""
# Lernfortschritt Somatoforme Störungen
## Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}

### 📊 Statistiken
- Karteikarten gelernt: {len(st.session_state.cards_studied)}/{len(flashcards)}
- Quiz-Erfolg: {quiz_percentage:.0f}%
- Memory Paare gefunden: {matches}/{len(memory_pairs)}
- Gesamtfortschritt: {st.session_state.progress:.0f}%
- Lernzeit: {(datetime.now() - st.session_state.start_time).seconds // 60} Minuten

### 🏆 Achievements ({len(st.session_state.achievements)})
"""
        for achievement in st.session_state.achievements:
            summary += f"\n- {achievement['title']}: {achievement['description']}"
        
        st.download_button(
            label="Download als Textdatei",
            data=summary,
            file_name=f"lernfortschritt_somatoforme_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# Footer with tips
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #718096;'>
    <p>💡 <strong>ADHS-Tipp</strong>: Mache alle 25 Minuten eine 5-Minuten-Pause (Pomodoro-Technik)</p>
    <p>🎯 Setze dir kleine, erreichbare Ziele und feiere deine Erfolge!</p>
</div>
""", unsafe_allow_html=True)
