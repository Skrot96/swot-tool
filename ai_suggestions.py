"""
Integration med Claude API för att generera åtgärdsförslag.
"""

import anthropic


def generate_action_suggestions(factors: dict, api_key: str) -> str:
    """
    Använd Claude för att generera strategiska åtgärdsförslag
    baserat på SWOT-faktorer.
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    # Formatera faktorer för prompten
    strengths = [f["description"] for f in factors.get("strengths", [])]
    weaknesses = [f["description"] for f in factors.get("weaknesses", [])]
    opportunities = [f["description"] for f in factors.get("opportunities", [])]
    threats = [f["description"] for f in factors.get("threats", [])]
    
    prompt = f"""Du är en strategisk rådgivare. Baserat på följande SWOT-analys, 
föreslå 5-7 konkreta och genomförbara åtgärder.

## SWOT-ANALYS

### Styrkor (interna fördelar)
{chr(10).join(f"- {s}" for s in strengths) if strengths else "- Inga angivna"}

### Svagheter (interna nackdelar)
{chr(10).join(f"- {w}" for w in weaknesses) if weaknesses else "- Inga angivna"}

### Möjligheter (externa fördelar)
{chr(10).join(f"- {o}" for o in opportunities) if opportunities else "- Inga angivna"}

### Hot (externa risker)
{chr(10).join(f"- {t}" for t in threats) if threats else "- Inga angivna"}

## INSTRUKTIONER

Föreslå åtgärder som:
1. **SO-strategier**: Utnyttjar styrkor för att gripa möjligheter
2. **WO-strategier**: Använder möjligheter för att övervinna svagheter
3. **ST-strategier**: Använder styrkor för att neutralisera hot
4. **WT-strategier**: Minimerar svagheter för att undvika hot

För varje åtgärd, ange:
- Konkret beskrivning av åtgärden
- Vilken strategityp (SO/WO/ST/WT)
- Förväntad effekt
- Ungefärlig tidshorisont (kort/medel/lång sikt)

Svara på svenska. Var konkret och handlingsorienterad."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text


def generate_risk_assessment(factors: dict, api_key: str) -> str:
    """
    Generera en riskbedömning baserat på hot och svagheter.
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    weaknesses = [f["description"] for f in factors.get("weaknesses", [])]
    threats = [f["description"] for f in factors.get("threats", [])]
    
    prompt = f"""Analysera följande svagheter och hot. Identifiera de mest kritiska 
riskerna och föreslå hur de kan hanteras.

### Svagheter
{chr(10).join(f"- {w}" for w in weaknesses) if weaknesses else "- Inga angivna"}

### Hot
{chr(10).join(f"- {t}" for t in threats) if threats else "- Inga angivna"}

Rangordna riskerna efter allvarlighetsgrad och sannolikhet. 
Svara på svenska."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text
