# Generate (Red Team - Simulation)

Synthetic data generator scripts — one per attack pattern selected from `/identify`.

Each generator:
- Takes the legit-transaction base (Kaggle/IEEE-CIS/PaySim) + a config dict + a random seed
- Outputs labeled fraud transactions matching the shared schema (see `/data/schema.md`)
- Gets validated for statistical fidelity against real fraud rows (KS-test on amount/timing distributions)

No working exploit code or real deepfake generation — synthetic feature vectors and mock templates only.
