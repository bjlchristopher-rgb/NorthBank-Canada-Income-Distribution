import streamlit as st
import numpy as np
from scipy.stats import lognorm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("🗺️ Interactive Canada Income Distribution Calculator")

# Parameters for Canadian income distribution (log-normal)
mu = 10.45  # Mean of log income
sigma = 0.95  # Standard deviation of log income
total_population = 20000000  # ~20M tax filers aged 15+

# Generate income distribution
income_range = np.linspace(0, 300000, 1000)
pdf_values = lognorm.pdf(income_range, sigma, scale=np.exp(mu))
cdf_values = lognorm.cdf(income_range, sigma, scale=np.exp(mu))

# Sidebar inputs
st.sidebar.header("Income Range Selector")
min_income = st.sidebar.slider("Minimum Income ($)", 0, 150000, 25000, 5000)
max_income = st.sidebar.slider("Maximum Income ($)", min_income, 300000, 100000, 5000)

# Calculate population between min and max
prob_between = lognorm.cdf(max_income, sigma, scale=np.exp(mu)) - lognorm.cdf(min_income, sigma, scale=np.exp(mu))
num_people = prob_between * total_population
percentage = prob_between * 100

# Display results
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("People in Range", f"{num_people:,.0f}")
with col2:
    st.metric("Percentage of Population", f"{percentage:.1f}%")
with col3:
    st.metric("Income Range", f"${min_income:,} - ${max_income:,}")

# Create interactive chart
fig = make_subplots(sizes=[0.7, 0.3], rows=1, cols=2, 
                    subplot_titles=('Income Distribution', 'Cumulative Distribution'),
                    specs=[[{"secondary_y": False}, {"secondary_y": False}]])

# Main density curve
fig.add_trace(go.Scatter(x=income_range, y=pdf_values/np.max(pdf_values)*100,
                        mode='lines', name='Population Density',
                        line=dict(color='blue', width=3)), row=1, col=1)

# Highlight selected range
fig.add_vrect(x0=min_income, x1=max_income, fillcolor="rgba(255,0,0,0.2)", 
              layer="below", line_width=0, row=1, col=1)

# Cumulative distribution
fig.add_trace(go.Scatter(x=income_range, y=cdf_values*100,
                        mode='lines', name='Cumulative %',
                        line=dict(color='green', width=2)), row=1, col=2)

# Vertical lines for min/max
fig.add_vline(x=min_income, line_dash="dash", line_color="red", row=1, col=1)
fig.add_vline(x=max_income, line_dash="dash", line_color="red", row=1, col=1)

fig.update_layout(height=500, title_text="Canada Income Distribution (Interactive)",
                  showlegend=True, hovermode='x unified')
fig.update_xaxes(title_text="Income ($ CAD)", row=1, col=1)
fig.update_xaxes(title_text="Income ($ CAD)", row=1, col=2)
fig.update_yaxes(title_text="Density (%)", row=1, col=1)
fig.update_yaxes(title_text="Cumulative %", row=1, col=2)

st.plotly_chart(fig, use_container_width=True)

# Examples
st.subheader("Quick Examples")
examples = [
    ("Low Income", 0, 30000, "~5.2M people (26%)"),
    ("Middle Class", 40000, 100000, "~7.8M people (39%)"),
    ("Upper Middle", 100000, 200000, "~1.9M people (9.5%)"),
    ("High Income", 200000, 500000, "~0.4M people (2%)")
]

for label, min_inc, max_inc, result in examples:
    prob = lognorm.cdf(max_inc, sigma, scale=np.exp(mu)) - lognorm.cdf(min_inc, sigma, scale=np.exp(mu))
    st.caption(f"• **{label}** (${min_inc:,}-${max_inc:,}): {prob*total_population:,.0f} people ({prob*100:.1f}%)")
