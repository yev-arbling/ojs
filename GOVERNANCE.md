# OJS Governance

## Mission

The Open Jewelry Schema (OJS) exists to **make jewelry catalogs interoperable with AI commerce agents** without forcing retailers to negotiate proprietary terms with each agent platform separately. The schema is permissively licensed (CC0 for vocabulary, Apache 2.0 for tooling) so that adoption is frictionless.

## Steering Committee

OJS is governed by a steering committee that **must include named external members beyond the originating maintainer (Arbling)** to prevent "zombie standard" capture by any single party.

Initial committee composition target (to be filled before v1.0 announcement):

- 1 seat — Arbling Inc. (founding maintainer)
- 1 seat — large jewelry retailer (Tier 1 e-commerce, ≥$50M GMV)
- 1 seat — gemological / industry body (GIA, CIBJO, or equivalent)
- 1 seat — independent technical architect (Schema.org / GS1 / FHIR background)
- 1 seat — At-large community contributor (rotating annually)

**Quorum**: 3 of 5 for normal decisions; 4 of 5 for breaking-change releases.

## Decision-making

- **Issues and pull requests**: any maintainer can merge non-controversial changes (typos, codelist additions, examples).
- **Field additions, deprecations**: require steering committee review on the public mailing list with ≥14-day comment period.
- **Breaking changes (major version bumps)**: require unanimous committee approval and a 6-month migration window.

## Contribution mechanism

OJS uses **DCO (Developer Certificate of Origin)** sign-off rather than a CLA. Contributors sign off each commit with `Signed-off-by:` per the standard DCO 1.1 text. This pattern matches GitLab's 2017 move from CLA to DCO and lowers contribution friction.

We do NOT collect copyright assignments. Contributors retain copyright; their contributions are licensed inbound under the same dual-license terms as the project (CC0 for vocabulary changes, Apache 2.0 for code).

## Code of Conduct

OJS adopts the [Contributor Covenant 3.0](https://www.contributor-covenant.org/version/3/0/code_of_conduct/) (released July 28, 2025). Violations should be reported to `conduct@openjewelryschema.org`. The steering committee maintains the enforcement ladder.

## Release cadence

- **Patches** (codelist additions, doc fixes): on demand, no schedule.
- **Minor releases**: quarterly target. Backwards-compatible additions only.
- **Major releases**: target ≥18 months between major versions to provide migration stability. Breaking changes batched.

## Versioning

OJS follows [SemVer 2.0](https://semver.org/). Codelists version independently of the core schema (`metals.json` v1.2 can be paired with OJS spec v1.0).

## Funding and operations

OJS is operated by Arbling Inc. at this time, with infrastructure funded by Arbling and committee members. We commit to publishing **annual budget transparency reports** beginning 12 months post-v1.0 launch — covering hosting costs, CI/CD spend, conference outreach, and any sponsorships received.

Target operating budget: **$22-38K/year** with 0.2 FTE of maintainer time. This is realistic for a vocabulary-style project at this scope (GS1 WebVoc operates on similar budget; FHIR Argonaut velocity guidance applies).

## Trademark policy

The "OJS" and "Open Jewelry Schema" names and logos are NOT subject to CC0/Apache licensing — they are trademarks of Arbling Inc. used to identify the canonical project. Forks may use the schema and tooling freely under their licenses; forks may NOT use the project names without explicit permission.

## Conflict resolution

Maintainer disputes are escalated to the steering committee. Steering committee deadlocks are resolved by a public vote on the mailing list with all contributors (commits in the last 12 months) eligible to vote.

## Successor planning

In the event Arbling Inc. ceases operations or chooses to divest from OJS maintenance, the project's domain (`openjewelryschema.org`), GitHub organization, and trademark rights are committed to be transferred to an independent foundation (preferred: Linux Foundation Projects, Apache Software Foundation, or a new 501(c)(6)). The committee identifies a successor home within 12 months of triggering events.

## References

- [Developer Certificate of Origin 1.1](https://developercertificate.org/)
- [Contributor Covenant 3.0](https://www.contributor-covenant.org/version/3/0/code_of_conduct/)
- [GitLab's CLA-to-DCO migration (Nov 2017)](https://about.gitlab.com/blog/2017/11/01/gitlab-dco/)
- [Linux Foundation Projects](https://www.linuxfoundation.org/projects)
