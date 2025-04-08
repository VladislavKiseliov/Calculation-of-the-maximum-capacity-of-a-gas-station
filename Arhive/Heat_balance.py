import tkinter as tk
from tkinter import ttk

def heat_balance(P_in,P_out,T_in,T_out,Boiler_capacity,Di,Ccp,typeCalculate = False):

    T_heat_exchanger = T_out+(P_in-P_out) * Di
    Q = (Boiler_capacity/(1163*0.000001*(T_heat_exchanger-T_in)*Ccp))

    if typeCalculate:
        return Q
    else:
        return Q,T_heat_exchanger
