# Өгөгдлийн гэрээ

UTF-8 JSONL: нэг мөр бүр нэг object.

Заавал: `id`, `instruction`, `output`, `source`, `license`, `split` — хоосон биш string. `input` сонголттой string. `split`: train, validation, test.

`source` нь эх баримт эсвэл dataset-ийн тогтвортой холбоос байна. `license`-ийг эх сурвалжийн нөхцөлийг уншиж бөглөнө. Шалгах скрипт лицензийн хууль зүйн хүчинтэй эсэх, Монгол хэлний чанар, хувийн мэдээлэл байгаа эсэхийг батлахгүй. Эдгээрт тусдаа хяналт хэрэгтэй.

Үндсэн validator-д бүх split-ийг хамтад нь өгвөл ижил instruction/input/output болон ID давхардлыг илрүүлнэ. Тусдаа fuzzy audit нь ойролцоо тэмдэгтийн хэв шинжийг зөвхөн review candidate болгон гаргана; ижил prompt өөр output-той байх, train/test эх баримтын давхардал, semantic утга болон орчуулгыг баталгаатай илрүүлэхгүй.

Тестийн асуултуудыг сургалтад бүү оруул. Эх баримтаар бүлэглэн split хийж, normalization, exact dedup болон `audit_evaluation_overlap.py`-ийн fuzzy candidate шалгалтыг ажиллуулна. Character n-gram audit нь semantic/translation overlap-ийг баталгаатай илрүүлэхгүй тул candidate бүрийг хүн шалгана. Raw өгөгдөл, нууц түлхүүр, хувийн мэдээлэл, том модель жинг GitHub-д commit хийхгүй.

`data/examples.jsonl`-ийн ганц жишээг CC0-1.0 нөхцөлөөр гаргасан; бусад өгөгдлийн лицензэд хамаарахгүй.
