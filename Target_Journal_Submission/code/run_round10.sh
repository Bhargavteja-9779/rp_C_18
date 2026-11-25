#!/bin/bash
# Round 10 (deviations 62-63). Re-runnable: RESUME=1 keeps finished states.
cd "$(dirname "$0")/.."
export RESUME=1
(STRATA=svi python3 code/src/equity_check.py 5 as > results/log_svi_as.txt 2>&1; FRONTIER=1 STRATA=county python3 code/src/equity_check.py 5 as > results/log_frontier_county.txt 2>&1) &
(STRATA=svi python3 code/src/equity_check.py 3 n > results/log_svi_n.txt 2>&1; FRONTIER=1 STRATA=svi python3 code/src/equity_check.py 5 as > results/log_frontier_svi.txt 2>&1) &
(STRATA=svi python3 code/src/equity_check.py 3 u > results/log_svi_u.txt 2>&1) &
(STRATA=svi python3 code/src/equity_check.py 3 f > results/log_svi_f.txt 2>&1) &
wait
