"""
Logik för SWOT-analys och TOWS-matris.
"""

def calculate_priority_score(impact: int, urgency: int) -> float:
    """
    Beräkna prioritetspoäng baserat på påverkan och brådska.
    
    Använder en viktad formel där påverkan väger något tyngre.
    """
    return (impact * 0.6) + (urgency * 0.4)


def generate_tows_matrix(factors: dict) -> dict:
    """
    Generera TOWS-korsanalys baserat på SWOT-faktorer.
    
    Returnerar kombinationer för:
    - SO: Styrkor + Möjligheter
    - WO: Svagheter + Möjligheter  
    - ST: Styrkor + Hot
    - WT: Svagheter + Hot
    """
    tows = {
        "SO": [],
        "WO": [],
        "ST": [],
        "WT": []
    }
    
    strengths = factors.get("strengths", [])
    weaknesses = factors.get("weaknesses", [])
    opportunities = factors.get("opportunities", [])
    threats = factors.get("threats", [])
    
    # SO: Hur kan styrkor utnyttja möjligheter?
    for s in strengths[:3]:  # Begränsa till topp 3
        for o in opportunities[:3]:
            tows["SO"].append(
                f"Använd '{s['description'][:30]}...' för att gripa '{o['description'][:30]}...'"
            )
    
    # WO: Hur kan möjligheter kompensera svagheter?
    for w in weaknesses[:3]:
        for o in opportunities[:3]:
            tows["WO"].append(
                f"Åtgärda '{w['description'][:30]}...' genom '{o['description'][:30]}...'"
            )
    
    # ST: Hur kan styrkor bemöta hot?
    for s in strengths[:3]:
        for t in threats[:3]:
            tows["ST"].append(
                f"Använd '{s['description'][:30]}...' för att hantera '{t['description'][:30]}...'"
            )
    
    # WT: Hur minimerar vi svagheter mot hot?
    for w in weaknesses[:3]:
        for t in threats[:3]:
            tows["WT"].append(
                f"Minska risken från '{t['description'][:30]}...' genom att åtgärda '{w['description'][:30]}...'"
            )
    
    return tows


def get_top_priorities(factors: dict, n: int = 5) -> list:
    """
    Hämta de n högst prioriterade faktorerna oavsett kategori.
    """
    all_factors = []
    
    category_labels = {
        "strengths": "Styrka",
        "weaknesses": "Svaghet",
        "opportunities": "Möjlighet",
        "threats": "Hot"
    }
    
    for category, factor_list in factors.items():
        for factor in factor_list:
            all_factors.append({
                **factor,
                "category_label": category_labels[category]
            })
    
    sorted_factors = sorted(
        all_factors,
        key=lambda x: x["priority_score"],
        reverse=True
    )
    
    return sorted_factors[:n]


def analyze_balance(factors: dict) -> dict:
    """
    Analysera balansen mellan interna och externa faktorer.
    """
    internal_positive = len(factors.get("strengths", []))
    internal_negative = len(factors.get("weaknesses", []))
    external_positive = len(factors.get("opportunities", []))
    external_negative = len(factors.get("threats", []))
    
    return {
        "internal_balance": internal_positive - internal_negative,
        "external_balance": external_positive - external_negative,
        "overall_balance": (internal_positive + external_positive) - (internal_negative + external_negative),
        "summary": {
            "strengths": internal_positive,
            "weaknesses": internal_negative,
            "opportunities": external_positive,
            "threats": external_negative
        }
    }
