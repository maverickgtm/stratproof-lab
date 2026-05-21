# License Decision Record

## Decision

Use `AGPL-3.0-or-later` for StratProof Lab Community Edition and reserve separate commercial licensing for Pro, Enterprise, SaaS, private deployments, and proprietary extensions.

## Rationale

StratProof Lab is likely to be valuable as a hosted audit system. A permissive license could allow direct SaaS cloning without contributing modifications back to the public project. AGPL is better aligned with a public-good Community Edition and a separate commercial path.

## Consequences

Positive:

- protects the Community Edition better than MIT/Apache for hosted derivatives;
- supports dual-license monetization;
- communicates serious open-source boundaries;
- keeps premium/private modules separate.

Tradeoffs:

- some companies avoid AGPL dependencies;
- commercial licensing must be clear;
- contributors need clear contribution terms;
- legal review is recommended before monetization.

## Future option

If adoption becomes more important than SaaS protection, a later project owner could evaluate MPL-2.0, Apache-2.0, or a business-source model for different editions. For now, AGPL + commercial dual licensing remains the selected path.
