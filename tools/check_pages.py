from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse
parser=argparse.ArgumentParser(description='Check local links in the built Jekyll site.')
parser.add_argument('site',nargs='?',default='_site')
parser.add_argument('--base-path',default='')
args=parser.parse_args()
root=Path(args.site).resolve()
base='/' + args.base_path.strip('/') if args.base_path.strip('/') else ''
class Page(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.add(d['id'])
  for k in ('href','src'):
   if k in d:self.links.append(d[k])
pages={}
for p in root.rglob('*.html'):
 obj=Page();obj.feed(p.read_text());pages[p.resolve()]=obj
errors=[];count=0
for p,obj in pages.items():
 for link in obj.links:
  u=urlsplit(link)
  if u.scheme or u.netloc:continue
  path=unquote(u.path)
  if path.startswith('/'):
   if base and (path==base or path.startswith(base+'/')):path=path[len(base):]
   target=(root/path.lstrip('/')).resolve()
  else:target=(p.parent/path).resolve() if path else p
  if target.is_dir():target=target/'index.html'
  count+=1
  if not target.exists():errors.append(f'{p.relative_to(root)} -> {link}: missing file')
  elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'{p.relative_to(root)} -> {link}: missing anchor')
print(f'{len(pages)} HTML pages; {count} internal links/assets; {len(errors)} errors')
print('\n'.join(errors[:30]))
raise SystemExit(bool(errors))
