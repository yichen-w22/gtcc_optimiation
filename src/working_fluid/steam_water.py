import math
from dataclasses import dataclass
from typing import Optional

from iapws import IAPWS97

from src.base.stream import FlowState

_T_FREEZE = 273.15
_CP_ICE = 2090.0       # J/(kg·K)
_L_FUSION = 333500.0   # J/kg


def _ice_h_s(T):
    """Return (h, s) in J/kg and J/(kg·K) for ice below 0°C, referenced to liquid water at 0°C."""
    dT = T - _T_FREEZE
    h = -_L_FUSION + _CP_ICE * dT
    s = -_L_FUSION / _T_FREEZE + _CP_ICE * math.log(T / _T_FREEZE)
    return h, s

def _invalid_state(cls, *, P=None, T=None, m_dot=None, name="", ref=None, x=None):
    return cls(
        name=name,
        T=T,
        P=P,
        m_dot=m_dot,
        h=None,
        s=None,
        ref=ref,
        x=x,
    )


@dataclass
class WaterSteamState(FlowState):
    x: Optional[float] = None

    @classmethod
    def from_PT(cls, P, T, m_dot=None, name="", ref=None):
        if (P is None or isinstance(P, float) and math.isnan(P)) or (T is None or isinstance(T, float) and math.isnan(T)):
            return _invalid_state(cls, P=P, T=T, m_dot=m_dot, name=name, ref=ref)
        if T < _T_FREEZE:
            h, s = _ice_h_s(T)
            return cls(name=name, T=T, P=P, m_dot=m_dot, h=h, s=s, x=0.0, ref=ref)
        try:
            if 611.657 <= P < 22.064e6:
                saturated = IAPWS97(P=P / 1e6, x=0)
                if math.isclose(T, saturated.T, abs_tol=1e-5, rel_tol=0):
                    state = _invalid_state(cls, P=P, T=T, m_dot=m_dot, name=name, ref=ref)
                    return state
            w = IAPWS97(P=P / 1e6, T=T)
        except Exception:
            return _invalid_state(cls, P=P, T=T, m_dot=m_dot, name=name, ref=ref)
        if (w.h is None or isinstance(w.h, float) and math.isnan(w.h)) or (w.s is None or isinstance(w.s, float) and math.isnan(w.s)):
            return _invalid_state(
                cls,
                P=P,
                T=T,
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=getattr(w, "x", None),
            )
        return cls(
            name=name,
            T=T,
            P=P,
            m_dot=m_dot,
            h=w.h * 1000.0,
            s=w.s * 1000.0,
            x=getattr(w, "x", None),
            ref=ref,
        )

    @classmethod
    def from_Px(cls, P, x, m_dot=None, name="", ref=None):
        if (P is None or isinstance(P, float) and math.isnan(P)) or (x is None or isinstance(x, float) and math.isnan(x)):
            return _invalid_state(
                cls,
                P=P,
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=x,
            )
        try:
            w = IAPWS97(P=P / 1e6, x=x)
        except Exception:
            return _invalid_state(
                cls,
                P=P,
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=x,
            )
        if (w.h is None or isinstance(w.h, float) and math.isnan(w.h)) or (w.s is None or isinstance(w.s, float) and math.isnan(w.s)):
            return _invalid_state(
                cls,
                P=P,
                T=getattr(w, "T", None),
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=getattr(w, "x", x),
            )
        return cls(
            name=name,
            T=w.T,
            P=P,
            m_dot=m_dot,
            h=w.h * 1000.0,
            s=w.s * 1000.0,
            x=getattr(w, "x", x),
            ref=ref,
        )

    @classmethod
    def from_Ps(cls, P, s, m_dot=None, name="", ref=None):
        if (P is None or isinstance(P, float) and math.isnan(P)) or (s is None or isinstance(s, float) and math.isnan(s)):
            return _invalid_state(cls, P=P, m_dot=m_dot, name=name, ref=ref)
        try:
            w = IAPWS97(P=P / 1e6, s=s / 1000.0)
        except Exception:
            return _invalid_state(cls, P=P, m_dot=m_dot, name=name, ref=ref)
        if (w.h is None or isinstance(w.h, float) and math.isnan(w.h)) or (w.s is None or isinstance(w.s, float) and math.isnan(w.s)):
            return _invalid_state(
                cls,
                P=P,
                T=getattr(w, "T", None),
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=getattr(w, "x", None),
            )
        return cls(
            name=name,
            T=w.T,
            P=P,
            m_dot=m_dot,
            h=w.h * 1000.0,
            s=w.s * 1000.0,
            x=getattr(w, "x", None),
            ref=ref,
        )

    @classmethod
    def from_Ph(cls, P, h, m_dot=None, name="", ref=None):
        if (P is None or isinstance(P, float) and math.isnan(P)) or (h is None or isinstance(h, float) and math.isnan(h)):
            return _invalid_state(cls, P=P, m_dot=m_dot, name=name, ref=ref)
        try:
            w = IAPWS97(P=P / 1e6, h=h / 1000.0)
        except Exception:
            return _invalid_state(cls, P=P, m_dot=m_dot, name=name, ref=ref)
        if (w.h is None or isinstance(w.h, float) and math.isnan(w.h)) or (w.s is None or isinstance(w.s, float) and math.isnan(w.s)):
            return _invalid_state(
                cls,
                P=P,
                T=getattr(w, "T", None),
                m_dot=m_dot,
                name=name,
                ref=ref,
                x=getattr(w, "x", None),
            )
        return cls(
            name=name,
            T=w.T,
            P=P,
            m_dot=m_dot,
            h=w.h * 1000.0,
            s=w.s * 1000.0,
            x=getattr(w, "x", None),
            ref=ref,
        )

    @property
    def exergy(self):
        if self.ref is None or (self.h is None or isinstance(self.h, float) and math.isnan(self.h)) or (self.s is None or isinstance(self.s, float) and math.isnan(self.s)):
            return None
        reference_state = self.from_PT(P=self.ref.P0, T=self.ref.T0)
        if (reference_state.h is None or isinstance(reference_state.h, float) and math.isnan(reference_state.h)) or (reference_state.s is None or isinstance(reference_state.s, float) and math.isnan(reference_state.s)):
            return None
        enthalpy_delta = (self.h - reference_state.h)
        entropy_delta = (self.s - reference_state.s)
        ambient_term = (self.ref.T0 * entropy_delta)
        return (enthalpy_delta - ambient_term)


