"""Small real Mongolian text pilot with source revisions and attribution."""
import argparse, hashlib, json, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
TITLES=['Монгол улс','Улаанбаатар','Монгол хэл','Монгол бичиг','Кирилл үсэг','Орхон гол','Сэлэнгэ мөрөн','Хөвсгөл нуур','Увс нуур','Говь','Алтайн нуруу','Хангайн нуруу','Хэнтийн нуруу','Наадам','Морин хуур','Хөөмий','Уртын дуу','Гэр','Айраг','Цагаан сар']
def request(params):
 url='https://mn.wikipedia.org/w/api.php?'+urllib.parse.urlencode(dict(format='json',**params))
 req=urllib.request.Request(url,headers={'User-Agent':'RAINY-LLM/0.1 (https://github.com/ssboroo/rainy_llm)'})
 with urllib.request.urlopen(req,timeout=60) as response: data=json.load(response)
 if 'error' in data: raise ValueError(str(data['error']))
 return data

def collect():
 data=request(dict(action='query',titles='|'.join(TITLES),redirects=1,prop='extracts|info|revisions',explaintext=1,exintro=1,exlimit=20,rvprop='ids',inprop='url'))
 rows=[]; skipped=[]
 for page in sorted(data['query']['pages'].values(),key=lambda p:p['title']):
  text=page.get('extract','').strip()
  if len(text)<100: skipped.append(page['title']); continue
  revision=page['revisions'][0]['revid']
  rows.append(dict(id=f'mnwiki-{page["pageid"]}-{revision}',title=page['title'],text=text,
   source=page['fullurl'],revision=revision,revision_url=f'https://mn.wikipedia.org/w/index.php?oldid={revision}',
   attribution='Mongolian Wikipedia contributors',history_url=page['fullurl']+'?action=history',
   license='CC-BY-SA-4.0',license_url='https://creativecommons.org/licenses/by-sa/4.0/',
   modifications='API plain-text lead extraction; surrounding whitespace trimmed.',
   review_status='unreviewed-real-source-text',text_sha256=hashlib.sha256(text.encode()).hexdigest()))
 return rows,skipped

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True);a=p.parse_args();target=Path(a.output_dir)
 if target.exists(): p.exit(1,'output exists\n')
 rows,skipped=collect()
 if not rows: p.exit(1,'no data\n')
 target.mkdir(parents=True)
 payload=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows)
 (target/'corpus.jsonl').write_text(payload,encoding='utf-8')
 report=dict(retrieved_at=datetime.now(timezone.utc).isoformat(),articles=len(rows),characters=sum(len(r['text']) for r in rows),skipped=skipped,sha256=hashlib.sha256(payload.encode()).hexdigest(),source_terms='https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use',purpose='unreviewed real-text research pilot; not instruction data')
 (target/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
