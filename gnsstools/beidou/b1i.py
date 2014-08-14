# Beidou B1I code construction (serves also for B2I)
#
# Copyright 2014 Peter Monta

import numpy as np

chip_rate = 2046000
code_length = 2046

secondary_code = np.array([0,0,0,0,0,1,0,0,1,1,0,1,0,1,0,0,1,1,1,0])
secondary_code = 1.0 - 2.0*secondary_code

b1i_g2_taps = {
   1: (1,3),    2: (1,4),    3: (1,5),    4: (1,6),
   5: (1,8),    6: (1,9),    7: (1,10),   8: (1,11),
   9: (2,7),   10: (3,4),   11: (3,5),   12: (3,6),
  13: (3,8),   14: (3,9),   15: (3,10),  16: (3,11),
  17: (4,5),   18: (4,6),   19: (4,8),   20: (4,9),
  21: (4,10),  22: (4,11),  23: (5,6),   24: (5,8),
  25: (5,9),   26: (5,10),  27: (5,11),  28: (6,8),
  29: (6,9),   30: (6,10),  31: (6,11),  32: (8,9),
  33: (8,10),  34: (8,11),  35: (9,10),  36: (9,11),
  37: (10,11)
}

def b1i_g1_shift(x):
  return [x[0]^x[6]^x[7]^x[8]^x[9]^x[10]] + x[0:10]

def b1i_g2_shift(x):
  return [x[0]^x[1]^x[2]^x[3]^x[4]^x[7]^x[8]^x[10]] + x[0:10]

def b1i(prn):
  n = code_length
  (tap1,tap2) = b1i_g2_taps[prn]
  g1 = [0,1,0,1,0,1,0,1,0,1,0]
  g2 = [0,1,0,1,0,1,0,1,0,1,0]
  b1i = np.zeros(n)
  for i in range(n):
    b1i[i] = g1[10] ^ g2[tap1-1] ^ g2[tap2-1]
    g1 = b1i_g1_shift(g1)
    g2 = b1i_g2_shift(g2)
  return b1i

codes = {}

def b1i_code(prn):
  if not codes.has_key(prn):
    codes[prn] = b1i(prn)
  return codes[prn]

def code(prn,chips,frac,incr,n):
  c = b1i_code(prn)
  idx = (chips%code_length) + frac + incr*np.arange(n)
  idx = np.floor(idx).astype('int')
  idx = np.mod(idx,code_length)
  x = c[idx]
  return 1.0 - 2.0*x

from numba import jit

@jit(nopython=True)
def correlate(x,prn,chips,frac,incr,c):
  n = len(x)
  p = 0.0j
  cp = (chips+frac)%code_length
  for i in range(n):
    p += x[i]*(1.0-2.0*c[int(cp)])
    cp = (cp+incr)%code_length
  return p

# test

if __name__=='__main__':
  print b1i_code(1)[0:20]
  print b1i_code(2)[0:20]
