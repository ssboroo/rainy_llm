"""CPU Qwen3 baseline: pinned revision, real generations and recorded metadata."""
import argparse, hashlib, json, platform, time
from pathlib import Path
from prepare_data import read_rows
from evaluate import score

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--cases',default='evaluation/mn_smoke.jsonl'); p.add_argument('--output-dir',required=True)
 p.add_argument('--revision',required=True);p.add_argument('--model',default='Qwen/Qwen3-0.6B')
 p.add_argument('--threads',type=int,default=4);p.add_argument('--max-new-tokens',type=int,default=64)
 a=p.parse_args()
 import torch, transformers
 from transformers import AutoTokenizer, AutoModelForCausalLM
 torch.set_num_threads(a.threads);torch.manual_seed(42)
 target=Path(a.output_dir);target.mkdir(parents=True,exist_ok=False)
 cases=read_rows(a.cases)
 tokenizer=AutoTokenizer.from_pretrained(a.model,revision=a.revision,trust_remote_code=False)
 model=AutoModelForCausalLM.from_pretrained(a.model,revision=a.revision,trust_remote_code=False,torch_dtype=torch.float32)
 model.eval(); predictions=[]
 metadata=dict(model=a.model,revision=a.revision,device='cpu',dtype='float32',threads=a.threads,seed=42,
  torch=torch.__version__,transformers=transformers.__version__,python=platform.python_version(),
  thinking=False,do_sample=False,max_new_tokens=a.max_new_tokens,
  cases_sha256=hashlib.sha256(Path(a.cases).read_bytes()).hexdigest(),status='running',
  note='Small older model used for feasible CPU baseline; not a latest-model quality claim. Greedy non-thinking run.')
 (target/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
 with (target/'predictions.jsonl').open('w',encoding='utf-8') as out:
  for case in cases:
   prompt=tokenizer.apply_chat_template([dict(role='user',content=case['prompt'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
   inputs=tokenizer(prompt,return_tensors='pt');start=time.perf_counter()
   with torch.inference_mode(): result=model.generate(**inputs,max_new_tokens=a.max_new_tokens,do_sample=False,pad_token_id=tokenizer.eos_token_id)
   tokens=result[0,inputs['input_ids'].shape[1]:]
   row=dict(id=case['id'],output=tokenizer.decode(tokens,skip_special_tokens=True).strip(),generated_tokens=len(tokens),seconds=round(time.perf_counter()-start,4),hit_token_limit=len(tokens)>=a.max_new_tokens)
   predictions.append(row);out.write(json.dumps(row,ensure_ascii=False)+'\n');out.flush();print(row['id'],repr(row['output']),flush=True)
 report=score(cases,predictions);(target/'scores.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 metadata['status']='completed';metadata['total_generation_seconds']=sum(r['seconds'] for r in predictions)
 (target/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n');print('SCORE',report['correct'],report['total'],flush=True)
if __name__=='__main__':main()
