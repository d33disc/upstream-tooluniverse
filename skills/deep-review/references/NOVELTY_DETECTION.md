# Novelty Detection

Classify every finding. The review's value is proportional to what a human
reader could not have found alone.

## Classification

| Label | Definition | Criterion |
| ------- | ----------- | ----------- |
| VERIFIED | Established fact | Confirmed by 2+ independent databases at T1/T2 |
| NOVEL INSIGHT | Cross-domain connection | Links entities from different domains; requires T2+ evidence from each side; not stated in any single source |
| NOVEL IP | Multi-hop hypothesis | 3+ hops through the entity graph producing a testable prediction; no existing publication states this claim |
| GAP | Known unknown | Expected data is missing; databases that should have it do not |
| INFORMATIVE NEGATIVE | Constraining absence | Empty result that narrows the hypothesis space (e.g., no FAERS signal constrains toxicity) |

## How to Detect Each

### VERIFIED

Two databases agree independently. Example: PubMed reports TP53 loss-of-function
in Li-Fraumeni AND ClinVar lists TP53 variants as pathogenic for the same
syndrome. Record both sources. No novelty claim.

### NOVEL INSIGHT

Entity A (from domain X) connects to entity B (from domain Y) through shared
biology, but no single publication states the connection. Example: KEGG shows
gene X in pathway P; OpenTargets shows drug D targeting pathway P; no PubMed
article links gene X to drug D. The cross-domain link is the insight.

Require: T2+ evidence on both sides. T4-only links (STRING prediction alone)
do not qualify.

### NOVEL IP

Three or more hops through the entity graph. Example: variant V (ClinVar) ->
gene G (Ensembl) -> pathway P (KEGG) -> drug D (ChEMBL) -> no trial for
disease Q (ClinicalTrials). The prediction: "Drug D may treat disease Q via
pathway P, testable by enrolling patients with variant V." State what would
falsify it.

### GAP

A database that should contain the entity does not. Example: a gene with
strong disease association in OpenTargets has zero ClinVar submissions.
Document: what was queried, what was expected, what was returned.

### INFORMATIVE NEGATIVE

An absence that constrains mechanism. Example: FAERS returns zero adverse
events for drug D at a dose that STRING predicts would disrupt protein
interactions. This absence argues against the predicted interaction being
clinically relevant at that dose.

## Cross-Domain Strategies

### Entity Pair Linking

For every unconnected (entity_A, entity_B) pair in the entity graph, search
for a bridging database. If gene G and drug D are both in the graph but not
connected, query: ChEMBL targets, KEGG pathways, OpenTargets associations.
A bridge found = NOVEL INSIGHT. No bridge found = GAP.

### Expanding Frontier

Each research wave discovers new entities. Track which entity pairs have been
checked and which remain. Prioritize pairs where both entities have T1/T2
evidence but no known connection.

### Informative Negatives as Evidence

Empty results are not failures. They constrain the hypothesis:

- No GWAS hits -> not a common-variant disease
- No FAERS signal -> low reported toxicity (not proof of safety)
- No ClinicalTrials entry -> therapeutic gap, potential opportunity
- No STRING interactions -> protein may act independently

Record every informative negative with: tool, query, expected result,
actual result, what this constrains.
