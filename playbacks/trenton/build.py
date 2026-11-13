"""Build the playback page: put data.json into page.src.html and write index.html, which opens in any browser."""
import os, re
W = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(W, 'page.src.html'), encoding='utf-8').read(); d = open(os.path.join(W, 'data.json'), encoding='utf-8').read().replace('</', '<\\/')
out = s.replace('__DATA__', d)
title = re.search(r'<title>.*?</title>', out).group(0); out = out.replace(title, '', 1)
sk='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'+title+'<style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>'
open(os.path.join(W,'index.html'),'w',encoding='utf-8').write(sk+out+'</body></html>'); print('index.html', len(out))
