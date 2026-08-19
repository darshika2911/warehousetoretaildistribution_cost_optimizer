# UPI Attack Scope

Primary UPI attack pattern for this project: **collect-request impersonation
leading to mule-account fund movement.**

A fraudster impersonates a bank official/executive and convinces a victim
that their account is flagged or at risk. The victim is told to "verify"
their identity by approving a UPI collect request — which actually
authorizes an outgoing payment, not a verification. The collect request
displays a real bank name and last-four digits, making it look legitimate.
Approved amounts typically range ₹25,000–₹5,00,000. Once received, funds
are moved rapidly through a chain of 4–6 mule accounts before final
withdrawal, to break the trail back to the fraudster.

This pattern is chosen over other UPI fraud types (QR-code swap scams,
fake merchant collect requests) because it has the clearest, most
well-documented behavioral signature that can be represented as structured
transaction-graph data — which is what makes it simulate-able and
detectable, rather than requiring free-text or voice/video modeling we
can't responsibly build.

This complements the CNP (card-not-present) track being built in parallel,
giving the overall system breadth across two structurally different
payment rails (card-number-based vs. account-ID-based).
