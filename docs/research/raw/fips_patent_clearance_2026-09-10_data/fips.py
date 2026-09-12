import re, ssl, sys, urllib.request, urllib.parse, http.cookiejar, html as H
S='/private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/b2281723-6318-4dc9-8deb-dd9bf4d84cd4/scratchpad/'
ctx=ssl._create_unverified_context()
cj=http.cookiejar.CookieJar()
op=urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx),urllib.request.HTTPCookieProcessor(cj))
op.addheaders=[('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36')]
B='https://www1.fips.ru/iiss/'
def get(u): return op.open(B+u,timeout=60).read().decode('utf-8','replace')
def post(u,d,ajax=False):
    r=urllib.request.Request(B+u,data=urllib.parse.urlencode(d).encode())
    if ajax: r.add_header('Faces-Request','partial/ajax'); r.add_header('X-Requested-With','XMLHttpRequest')
    return op.open(r,timeout=90).read().decode('utf-8','replace')
def vs(h,form):
    i=h.find('id="%s"'%form); j=h.find('javax.faces.ViewState',i); return re.search(r'value="([^"]+)"',h[j:j+3000]).group(1)
def setup(dbs):
    h=get('db.xhtml'); v=vs(h,'db-selection-form')
    for k in dbs:
        cb='db-selection-form:%s'%k
        d={'javax.faces.partial.ajax':'true','javax.faces.source':cb,'javax.faces.partial.execute':cb,'javax.faces.behavior.event':'change','javax.faces.partial.event':'change','db-selection-form':'db-selection-form',cb:'on','javax.faces.ViewState':v}
        post('db.xhtml',d,True)
    h=get('db.xhtml'); v=vs(h,'sidebarForm')
    r=post('db.xhtml',{'sidebarForm':'sidebarForm','sidebarForm:searchLink':'sidebarForm:searchLink','javax.faces.ViewState':v})
    return r
if __name__=='__main__':
    r=setup(sys.argv[1:] or ['dbsGrid1:0:dbsGrid1checkbox'])
    open(S+'search_page.html','w').write(r)
    print(len(r)); 
    for m in re.finditer(r'<(input|select|textarea)[^>]*name="([^"]+)"[^>]*>',r): print(m.group(2))
    for m in re.finditer(r'<label[^>]*>([^<]+)</label>',r): print('L',m.group(1).strip())
