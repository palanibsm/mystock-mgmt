def trend_arrow(trend: str) -> str:
    arrows = {
        "UP": "▲ Up",
        "DOWN": "▼ Down",
        "SIDEWAYS": "▶ Sideways",
    }
    return arrows.get(trend, "— N/A")


def trend_color(trend: str) -> str:
    colors = {
        "UP": "green",
        "DOWN": "red",
        "SIDEWAYS": "orange",
    }
    return colors.get(trend, "gray")
