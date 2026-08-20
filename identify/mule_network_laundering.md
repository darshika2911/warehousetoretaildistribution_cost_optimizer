# Attack: Mule-Account / Laundering Network

**Channel/rail:** UPI (real-time account-to-account payments)

## Mechanism
Once funds are moved out of a victim's account — commonly through a
collect-request impersonation scam, where a fraudster posing as a bank
official convinces a victim to "verify" their identity by approving an
incoming UPI collect request — the money does not stay in one place.
It is routed rapidly through a chain of intermediary "mule" accounts
before final cash-out. Mule accounts are opened using stolen, purchased,
or synthetic identities, or belong to individuals paid or coerced into
receiving and forwarding funds. Each account in the chain receives the
money and, within a short window, forwards it onward to the next account
in the chain — typically 4-6 hops — before the final account withdraws
it as cash or converts it, breaking the traceable link back to the
original fraudster.

This attack module focuses specifically on **the movement of funds
through the mule chain**, not the initial social-engineering step that
gets money into the chain. The collect-request scam is documented below
as real-world precedent and context for how funds typically enter the
chain, but the buildable, simulate-able attack is the chain movement
itself — a structured, relationship-based pattern rather than a
free-text/voice social-engineering one.

## Real-world precedent
This is a live, high-frequency fraud pattern in India as of 2026.
Reported cases show a common front-end pattern: fraudsters impersonate
bank officials, convince victims their account is flagged, and get them
to approve a UPI collect request that displays the real bank name and
last four digits, lending false legitimacy. Approved amounts typically
range ₹25,000-₹5,00,000 per incident. NPCI has responded with a
dedicated tool, MuleHunter AI, which has identified over 4.7 lakh mule
accounts to date — but new mule accounts are onboarded continuously, and
most banks/NBFCs still operate reactive, post-facto fraud review rather
than real-time detection at the point of transaction.

## What GenAI specifically adds
- **Faster mule-network orchestration** — AI-assisted coordination can
  script the hop sequence (which account receives, how much, how fast it
  forwards) to mimic normal transaction timing and avoid obvious velocity
  flags.
- **Synthetic mule identities at scale** — GenAI-generated fake KYC
  documents let fraud networks open large numbers of mule accounts
  quickly, feeding a bigger, harder-to-map chain network.
- **Adaptive routing** — GenAI can help vary chain depth, hop timing, and
  amount-splitting patterns across campaigns to evade static detection
  rules, functioning as a built-in evolution mechanism.

## Data signature (what this looks like in transaction data)
This is the critical section — it defines what the generator must
produce, mapped to the shared team schema plus this attack's
relationship extension :

- **Receive-then-forward pattern**: an account receives funds
  (`direction = receive`) and, within a short time window, sends a
  similar amount onward (`direction = send`) to a different counterparty.
- **Short receive-to-forward latency** — mule accounts don't sit on
  money; the gap between receipt and onward transfer is much shorter
  than typical legitimate account behavior.
- **Multi-hop chain structure** — a traceable sequence of accounts
  (A → B → C → D), linked by a shared `chain_id`, each `hop_index`
  representing its position in the sequence.
- **No prior relationship between hops** — first-time payment between
  each pair of accounts in the chain, no transaction history between
  the two `entity_id`/`counterparty_entity_id` pairs.
- **Amount preservation with minor decay** — amount stays roughly
  consistent hop-to-hop, sometimes slightly reduced (a "cut" taken at
  each hop) or split across multiple downstream accounts.
- **Account dormancy-to-activity spike** — receiving accounts often show
  a long dormant period or thin prior history, followed by a sudden
  burst of activity tied to this event.
- **Amount clustering** in the ₹25,000-₹5,00,000 range at the point of
  entry into the chain (matching the collect-request precedent above),
  occasionally split across hops to avoid single-transaction thresholds.

## Schema extension required
The team's common event schema (`entity_id`, `merchant_id`, `device_id`,
`amount`, etc.) does not capture *relationships between entities*, which
is the defining feature of this attack. This module adds four fields on
top of the shared contract:

| Field | Purpose |
|---|---|
| `counterparty_entity_id` | who the money moved to/from in this event |
| `direction` | `"receive"` or `"send"` |
| `chain_id` | links all hops of one laundering episode together |
| `hop_index` | position in the chain (0 = first receipt, 1, 2, 3...) |

These are documented here for the team's schema so `/generate` and
`/defend` can plan for them, per the shared Integration Contract pattern.

## Feasibility to simulate responsibly
High. This pattern requires no voice, video, or free-text generation —
only structured account/transaction-graph data (entity IDs, counterparty
IDs, amounts, timestamps, chain/hop structure, account age/activity
history). It can be built using the same causal, single-pass behavioral
feature approach as the team's other attack modules, extended with
relationship-aware features (hop count, counterparty novelty,
receive-to-forward latency). No component of this simulation could be
repurposed as an actual money-laundering tool — it only produces labeled
synthetic transaction-graph records.
