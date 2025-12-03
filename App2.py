import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Canada Income Calculator", layout="wide")

st.title("🗺️ Canada Income Distribution Calculator")
st.markdown("---")

# Canadian income parameters (20M working age population)
total_pop = 20_000_000
income_range = np.linspace(1, 300_000, 1000)

# Pure NumPy log-normal functions (no scipy needed)
mu, sigma = 10.45, 0.95
scale = np.exp(mu)

def lognorm_pdf(x, s, scale):
    return (1 / (x * s * np.sqrt(2 * np.pi))) * np.exp(-((np.log(x) - np.log(scale))**2) / (2 * s**2))

def lognorm_cdf(x, s, scale):
    z = (np.log(x) - np.log(scale)) / s
    return 0.5 * (1 + np.tanh(np.sqrt(2) * z / 2) + np.sqrt(2/np.pi) * np.exp(-z**2/2))

# Calculate distribution
pdf = lognorm_pdf(income_range, sigma, scale)
cdf = lognorm_cdf(income_range, sigma, scale)

# Sidebar
st.sidebar.header("📊 Income Range")
col1, col2 = st.sidebar.columns(2)
min_income = col1.slider("Min ($)", 0, 150000, 25000, 5000)
max_income = col2.slider("Max ($)", min_income, 300000, 100000, 5000)

# Results
prob = lognorm_cdf(max_income, sigma, scale) - lognorm_cdf(min_income, sigma, scale)
people = prob * total_pop
percent = prob * 100

# Main metrics
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.metric("Population in Range", f"{people:,.0f}", f"{percent:.1f}%")
with col2:
    st.metric("Range", f"${min_income:,}")
with col3:
    st.metric("", f"${max_income:,}")

st.markdown("---")

# Interactive chart
fig = make_subplots(rows=1, cols=2, subplot_titles=('📈 Population Density', '📊 Cumulative'))

# Density
density_scaled = pdf / np.max(pdf) * 30
fig.add_trace(go.Scatter(x=income_range, y=density_scaled, mode='lines',
                        name='Density', line=dict(color='#1f77b4', width=4)), row=1, col=1)

# Highlight range
fig.add_vrect(x0=min_income, x1=max_income, fillcolor="rgba(255,0,0,0.2)", 
              layer="below", line_width=0, row=1, col=1)
fig.add_vline(x=min_income, line_dash="dash", line_color="red", row=1, col=1)
fig.add_vline(x=max_income, line_dash="dash", line_color="red", row=1, col=1)

# Cumulative
fig.add_trace(go.Scatter(x=income_range, y=cdf*100, mode='lines',
                        name='Cumulative %', line=dict(color='#2ca02c', width=3)), row=1, col=2)

fig.update_layout(height=500, showlegend=False, hovermode='x unified', 
                  title="Canada Income Distribution (Interactive)")
fig.update_xaxes(title="Income ($ CAD)", tickformat="$,d", row=1, col=1)
fig.update_xaxes(title="Income ($ CAD)", tickformat="$,d", row=1, col=2)
fig.update_yaxes(title="Density", row=1, col=1)
fig.update_yaxes(title="Cumulative %", row=1, col=2)

st.plotly_chart(fig, use_container_width=True)

# Examples
st.subheader("⚡ Examples")
examples = [
    ("Low Income", 0, 30000),
    ("Middle Class", 40000, 100000),
    ("Upper Middle", 100000, 200000),
    ("High Income", 200000, 300000)
]

for name, min_i, max_i in examples:
    p = lognorm_cdf(max_i, sigma, scale) - lognorm_cdf(min_i, sigma, scale)
    st.caption(f"• **{name}** (${min_i:,}-${max_i:,}): {p*total_pop:,.0f} people ({p*100:.1f}%)")
