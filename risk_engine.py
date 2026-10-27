from dataclasses import dataclass


@dataclass
class RiskResult:
    level: str
    score: int
    message: str
    recommendations: list


def assess_disaster_risk(
    incident_type: str,
    rainfall_mm: float = 0,
    wind_speed_kmh: float = 0,
    water_level_rising: bool = False,
    people_at_risk: int = 0
) -> RiskResult:
    """
    Prototype rule-based risk assessment.
    This is NOT an official disaster prediction model.
    """

    score = 0
    incident = incident_type.strip().lower()
    recommendations = []

    # Incident category contributes to a preliminary score.
    incident_weights = {
        "flood": 25,
        "cyclone": 25,
        "earthquake": 30,
        "fire": 25,
        "landslide": 25,
        "accident": 20,
        "other": 10
    }

    score += incident_weights.get(incident, 10)

    # Example rainfall indicators for prototype testing only.
    if rainfall_mm >= 100:
        score += 30
        recommendations.append(
            "Heavy rainfall reported: check official weather alerts."
        )
    elif rainfall_mm >= 50:
        score += 20
        recommendations.append(
            "Monitor rainfall and local drainage conditions."
        )
    elif rainfall_mm >= 20:
        score += 10

    # Wind-speed indicators for prototype testing only.
    if wind_speed_kmh >= 90:
        score += 30
        recommendations.append(
            "High wind speed: follow official weather warnings."
        )
    elif wind_speed_kmh >= 60:
        score += 20
        recommendations.append(
            "Secure loose outdoor objects and monitor official alerts."
        )
    elif wind_speed_kmh >= 30:
        score += 10

    if water_level_rising:
        score += 20
        recommendations.append(
            "Rising water level: avoid flooded roads and move away from danger."
        )

    if people_at_risk >= 100:
        score += 20
        recommendations.append(
            "Many people may be affected: notify emergency response teams."
        )
    elif people_at_risk >= 20:
        score += 10
        recommendations.append(
            "Check the safety of nearby residents."
        )

    # Keep the score within 0–100.
    score = min(score, 100)

    # Prototype categories, not validated safety thresholds.
    if score >= 75:
        level = "CRITICAL"
        message = "Urgent assessment by qualified emergency personnel is needed."
    elif score >= 50:
        level = "HIGH"
        message = "Prompt assessment and preparedness measures are recommended."
    elif score >= 30:
        level = "MODERATE"
        message = "Monitor the situation and check official advisories."
    else:
        level = "LOW"
        message = "Continue monitoring and follow local official guidance."

    if not recommendations:
        recommendations.append(
            "Monitor official local disaster and weather advisories."
        )

    return RiskResult(
        level=level,
        score=score,
        message=message,
        recommendations=recommendations
    )


if __name__ == "__main__":
    result = assess_disaster_risk(
        incident_type="Flood",
        rainfall_mm=120,
        wind_speed_kmh=35,
        water_level_rising=True,
        people_at_risk=50
    )

    print("DisasterShield AI - Risk Assessment")
    print("-" * 35)
    print("Risk Level:", result.level)
    print("Prototype Score:", result.score, "/ 100")
    print("Assessment:", result.message)
    print("Recommendations:")

    for item in result.recommendations:
        print("-", item)