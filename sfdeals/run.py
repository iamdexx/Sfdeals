import sys, traceback
from . import parcels, citations, sheriff, delinquent, lincoln, score

STEPS = {"parcels": parcels.run, "citations": citations.run, "sheriff": sheriff.run,
         "delinquent": delinquent.run, "lincoln": lincoln.run, "score": score.run}

if __name__ == "__main__":
    names = sys.argv[1:] or list(STEPS)
    if names == ["all"]:
        names = list(STEPS)
    failed = []
    for n in names:
        try:
            print(n, STEPS[n]())
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            failed.append(n)
    if failed and failed != ["lincoln"]:
        sys.exit("failed: " + ", ".join(failed))
