# Control Evidence Review

Produce a dated view of which security controls have current evidence, which checks failed and which owners need to supply fresh evidence. This is a small policy-to-engineering project for teams maintaining a control register. It runs offline with Python 3.11+ and the standard library.

## Run a review

```sh
python review.py examples/controls.csv examples/evidence.csv --as-of 2026-11-01
python -m unittest discover -s tests -v
```

| Control | Result on 1 November | Reason |
| --- | --- | --- |
| IAM-01 | current | The passing identity review is two days old. |
| LOG-01 | stale | The passing log sample is 31 days old against a 14-day limit. |
| BKP-01 | failed | The latest restore drill failed after an earlier pass. |
| ENC-01 | missing | Its only evidence is dated after the review. |

Repeat the command with `--as-of 2026-11-10` to see ENC-01 become current. The explicit date makes historical reviews reproducible.

## Data model

`controls.csv` assigns a unique control ID, accountable owner and maximum evidence age in whole days. `evidence.csv` records the control ID, observation date, pass/fail result and a reference to supporting material. Both files require their headers, as shown in the examples. For an empty evidence log, supply its header alone.

The latest observation on or before the review date governs the result. A failed check remains failed until superseded. Passing evidence is current through the final day of its allowed interval. An unknown control ID or two observations for the same control on the same day is rejected because it would make the report ambiguous.

## Scope

The register, dates and evidence references are illustrative. The program reports what the supplied records support. A current entry means a passing observation exists within the chosen interval. The program does not inspect the referenced evidence or certify compliance with a legal standard.
