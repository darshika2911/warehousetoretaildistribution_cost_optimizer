# Identify (Red Team - Ideation)

Attack catalog: one-pager per GenAI-enabled fraud pattern.

Each entry follows this template:
- **Attack name + channel/rail** (CNP or UPI)
- **Mechanism** — how it actually works, grounded in real payment mechanics
- **Real-world precedent** — reported cases, even adjacent non-AI fraud
- **What GenAI specifically adds** — speed, personalization, evasion, realism
- **Data signature** — what it would look like in transaction/account data (this feeds `/generate`)
- **Feasibility to simulate responsibly**

`scope.md` in this folder locks our rail decision: CNP (primary) + UPI (secondary).
