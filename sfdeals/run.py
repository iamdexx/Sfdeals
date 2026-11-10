"""python -m sfdeals.run [market] [step ...|all]

  python -m sfdeals.run all             every step of every market
  python -m sfdeals.run stl all         every St. Louis step
  python -m sfdeals.run sf parcels score
"""
import sys, traceback
from . import util
from .markets import MARKETS


def run_market(key, names):
    m = MARKETS[key]
    util.set_market(key)
    if names in ([], ["all"]):
        names = list(m["steps"])
    failed = []
    for n in names:
        try:
            print(key, n, m["steps"][n]())
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            failed.append(n)
    return [n for n in failed if n not in m["optional"]]


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] in MARKETS:
        jobs = [(args[0], args[1:])]
    else:
        jobs = [(k, args) for k in MARKETS]
    bad = []
    for key, names in jobs:
        bad += ["%s:%s" % (key, n) for n in run_market(key, names)]
    if bad:
        sys.exit("failed: " + ", ".join(bad))
