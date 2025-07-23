
import math
import streamlit as st
from CoolProp.CoolProp import PropsSI
from scipy.optimize import fsolve

st.title("Air-Side Area Calculator using P–NTU Method for Finned Tube Condenser")

st.sidebar.header("User Inputs")

# User inputs
fluid = st.sidebar.selectbox("Refrigerant", ["R134a", "R407C"])
m_dot_freon = st.sidebar.number_input("Freon Mass Flow Rate (kg/s)", value=0.599)

# Q inputs
Q_desuper = st.sidebar.number_input("Q for Desuperheating (kW)", value=20.0) * 1000
Q_cond = st.sidebar.number_input("Q for Condensation (kW)", value=100.0) * 1000
Q_sub = st.sidebar.number_input("Q for Subcooling (kW)", value=30.0) * 1000

# U values
U_desuper = st.sidebar.number_input("U for Desuperheating (W/m²·K)", value=70.0)
U_cond = st.sidebar.number_input("U for Condensation (W/m²·K)", value=80.0)
U_sub = st.sidebar.number_input("U for Subcooling (W/m²·K)", value=65.0)

# Air side
T_air_desuper = st.sidebar.number_input("Air Inlet Temp for Desuperheating (°C)", value=52.0) + 273.15
T_air_cond = st.sidebar.number_input("Air Inlet Temp for Condensation (°C)", value=45.0) + 273.15
T_air_sub = st.sidebar.number_input("Air Inlet Temp for Subcooling (°C)", value=40.0) + 273.15

# Freon temps
T_super_in = st.sidebar.number_input("Freon Superheated Inlet Temp (°C)", value=95.0) + 273.15
T_cond = st.sidebar.number_input("Freon Condensing Temp (°C)", value=57.0) + 273.15
P_cond = st.sidebar.number_input("Freon Condensing Pressure (Pa)", value=2352000.0)
T_sub_out = st.sidebar.number_input("Freon Subcooled Out Temp (°C)", value=52.0) + 273.15

# Air flow rates
m_dot_air_desuper = st.sidebar.number_input("Air Mass Flow Rate for Desuperheating (kg/s)", value=8.0)
m_dot_air_cond = st.sidebar.number_input("Air Mass Flow Rate for Condensation (kg/s)", value=12.0)
m_dot_air_sub = st.sidebar.number_input("Air Mass Flow Rate for Subcooling (kg/s)", value=5.0)

cp_air = 1006

def solve_NTU_eps(eps_target, Cr):
    def eq(NTU):
        return 1 - math.exp((1 / Cr) * (NTU**0.22) * (math.exp(-Cr * NTU**0.78) - 1)) - eps_target
    NTU_guess = 1.0
    NTU_sol = fsolve(eq, NTU_guess)[0]
    return NTU_sol

def compute_area(Q, T_hot, T_air_in, m_dot_air, U, zone_name, use_explicit=False):
    C_air = m_dot_air * cp_air
    delta_T_max = T_hot - T_air_in
    eps = Q / (C_air * delta_T_max)

    if use_explicit:
        NTU = -math.log(1 - eps)
    else:
        Cr = 1e-6  # close to zero for condensing zone
        NTU = solve_NTU_eps(eps, Cr)

    A = NTU * C_air / U
    T_air_out = T_air_in + Q / C_air
    return A, NTU, eps, T_air_out - 273.15

st.header("Results")

zones = [
    ("Desuperheating", Q_desuper, T_super_in, T_air_desuper, m_dot_air_desuper, U_desuper, False),
    ("Condensation", Q_cond, T_cond, T_air_cond, m_dot_air_cond, U_cond, True),
    ("Subcooling", Q_sub, T_cond, T_air_sub, m_dot_air_sub, U_sub, False)
]

for name, Q, T_hot, T_air_in, m_dot_air, U, use_simple in zones:
    A, NTU, eps, T_air_out = compute_area(Q, T_hot, T_air_in, m_dot_air, U, name, use_simple)
    st.subheader(f"{name} Zone")
    st.write(f"Required Area: {A:.2f} m²")
    st.write(f"NTU: {NTU:.2f}, Effectiveness: {eps:.3f}")
    st.write(f"Air Outlet Temp: {T_air_out:.2f} °C")
