# Mongolian Wikipedia pilot — real source text

20 article introductions, 18,934 Unicode characters, retrieved 2026-09-28 UTC / 2026-09-29 Ulaanbaatar. This is retrieved text, not model-generated prose.

## Attribution and license

Text: Mongolian Wikipedia contributors, **CC BY-SA 4.0**.
License: https://creativecommons.org/licenses/by-sa/4.0/
Terms: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use

Each corpus record carries the article URL, history URL, reported revision ID, attribution, license URL and text hash. Follow the article/history URLs for individual contributors. Modifications: API plain-text lead extraction and surrounding-whitespace trimming. This dataset is an explicit exception to the repository's all-rights-reserved notice; the upstream share-alike license governs these texts and adapted text.

The API returned current extracts and revision metadata in one response. Extract caching can mean they are not a cryptographically verified rendering of the recorded revision; the stored text hash identifies the exact text actually collected. Retrieval logs and dates are in manifest.json.

## Quality and intended use

Unreviewed research pilot, not a release-quality training corpus. It includes factual claims that may be inaccurate or time-sensitive, template remnants, disambiguation notices and wording needing editorial review. No guarantee is made about correctness or absence of personal data. No images are included.

Schema: id, title, text, source, revision, revision_url, attribution, history_url, license, license_url, modifications, review_status, text_sha256. This is raw document format, deliberately NOT the instruction/output training format.

Do not transform article text into purported human-written instruction answers without documenting the transformation. Split at article level before generating examples; reserve held-out documents before any adaptation. Public Wikipedia may already be present in a base model's pretraining, so this is not a contamination-free benchmark.

## Монгол

Энэ багц нь Монгол Wikipedia-гаас татсан 20 өгүүллийн эхлэл хэсэг. AI-аар зохиогоогүй. Эх сурвалж, зохиогчдын түүх, хувилбар, лиценз, hash-тай хадгалсан.

CC BY-SA 4.0 нөхцөл үйлчилнэ; төслийн ерөнхий эрхийн мэдэгдэл энэ өгөгдлийн лицензийг өөрчлөхгүй. Өгөгдөлд загварын үлдэгдэл, найруулгын алдаа, хуучирсан эсвэл буруу баримт байж болно. Хүний хяналтгүйгээр сургалтын баталгаатай корпус гэж үзэхгүй. Загварын өмнөх сургалтад Wikipedia орсон байх боломжтой тул тус багцаар contamination-free чанар нотлохгүй.
