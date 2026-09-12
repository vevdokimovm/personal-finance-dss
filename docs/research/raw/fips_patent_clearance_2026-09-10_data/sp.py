import json,ssl,sys,urllib.request
ctx=ssl._create_unverified_context()
def sp(body,path='/search'):
    r=urllib.request.Request('https://searchplatform.rospatent.gov.ru'+path,data=json.dumps(body,ensure_ascii=False).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0 Chrome/126'})
    try: return json.loads(urllib.request.urlopen(r,context=ctx,timeout=90).read())
    except urllib.error.HTTPError as e: return {'HTTPERR':e.code,'body':e.read()[:300].decode('utf-8','replace')}
if __name__=='__main__':
    print(json.dumps(sp(json.loads(sys.argv[1])),ensure_ascii=False)[:int(sys.argv[2]) if len(sys.argv)>2 else 3000])
