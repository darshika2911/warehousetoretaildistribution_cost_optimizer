# Attack: UPI Collect-Request Impersonation → Mule-Account Fund Movement

**Channel/rail:** UPI (real-time account-to-account payments)

## Mechanism
The fraudster contacts a victim by phone, SMS, or WhatsApp, posing as a
bank official or executive. They claim the victim's account has been
flagged for suspicious activity and that immediate "verification" is
required to avoid it being frozen. The victim is instructed to approve an
incoming UPI collect request — despite collect requests being used to
*receive* money, victims are manipulated into believing approval simply
confirms their identity. The request is crafted to display the real bank
name and the last four digits of the victim's account, which lends it
false legitimacy. Once approved, the payment is authorized and funds move
out of the victim's account immediately.

The receiving account is typically not the fraudster's own — it is the
first hop in a chain of "mule" accounts (accounts opened using stolen or
purchased identities, or belonging to people paid/coerced to receive and
forward funds). Money is moved through 4–6 such hops in quick succession,
then withdrawn as cash or converted, breaking the traceable link back to
the original fraudster.

## Real-world precedent
This is a live, high-frequency fraud pattern in India as of 2026, with
reported approved amounts ranging from ₹25,000 to ₹5,00,000 per incident.
NPCI has responded with a dedicated tool, MuleHunter AI, which has
identified over 4.7 lakh mule accounts to date — but new mule accounts are
onboarded continuously, and most banks/NBFCs still operate reactive,
post-facto fraud review rather than real-time detection at the point of
transaction.

## What GenAI specifically adds
- **Personalized impersonation scripts** — LLMs generate convincing,
  context-specific scam scripts (referencing real bank names, plausible
  "flagged account" scenarios) at a volume and quality no manual scam
  operation could match.
- **Victim targeting at scale** — combined with scraped/breached personal
  data, GenAI enables mass-personalization of the initial contact message,
  increasing conversion rates.
- **Faster mule-network orchestration** — AI-assisted coordination can
  script the hop sequence (which account receives, how much, how fast it
  forwards) to mimic normal transaction timing and avoid obvious velocity
  flags.

## Data signature (what this looks like in transaction data)
This is the critical section — it's the bridge to the Generate pillar.
The pattern should show up as:
- **Sudden receive-then-forward behavior** on an account with low or no
  prior transaction history (mule accounts don't have a normal, gradual
  usage pattern before this).
- **Short time gap** between receiving funds and forwarding them onward —
  mule accounts don't sit on money.
- **Multi-hop chain structure** — a traceable sequence of accounts
  (A → B → C → D) each receiving and near-immediately forwarding a similar
  amount within a compressed time window.
- **No prior relationship** between sender and first-hop receiver account
  (first-time payment, no transaction history between the two IDs).
- **Amount clustering** in the ₹25,000–₹5,00,000 range, occasionally split
  across hops to avoid single-transaction thresholds.
- **Account dormancy-to-activity spike** — receiving accounts often show
  a long dormant period followed by a sudden burst of activity tied to
  this event.

## Feasibility to simulate responsibly
High. This pattern requires no voice, video, or free-text generation —
only structured account/transaction-graph data (sender ID, receiver ID,
amount, timestamp, hop sequence, account age/activity history). It can be
fully represented using PaySim-style `TRANSFER`/`CASH_OUT` transaction
types as a structural base, with fraud-chain logic layered on top. No
component of this simulation could be repurposed as an actual scam tool —
it only produces labeled synthetic transaction records.
