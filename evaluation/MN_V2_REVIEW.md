# Монгол evaluation v2 — хяналтын заавар / Review guide

100 original AI-authored draft cases, 10 cases in each of 10 categories. This is a public development set, not a private held-out benchmark or a human-reviewed release. No external corpus was copied. Fictional names and scenarios are used. Keep this set out of training. General Mongolian quality, long-form writing, cultural knowledge and real-world factual accuracy are not established by these short-answer tasks.

100 асуулт нь AI-аар боловсруулсан ноорог. Хүн бүрийг хянасны дараа release хийх боломжтой боловч нийтэд ил багц хэвээр; жинхэнэ хараат бус үнэлгээнд тусдаа, ашиглаагүй эх сурвалжтай асуултууд шаардлагатай. Өмнөх 24 асуултын `mn_smoke.jsonl` болон туршилтын оноонууд өөрчлөгдөөгүй. Шинэ 100 асуултын оноог хуучин 24 асуултын оноотой шууд харьцуулж болохгүй.

| Ангилал | Тоо | Шалгах чадвар |
| --- | ---: | --- |
| arithmetic | 10 | Тооцоо, нэгж, цаг, хувь |
| comprehension | 10 | Өгсөн эхийг ойлгох |
| instruction | 10 | Заавар, дараалал, формат |
| logic | 10 | Дүгнэлт, дараалал |
| translation | 10 | Богино үгийн орчуулга |
| transliteration | 10 | Латин бичвэрийг кирилл болгох |
| grammar | 10 | Өгүүлбэрээс хэлзүйн нэгж таних |
| spelling | 10 | Зөв бичсэн хувилбар сонгох |
| extraction | 10 | Өгсөн бүртгэлээс мэдээлэл авах |
| abstention | 10 | Мэдээлэл дутууг таних; 5 хариулах боломжтой control |

## Хүн хэрхэн хянах вэ?

`mn_v2_review_packet.jsonl`-ийн мөр бүрд prompt, proposed_answers, source, case_sha256 бий. Бүх decision нь pending, бүх check false байна.

1. Монгол хэл найруулга зөв эсэхийг шалга (`mongolian_wording`).
2. Хариуг өөрөө бодож, зөв бүх хувилбар багтсан эсэхийг шалга (`answer_correct`).
3. Асуулт нэг утгатай эсэхийг шалга (`unambiguous`). Латин галиг стандартгүй, үгийн орчуулга олон хувилбартай байж болно.
4. Сургалтын эх, жишээтэй давхцаагүйг шалга (`source_independent`). Зөвхөн энэ repository-ийн ганц format example-тэй audit хийсэн нь бүх training corpus-ийн баталгаа биш.
5. Богино exact-match тохирох эсэхийг шалга (`exact_match_suitable`). Одоогийн scorer том/жижиг үсэг, зайг normalize хийдэг тул үсгийн том жижиг хэлбэрийн чадварыг энд хэмжихгүй.
6. Бүгд зөв бол checks-ийг true, decision-ийг accept болго. Засвар хэрэгтэй бол notes-д бичиж reject хэвээр үлдээ. AI review-г human review гэж тэмдэглэхгүй.

Prompt/answers/source өөрчлөгдвөл case fingerprint өөрчлөгдөнө. Case-ийг засаад шинэ packet экспортлон дахин хянана. Хуучин hash-ийг хүчээр тохируулахгүй. Reviewer-ийн хувийн мэдээлэл repository-д оруулах шаардлагагүй.

```bash
python scripts/validate_evaluation.py evaluation/mn_v2_draft.jsonl --training data/examples.jsonl
python scripts/review_evaluation.py summary \
  --cases evaluation/mn_v2_draft.jsonl \
  --reviews evaluation/mn_v2_review_packet.jsonl
python scripts/review_evaluation.py apply \
  --cases evaluation/mn_v2_draft.jsonl \
  --reviews path/to/completed-reviews.jsonl \
  --output evaluation/mn_v2_reviewed.jsonl \
  --reviewed-at YYYY-MM-DD --reviewer-role human-reviewer
python scripts/validate_evaluation.py evaluation/mn_v2_reviewed.jsonl --release --training data/examples.jsonl
```

`summary` нь prompt/answer-ыг тайланд хуулахгүйгээр `pending`, `ready-accept`, `incomplete`, `rejected`, `missing`, `stale`, `invalid` төлвийг ангилал тус бүрээр тоолно. CI эсвэл review gate-д `--fail-unready` нэмбэл бүх мөр structurally ready биш үед exit 1 буцаана. `ready-accept` нь зөвхөн packet-ийн бүтэц бүрэн гэсэн үг; хүний хэн хянасныг батлахгүй, бодит human review-г орлохгүй. Одоогийн хэмжсэн тайлан [`mn_v2_review_progress.json`](mn_v2_review_progress.json)-д 100/100 `pending`, `ready_to_apply: false` байна.

The pending packet must fail `apply`; all 100 cases must pass real review before release. Benchmark inference has not been run on this version. Freeze the reviewed file and its SHA-256 before comparing candidates under identical runtime/decoding settings.
