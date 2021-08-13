comf = {};
comf.pmvEN = function (ta, tr, vel, rh, met, clo, wme) {
    /**
    ta, air temperature (°C)
    tr, mean radiant temperature (°C)
    vel, average air speed (m/s)
    rh, relative humidity (%)
    met, metabolic rate (met)
    clo, dynamic clothing insulation (clo)
    wme, external work, normally around 0 (met)
     */
    const data = {};
    const relativeAirSpeed = comf.relativeAirSpeed(vel, met);
    const pmv = comf.pmv(ta, tr, relativeAirSpeed, rh, met, clo, wme);
    data.pmv = pmv.pmv;
    data.ppd = pmv.ppd;
    return data;
  };

  comf.relativeAirSpeed = function (v, met) {
    if (met > 1) {
      return v + 0.3 * (met - 1);
    } else {
      return v;
    }
  };

  comf.pmv = function (ta, tr, vel, rh, met, clo, wme = 0) {
    /**
    ta, air temperature (°C)
    tr, mean radiant temperature (°C)
    vel, relative air speed (m/s)
    rh, relative humidity (%) Used only this way to input humidity level
    met, metabolic rate (met)
    clo, dynamic clothing insulation (clo)
    wme, external work, normally around 0 (met)
     */
  
    let pa,
      icl,
      m,
      w,
      mw,
      fcl,
      hcf,
      taa,
      tra,
      t_cla,
      p1,
      p2,
      p3,
      p4,
      p5,
      xn,
      xf,
      eps,
      hcn,
      hc,
      tcl,
      hl1,
      hl2,
      hl3,
      hl4,
      hl5,
      hl6,
      ts,
      pmv,
      ppd,
      n;
  
    pa = rh * 10 * Math.exp(16.6536 - 4030.183 / (ta + 235));
  
    icl = 0.155 * clo; //thermal insulation of the clothing in M2K/W
    m = met * 58.15; //metabolic rate in W/M2
    w = wme * 58.15; //external work in W/M2
    mw = m - w; //internal heat production in the human body
    if (icl <= 0.078) fcl = 1 + 1.29 * icl;
    else fcl = 1.05 + 0.645 * icl;
  
    //heat transfer coefficient by forced convection
    hcf = 12.1 * Math.sqrt(vel);
    taa = ta + 273;
    tra = tr + 273;
    // we have verified that using the equation below or this t_cla = taa + (35.5 - ta) / (3.5 * (6.45 * icl + .1)) does not affect the PMV value
    t_cla = taa + (35.5 - ta) / (3.5 * icl + 0.1);
  
    p1 = icl * fcl;
    p2 = p1 * 3.96;
    p3 = p1 * 100;
    p4 = p1 * taa;
    p5 = 308.7 - 0.028 * mw + p2 * Math.pow(tra / 100, 4);
    xn = t_cla / 100;
    xf = t_cla / 50;
    eps = 0.00015;
  
    n = 0;
    while (Math.abs(xn - xf) > eps) {
      xf = (xf + xn) / 2;
      hcn = 2.38 * Math.pow(Math.abs(100.0 * xf - taa), 0.25);
      if (hcf > hcn) hc = hcf;
      else hc = hcn;
      xn = (p5 + p4 * hc - p2 * Math.pow(xf, 4)) / (100 + p3 * hc);
      ++n;
      if (n > 150) {
        alert("Math.max iterations exceeded");
        return 1;
      }
    }
  
    tcl = 100 * xn - 273;
  
    // heat loss diff. through skin
    hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa);
    // heat loss by sweating
    if (mw > 58.15) hl2 = 0.42 * (mw - 58.15);
    else hl2 = 0;
    // latent respiration heat loss
    hl3 = 1.7 * 0.00001 * m * (5867 - pa);
    // dry respiration heat loss
    hl4 = 0.0014 * m * (34 - ta);
    // heat loss by radiation
    hl5 = 3.96 * fcl * (Math.pow(xn, 4) - Math.pow(tra / 100, 4));
    // heat loss by convection
    hl6 = fcl * hc * (tcl - ta);
  
    ts = 0.303 * Math.exp(-0.036 * m) + 0.028;
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6);
    ppd =
      100.0 -
      95.0 *
        Math.exp(-0.03353 * Math.pow(pmv, 4.0) - 0.2179 * Math.pow(pmv, 2.0));
  
    return {
      pmv: pmv,
      ppd: ppd,
      hl1: hl1,
      hl2: hl2,
      hl3: hl3,
      hl4: hl4,
      hl5: hl5,
      hl6: hl6,
    };
  };
  