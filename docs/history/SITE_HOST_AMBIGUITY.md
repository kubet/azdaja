# Site host configuration ambiguity

The tracked site surface currently contains overlapping host-oriented files:

- `site/CNAME` and `site/.nojekyll` are compatible with a custom-domain GitHub Pages deployment.
- `site/_headers` uses the redirects/headers-file convention supported by hosts such as Netlify.
- `site/vercel.json` defines a Vercel deployment and a partly overlapping header policy.

The repository contains no current deployment receipt or reviewed ownership record that establishes which one host is authoritative, whether more than one is intentionally active, or which header policy is served at `azdaja.dev`. File presence alone is not sufficient evidence to select a host. Keep all three configurations until deployment evidence and owner intent establish a safe consolidation path.
