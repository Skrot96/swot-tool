import streamlit as st
from datetime import datetime
from swot_logic import calculate_priority_score, generate_tows_matrix
from ai_suggestions import generate_action_suggestions
from data_store import save_analysis, load_analysis, list_analyses

# Sidkonfiguration
st.set_page_config(
    page_title="SWOT-verktyg",
    page_icon="📊",
    layout="wide"
)

# Initiera session state
if "factors" not in st.session_state:
    st.session_state.factors = {
        "strengths": [],
        "weaknesses": [],
        "opportunities": [],
        "threats": []
    }

if "current_step" not in st.session_state:
    st.session_state.current_step = 1

if "actions" not in st.session_state:
    st.session_state.actions = []


def add_factor(category: str, description: str, impact: int, urgency: int):
    """Lägg till en faktor i angiven kategori."""
    factor = {
        "id": f"{category}_{len(st.session_state.factors[category])}",
        "description": description,
        "impact": impact,
        "urgency": urgency,
        "priority_score": calculate_priority_score(impact, urgency),
        "created_at": datetime.now().isoformat()
    }
    st.session_state.factors[category].append(factor)


def remove_factor(category: str, factor_id: str):
    """Ta bort en faktor."""
    st.session_state.factors[category] = [
        f for f in st.session_state.factors[category] 
        if f["id"] != factor_id
    ]


# Sidopanel
with st.sidebar:
    st.header("📁 Sparade analyser")
    
    # Ladda befintlig analys
    saved = list_analyses()
    if saved:
        selected = st.selectbox("Välj analys", ["-- Ny analys --"] + saved)
        if selected != "-- Ny analys --":
            if st.button("Ladda"):
                loaded = load_analysis(selected)
                st.session_state.factors = loaded["factors"]
                st.session_state.actions = loaded.get("actions", [])
                st.success(f"Laddade: {selected}")
    
    st.divider()
    
    # Spara nuvarande analys
    analysis_name = st.text_input("Namn på analys")
    if st.button("Spara analys", disabled=not analysis_name):
        save_analysis(analysis_name, {
            "factors": st.session_state.factors,
            "actions": st.session_state.actions
        })
        st.success("Analys sparad!")
    
    st.divider()
    
    # Rensa allt
    if st.button("🗑️ Rensa allt", type="secondary"):
        st.session_state.factors = {
            "strengths": [], "weaknesses": [], 
            "opportunities": [], "threats": []
        }
        st.session_state.actions = []
        st.rerun()


# Huvudinnehåll
st.title("📊 SWOT-analysverktyg")

# Stegnavigering
step1, step2, step3 = st.tabs([
    "1️⃣ Identifiera faktorer",
    "2️⃣ Analysera",
    "3️⃣ Åtgärder"
])


# ============ STEG 1: IDENTIFIERA FAKTORER ============
with step1:
    st.header("Identifiera faktorer")
    st.write("Lägg till faktorer i varje kategori. Bedöm påverkan och brådska.")
    
    categories = {
        "strengths": {
            "title": "💪 Styrkor",
            "color": "green",
            "help_questions": [
                "Vad gör ni bättre än konkurrenterna?",
                "Vilka unika resurser eller kompetenser har ni?",
                "Vad uppskattar kunderna mest hos er?"
            ]
        },
        "weaknesses": {
            "title": "⚠️ Svagheter",
            "color": "orange",
            "help_questions": [
                "Var tappar ni kunder?",
                "Vilka kompetenser saknas?",
                "Vad klagar kunder på?"
            ]
        },
        "opportunities": {
            "title": "🚀 Möjligheter",
            "color": "blue",
            "help_questions": [
                "Vilka marknadstrender gynnar er?",
                "Finns nya kundsegment att nå?",
                "Vilken ny teknik kan ni dra nytta av?"
            ]
        },
        "threats": {
            "title": "🔴 Hot",
            "color": "red",
            "help_questions": [
                "Vilka konkurrenter oroar er?",
                "Finns regulatoriska förändringar på gång?",
                "Vilka ekonomiska risker ser ni?"
            ]
        }
    }
    
    # Visa alla kategorier i två kolumner
    col1, col2 = st.columns(2)
    
    for idx, (category, config) in enumerate(categories.items()):
        with col1 if idx < 2 else col2:
            st.subheader(config["title"])
            
            # Hjälpfrågor
            with st.expander("💡 Hjälpfrågor"):
                for q in config["help_questions"]:
                    st.write(f"• {q}")
            
            # Formulär för ny faktor
            with st.form(key=f"form_{category}"):
                description = st.text_area(
                    "Beskrivning",
                    key=f"desc_{category}",
                    height=80,
                    placeholder="Beskriv faktorn..."
                )
                
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    impact = st.slider(
                        "Påverkan",
                        1, 5, 3,
                        key=f"impact_{category}",
                        help="Hur stor effekt har denna faktor?"
                    )
                with subcol2:
                    urgency = st.slider(
                        "Brådska",
                        1, 5, 3,
                        key=f"urgency_{category}",
                        help="Hur snart behöver detta hanteras?"
                    )
                
                if st.form_submit_button("➕ Lägg till"):
                    if description.strip():
                        add_factor(category, description.strip(), impact, urgency)
                        st.rerun()
                    else:
                        st.warning("Ange en beskrivning")
            
            # Lista befintliga faktorer
            for factor in st.session_state.factors[category]:
                with st.container():
                    fcol1, fcol2 = st.columns([4, 1])
                    with fcol1:
                        score = factor["priority_score"]
                        st.write(f"**{factor['description']}**")
                        st.caption(
                            f"Påverkan: {factor['impact']} | "
                            f"Brådska: {factor['urgency']} | "
                            f"Prioritet: {score:.1f}"
                        )
                    with fcol2:
                        if st.button("🗑️", key=f"del_{factor['id']}"):
                            remove_factor(category, factor["id"])
                            st.rerun()
                    st.divider()


