R39 · Four-Gate Layer Structure
  Every layer has 4 gates: PRE-DEBUG (preconditions) · ANTICIPATE (known errors)
  · POST-DEBUG (real vs expected) · FRONTIER (no leakage to next layer).
  Without all 4, the layer is not valid even if result looks OK.

R40 · Known Error Anticipation
  Every layer declares anticipated errors in hbos_anticipations.
  The DAG reads them before executing. If an anticipated error is present,
  the layer enters arbitrage mode or halts, per severity.

R41 · Phase Frontier Debug
  At phase close, before advancing, a frontier debug verifies:
  consistent state · nothing leaked (keys, tokens, partial outputs, silent errors)
  · checkpoint written to Qdrant · ledger updated with all gates.
  If frontier debug fails, phase does not close, no advance.

R42 · FreeLLMAPI is Source of Truth for Arbitrage
  Chains, routing strategy and roadmap live in FreeLLMAPI (operational truth).
  Qdrant is factorization mirror: registers state for analysis, traceability
  and query · does not substitute nor duplicate FreeLLMAPI logic.

R43 · Auto-Edit by Default
  Every improvement or update is applied automatically via script.
  Registered in hbos_approvals with hash. No manual step-by-step.

R44 · Confirmation Only When Critical
  Confirmation pauses only when: editing secrets (R30/R31) · touching
  inviolable rules (R28, R32) · deleting/replacing Qdrant points (not only adding)
  · changing live routing strategy in FreeLLMAPI (not only mirroring)
  · opening/closing DAG gates.

R45 · Control from Antigravity
  When confirmation is required, it is given in Antigravity, not in chat.
  Chat reasons · Antigravity controls · Anti executes · Qdrant persists.
