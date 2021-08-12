import math
from .const import T_INT_WEIGHT, INTERNAL_SUN_ELEVATION_FACTOR

def relativeAirSpeed(v, met):
    if (met > 1):
        return v + 0.3 * (met - 1)
    else:
        return v

def calc_pmv(ta, tr, vel, rh, met, clo, wme = 0):
    # ta, air temperature (°C)
    # tr, mean radiant temperature (°C)
    # vel, relative air speed (m/s)
    # rh, relative humidity (%) Used only this way to input humidity level
    # met, metabolic rate (met)
    # clo, dynamic clothing insulation (clo)
    # wme, external work, normally around 0 (met)

    #  pa,
    #  icl,
    #  m,
    #  w,
    #  mw,
    #  fcl,
    #  hcf,
    #  taa,
    #  tra,
    #  t_cla,
    #  p1,
    #  p2,
    #  p3,
    #  p4,
    #  p5,
    #  xn,
    #  xf,
    #  eps,
    #  hcn,
    #  hc,
    #  tcl,
    #  hl1,
    #  hl2,
    #  hl3,
    #  hl4,
    #  hl5,
    #  hl6,
    #  ts,
    #  pmv,
    #  ppd,
    #  n;

    pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235))

    icl = 0.155 * clo # thermal insulation of the clothing in M2K/W
    m = met * 58.15 # metabolic rate in W/M2
    w = wme * 58.15 # external work in W/M2
    mw = m - w # internal heat production in the human body
    fcl = 1 + 1.29 * icl if icl <= 0.078 else 1.05 + 0.645 * icl

    # heat transfer coefficient by forced convection
    hcf = 12.1 * math.sqrt(vel)
    taa = ta + 273
    tra = tr + 273
    #  we have verified that using the equation below or this t_cla = taa + (35.5 - ta) / (3.5 * (6.45 * icl + .1)) does not affect the PMV value
    t_cla = taa + (35.5 - ta) / (3.5 * icl + 0.1)

    p1 = icl * fcl
    p2 = p1 * 3.96
    p3 = p1 * 100
    p4 = p1 * taa
    p5 = 308.7 - 0.028 * mw + p2 * math.pow(tra / 100, 4)
    xn = t_cla / 100
    xf = t_cla / 50
    eps = 0.00015

    n = 0
    while (abs(xn - xf) > eps):
        xf = (xf + xn) / 2
        hcn = 2.38 * math.pow(abs(100.0 * xf - taa), 0.25)
        hc = hcf if hcf > hcn else hcn
        xn = (p5 + p4 * hc - p2 * math.pow(xf, 4)) / (100 + p3 * hc)
        n += 1
        if (n > 150):
            raise Exception('math.max iterations exceeded')

    tcl = 100 * xn - 273

    #  heat loss diff. through skin
    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa)
    #  heat loss by sweating
    hl2 = 0.42 * (mw - 58.15) if (mw > 58.15) else 0
    #  latent respiration heat loss
    hl3 = 1.7 * 0.00001 * m * (5867 - pa)
    #  dry respiration heat loss
    hl4 = 0.0014 * m * (34 - ta)
    #  heat loss by radiation
    hl5 = 3.96 * fcl * (math.pow(xn, 4) - math.pow(tra / 100, 4))
    #  heat loss by convection
    hl6 = fcl * hc * (tcl - ta)

    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)
    ppd = 100.0 - 95.0 * math.exp(-0.03353 * math.pow(pmv, 4.0) - 0.2179 * math.pow(pmv, 2.0))

    return pmv, ppd

def pmvEN(ta, tr, vel, rh, met, clo, wme):
    
    # ta, air temperature (°C)
    # tr, mean radiant temperature (°C)
    # vel, average air speed (m/s)
    # rh, relative humidity (%)
    # met, metabolic rate (met)
    # clo, dynamic clothing insulation (clo)
    # wme, external work, normally around 0 (met)
    data = {}
    ras = relativeAirSpeed(vel, met)
    pmv, ppd = calc_pmv(ta, tr, ras, rh, met, clo, wme)
    data['pmv'] = pmv
    data['ppd'] = ppd
    return data


def get_mean_radiant_temperature(internal, external, sun_elevation):
    global T_INT_WEIGHT, INTERNAL_SUN_ELEVATION_FACTOR
    # T_INT_WEIGHT = 0.95
    f=sun_elevation*2*math.pi/360.0
    f = math.sin(f)
    w = T_INT_WEIGHT - (f*INTERNAL_SUN_ELEVATION_FACTOR)
    T_EXT_WEIGHT = 2 - w

    return round(((internal * w) + (external * T_EXT_WEIGHT)) / 2, 2)
# print(pmvEN(29.9, 30.0, 0.1, 59.1, 1.0, 0.5, 0))