# ============ STEG 2: ANALYSERA ============
with step2:
    st.header("Analys")
    
    # Kontrollera att det finns faktorer
    total_factors = sum(len(f) for f in st.session_state.factors.values())
    
    if total_factors == 0:
        st.info("👆 Lägg till faktorer i steg 1 först.")
    else:
        # SWOT-matris
        st.subheader("SWOT-matris")
        
        matrix_col1, matrix_col2 = st.columns(2)
        
        with matrix_col1:
            # Styrkor
            st.markdown("### 💪 Styrkor")
            for f in sorted(
                st.session_state.factors["strengths"],
                key=lambda x: x["priority_score"],
                reverse=True
            ):
                st.success(f"**{f['description']}** (Prioritet: {f['priority_score']:.1f})")
            
            # Svagheter
            st.markdown("### ⚠️ Svagheter")
            for f in sorted(
                st.session_state.factors["weaknesses"],
                key=lambda x: x["priority_score"],
                reverse=True
            ):
                st.warning(f"**{f['description']}** (Prioritet: {f['priority_score']:.1f})")
        
        with matrix_col2:
            # Möjligheter
            st.markdown("### 🚀 Möjligheter")
            for f in sorted(
                st.session_state.factors["opportunities"],
                key=lambda x: x["priority_score"],
                reverse=True
            ):
                st.info(f"**{f['description']}** (Prioritet: {f['priority_score']:.1f})")
            
            # Hot
            st.markdown("### 🔴 Hot")
            for f in sorted(
                st.session_state.factors["threats"],
                key=lambda x: x["priority_score"],
                reverse=True
            ):
                st.error(f"**{f['description']}** (Prioritet: {f['priority_score']:.1f})")
        
        st.divider()
        
        # TOWS-analys
        st.subheader("TOWS-korsanalys")
        st.write("Kombinera interna och externa faktorer för strategiska insikter.")
        
        tows = generate_tows_matrix(st.session_state.factors)
        
        tows_col1, tows_col2 = st.columns(2)
        
        with tows_col1:
            st.markdown("#### SO-strategier")
            st.caption("Använd styrkor för att gripa möjligheter")
            for combo in tows["SO"]:
                st.write(f"• {combo}")
            
            st.markdown("#### WO-strategier")
            st.caption("Övervinn svagheter genom möjligheter")
            for combo in tows["WO"]:
                st.write(f"• {combo}")
        
        with tows_col2:
            st.markdown("#### ST-strategier")
            st.caption("Använd styrkor för att bemöta hot")
            for combo in tows["ST"]:
                st.write(f"• {combo}")
            
            st.markdown("#### WT-strategier")
            st.caption("Minimera svagheter och undvik hot")
            for combo in tows["WT"]:
                st.write(f"• {combo}")
        
        st.divider()
        
        # Prioriteringsdiagram
        st.subheader("Prioriteringsöversikt")
        
        import plotly.express as px
        import pandas as pd
        
        # Samla alla faktorer för visualisering
        all_factors = []
        category_names = {
            "strengths": "Styrkor",
            "weaknesses": "Svagheter",
            "opportunities": "Möjligheter",
            "threats": "Hot"
        }
        
        for category, factors in st.session_state.factors.items():
            for f in factors:
                all_factors.append({
                    "Kategori": category_names[category],
                    "Beskrivning": f["description"][:30] + "..." if len(f["description"]) > 30 else f["description"],
                    "Påverkan": f["impact"],
                    "Brådska": f["urgency"],
                    "Prioritet": f["priority_score"]
                })
        
        if all_factors:
            df = pd.DataFrame(all_factors)
            
            fig = px.scatter(
                df,
                x="Påverkan",
                y="Brådska",
                color="Kategori",
                size="Prioritet",
                hover_data=["Beskrivning"],
                title="Faktorer efter påverkan och brådska",
                color_discrete_map={
                    "Styrkor": "green",
                    "Svagheter": "orange",
                    "Möjligheter": "blue",
                    "Hot": "red"
                }
            )
            
            fig.update_layout(
                xaxis=dict(range=[0.5, 5.5]),
                yaxis=dict(range=[0.5, 5.5])
            )
            
            st.plotly_chart(fig, use_container_width=True)


