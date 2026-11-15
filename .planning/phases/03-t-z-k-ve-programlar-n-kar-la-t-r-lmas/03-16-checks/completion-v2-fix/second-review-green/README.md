# Focused synthesis and structural-gap checks

The `proje-sr25-substantive-*` receipt is an earlier immutable test epoch.
It ran the real SR25 synthesis fixture including independently registered
mechanical and substantive replacements, and passed. Its copied input tree
was `/tmp/proje-sr25-substantive-20261115`; the pre-execution SHA list and
process handshake identify that tree and code. Subsequent local changes added
the prior-selection/date guard and an explicit rendered-output assertion, so
this earlier receipt is not evidence for those later bytes.

The `proje-final-focus-*` receipt is the later frozen focused batch. Its input
tree was `/tmp/proje-final-focus-20261115`; the input list was captured before
execution. It checks the structural future gap, the actual SR25 replacement and
rendered output, and the regenerated canonical package. The synthetic gap is
not a claim that a missing TİP or Yeni Yol source was discovered. This batch
does not run the longer isolated import/publish/audit round trip.
