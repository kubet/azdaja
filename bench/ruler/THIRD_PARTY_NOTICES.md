# Third-party notices for `ruler-exact-mini-v1`

This file inventories software and data resources used to generate the private
suite. Azdaja does not modify the listed upstream source. Each generated public
tree redistributes the exact pinned RULER `LICENSE` as
`LICENSE.NVIDIA-RULER` and a copy of this notice. Any redistributed fixture copy
must retain applicable notices and license terms. This inventory is not a
substitute for license texts in each upstream distribution.

## NVIDIA RULER

* Project: <https://github.com/NVIDIA/RULER>
* Pinned source: `c3f5e3b4f87f97e048793bb510a3a6b19a46bf3a`
* Copyright: NVIDIA Corporation
* License: Apache License 2.0
* Pinned `LICENSE` SHA-256:
  `43070e2d4e532684de521b885f385d0841030efa2b1a20bafb76133a5e1379c1`

RULER describes itself as a research benchmark and not an NVIDIA product. This
Azdaja suite executes the unmodified pinned generator and selects a disclosed
three-task subset. `ruler-exact-mini-v1` is not the full RULER benchmark and is
not leaderboard-comparable.

Apache License 2.0 text: <https://www.apache.org/licenses/LICENSE-2.0>

## Python packages

Exact versions and distribution hashes are in `requirements.lock`.

| Distribution | Version | License / notice source |
|---|---:|---|
| certifi | 2026.7.22 | Mozilla Public License 2.0; <https://github.com/certifi/python-certifi> |
| charset-normalizer | 3.5.0 | MIT; <https://github.com/jawah/charset_normalizer> |
| click | 8.4.2 | BSD-3-Clause; <https://github.com/pallets/click> |
| colorama (Windows marker only) | 0.4.6 | BSD-3-Clause; <https://github.com/tartley/colorama> |
| idna | 3.18 | BSD-3-Clause; <https://github.com/kjd/idna> |
| joblib | 1.5.3 | BSD-3-Clause; <https://github.com/joblib/joblib> |
| NLTK | 3.9.2 | Apache-2.0; <https://github.com/nltk/nltk> |
| NumPy | 2.3.5 | BSD-3-Clause and bundled component notices; <https://numpy.org/doc/stable/license.html> |
| PyYAML | 6.0.3 | MIT; <https://github.com/yaml/pyyaml> |
| regex | 2026.7.19 | Apache-2.0/CNRI-derived notices; <https://github.com/mrabarnett/mrab-regex> |
| Requests | 2.34.2 | Apache-2.0; <https://github.com/psf/requests> |
| SciPy | 1.16.3 | BSD-3-Clause and bundled component notices; <https://scipy.org/scipylib/license.html> |
| Tenacity | 9.1.2 | Apache-2.0; <https://github.com/jd/tenacity> |
| tiktoken | 0.12.0 | MIT; <https://github.com/openai/tiktoken> |
| tqdm | 4.67.1 | MPL-2.0 and MIT; <https://github.com/tqdm/tqdm> |
| urllib3 | 2.7.0 | MIT; <https://github.com/urllib3/urllib3> |
| wonderwords | 3.0.1 | MIT; copyright Maxim Rebguns; <https://github.com/mrmaxguns/wonderwordsmodule> |

MPL-2.0 text: <https://www.mozilla.org/MPL/2.0/>

## Downloaded generation resources

`tiktoken` downloads the OpenAI `cl100k_base.tiktoken` encoding data from
<https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken>.
The sealer requires SHA-256
`223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`.
See the tiktoken repository and installed distribution for its MIT notice.

The owner initially obtains `punkt` and `punkt_tab` from the NLTK data repository:
<https://github.com/nltk/nltk_data>. `build` accepts only the two pinned archive
SHA-256 values recorded in `README.md`, safely extracts them into a private
snapshot before starting RULER, and rejects any NLTK downloader attempt during
generation. Consult each NLTK data package's included metadata/README and model
provenance before redistributing those archives. They are generation inputs and
are not included in this repository or in the public inference payload tree.

## Common permissive-license texts

MIT license text: <https://opensource.org/license/mit>

BSD 3-Clause license text: <https://opensource.org/license/bsd-3-clause>
