def format_currency(amount):
    return f"₹{amount:,.0f}"

def format_percent(value):
    arrow = "▲" if value >= 0 else "▼"
    color = "green" if value >= 0 else "red"
    return arrow, color, abs(value)

def get_signal_strength(score):
    if score >= 5:
        return "HIGH", "#f85149"
    elif score >= 3:
        return "MEDIUM", "#d29922"
    else:
        return "LOW", "#3fb950"