# ============ STEG 3: ÅTGÄRDER ============
with step3:
    st.header("Åtgärder")
    
    total_factors = sum(len(f) for f in st.session_state.factors.values())
    
    if total_factors == 0:
        st.info("👆 Lägg till faktorer i steg 1 först.")
    else:
        # AI-genererade förslag
        st.subheader("🤖 AI-genererade förslag")
        
        api_key = st.text_input(
            "Anthropic API-nyckel",
            type="password",
            help="Krävs för att generera AI-förslag. Hämta från console.anthropic.com"
        )
        
        if st.button("Generera förslag", disabled=not api_key):
            with st.spinner("Analyserar och genererar förslag..."):
                try:
                    suggestions = generate_action_suggestions(
                        st.session_state.factors,
                        api_key
                    )
                    st.session_state.ai_suggestions = suggestions
                except Exception as e:
                    st.error(f"Kunde inte generera förslag: {e}")
        
        if "ai_suggestions" in st.session_state:
            st.markdown(st.session_state.ai_suggestions)
            
            if st.button("Rensa AI-förslag"):
                del st.session_state.ai_suggestions
                st.rerun()
        
        st.divider()
        
        # Manuella åtgärder
        st.subheader("📝 Handlingsplan")
        
        with st.form("add_action"):
            action_desc = st.text_area("Åtgärd", placeholder="Beskriv åtgärden...")
            
            action_col1, action_col2, action_col
        # Manuella åtgärder
        st.subheader("📝 Handlingsplan")
        
        with st.form("add_action"):
            action_desc = st.text_area("Åtgärd", placeholder="Beskriv åtgärden...")
            
            action_col1, action_col2, action_col3 = st.columns(3)
            
            with action_col1:
                owner = st.text_input("Ansvarig")
            
            with action_col2:
                deadline = st.date_input("Deadline")
            
            with action_col3:
                status = st.selectbox(
                    "Status",
                    ["Ej påbörjad", "Pågående", "Klar"]
                )
            
            # Koppla till faktorer
            all_factor_options = []
            for category, factors in st.session_state.factors.items():
                for f in factors:
                    all_factor_options.append(f"{f['description'][:40]}...")
            
            linked_factors = st.multiselect(
                "Kopplade faktorer",
                all_factor_options,
                help="Vilka SWOT-faktorer adresserar denna åtgärd?"
            )
            
            if st.form_submit_button("➕ Lägg till åtgärd"):
                if action_desc.strip():
                    action = {
                        "id": f"action_{len(st.session_state.actions)}",
                        "description": action_desc.strip(),
                        "owner": owner,
                        "deadline": deadline.isoformat(),
                        "status": status,
                        "linked_factors": linked_factors,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.actions.append(action)
                    st.rerun()
                else:
                    st.warning("Ange en beskrivning")
        
        # Lista åtgärder
        if st.session_state.actions:
            st.divider()
            st.subheader("Registrerade åtgärder")
            
            for action in st.session_state.actions:
                with st.container():
                    status_icons = {
                        "Ej påbörjad": "⬜",
                        "Pågående": "🔄",
                        "Klar": "✅"
                    }
                    
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 0.5])
                    
                    with col1:
                        st.write(f"{status_icons.get(action['status'], '⬜')} **{action['description']}**")
                        if action["linked_factors"]:
                            st.caption(f"Kopplad till: {', '.join(action['linked_factors'])}")
                    
                    with col2:
                        st.caption(f"👤 {action['owner'] or 'Ej tilldelad'}")
                    
                    with col3:
                        st.caption(f"📅 {action['deadline']}")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_action_{action['id']}"):
                            st.session_state.actions = [
                                a for a in st.session_state.actions 
                                if a["id"] != action["id"]
                            ]
                            st.rerun()
                    
                    st.divider()
            
            # Exportera handlingsplan
            st.subheader("Exportera")
            
            import pandas as pd
            
            export_data = []
            for action in st.session_state.actions:
                export_data.append({
                    "Åtgärd": action["description"],
                    "Ansvarig": action["owner"],
                    "Deadline": action["deadline"],
                    "Status": action["status"],
                    "Kopplade faktorer": ", ".join(action["linked_factors"])
                })
            
            df_export = pd.DataFrame(export_data)
            
            csv = df_export.to_csv(index=False).encode("utf-8")
            
            st.download_button(
                label="📥 Ladda ner som CSV",
                data=csv,
                file_name="handlingsplan.csv",
                mime="text/csv"
            )
        else:
            st.info("Inga åtgärder registrerade ännu.")