def infer_m2_by_enthalpy_balance(
    m1: Optional[float],
    T1: Optional[float],
    P1: Optional[float],
    T2: Optional[float],
    P2: Optional[float],
    T3: Optional[float],
    P3: Optional[float],
    q_dot: float = 0.0,
    eps: float = 1e-6,
) -> tuple[Optional[float], Optional[float]]:
    """
    Infer the second and mixed water-steam mass flows from PT states.

    m1*h1(P1, T1) + m2*h2(P2, T2) + q_dot = m3*h3(P3, T3)
    m3 = m1 + m2

    Returns ``(None, None)`` when a state is invalid or the equation is
    ill-conditioned.
    """
    if any((v is None or isinstance(v, float) and math.isnan(v)) for v in (m1, T1, P1, T2, P2, T3, P3)) or m1 < 0:
        return None, None
    if (eps is None or isinstance(eps, float) and math.isnan(eps)) or eps < 0:
        eps = 1e-6

    state1 = WaterSteamState.from_PT(P=P1, T=T1)
    state2 = WaterSteamState.from_PT(P=P2, T=T2)
    state3 = WaterSteamState.from_PT(P=P3, T=T3)
    if any((state.h is None or isinstance(state.h, float) and math.isnan(state.h)) for state in (state1, state2, state3)):
        return None, None

    numerator = (m1 * (state1.h - state3.h) + q_dot)
    denominator = (state3.h - state2.h)

    if (numerator is None or isinstance(numerator, float) and math.isnan(numerator)) or (denominator is None or isinstance(denominator, float) and math.isnan(denominator)):
        return None, None
    if abs(float(denominator)) <= eps:
        return None, None

    m2 = (numerator / denominator)
    if (m2 is None or isinstance(m2, float) and math.isnan(m2)) or m2 < 0:
        return None, None
    m3 = (m1 + m2)
    if (m3 is None or isinstance(m3, float) and math.isnan(m3)) or m3 < 0:
        return None, None
    return m2, m3
