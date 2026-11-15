# Historical completion fixture after v2 adoption

The RED and GREEN runs used separate pre-hashed frozen input trees. The RED
combines the actual immutable v1 release records and canonical v2 adoption
records under an isolated temporary current pointer. It reproduces the old
legacy test failing when it removes the marker required by a v2 revision.

The first post-fix run passed the scenario and omission checks but its renderer
check could not find `index.html` in the copied input tree. The final run uses
a new pre-hashed copy including the actual immutable historical HTML. It
exercises the same scenario, historical proof omission checks, and frozen
renderer 22. Historical tests explicitly load the immutable v1
release; live release reads return the actual current records without replacing
their completion marker. The isolated API round-trip fixture now points its
temporary current file at its own historical base. No production pointer or
release was modified; the independently running API job has its own inputs.
