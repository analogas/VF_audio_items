
import os, secrets, hmac
from contextlib import contextmanager
from html import escape
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.environ['SECRET_KEY'], https_only=True, same_site='lax')
PASSWORD = os.environ['APP_PASSWORD']
@contextmanager
def connect():
    with psycopg.connect(os.environ['DATABASE_URL'], row_factory=dict_row) as c:
        yield c

def esc(x): return escape(str(x or ''))
def redirect(path='/'): return RedirectResponse(path, status_code=303)
def shell(body):
    import re
    labels = {'/actions/item': '+ Pridėti daiktą', '/actions/category': '+ Pridėti kategoriją', '/actions/case': '+ Naujas case’as', '/actions/show': '+ Nauja išvyka', '/actions/vehicle': '+ Pridėti automobilį'}
    def fold(match):
        label = labels.get(match.group(1))
        return ('<details><summary>' + label + '</summary>' + match.group(0) + '</details>') if label else match.group(0)
    body = re.sub(r'<form method="post" action="([^"]+)">.*?</form>', fold, body, flags=re.S)
    return HTMLResponse('<!doctype html><html lang="lt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#f5f7fb"><title>VF · Audio sandėlys</title><style>\n:root{--bg:#f5f7fb;--paper:#fff;--ink:#17243b;--muted:#617189;--line:#dce3ef;--accent:#2856db}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{background:var(--paper);border-bottom:1px solid var(--line)}.top{max-width:1080px;margin:auto;padding:20px 24px;display:flex;justify-content:space-between;align-items:center;gap:12px}.brand{font-weight:800;letter-spacing:-.5px;font-size:21px}.brand span{display:inline-grid;place-items:center;background:var(--accent);color:white;border-radius:10px;width:40px;height:40px;margin-right:10px}.subtitle{font-size:13px;color:var(--muted)}nav{max-width:1080px;margin:auto;display:flex;gap:8px;padding:0 24px 14px}nav a{color:var(--muted);text-decoration:none;padding:10px 15px;border-radius:10px;font-size:14px;font-weight:650;white-space:nowrap}nav a[aria-current=page]{background:#eaf0ff;color:var(--accent)}main{max-width:1000px;padding:32px 24px 100px;margin:auto}h1{font-size:clamp(27px,5vw,36px);line-height:1.2;letter-spacing:-1px;margin:0 0 24px}h2{font-size:20px;line-height:1.35;margin:10px 0;color:var(--ink)}p{margin:10px 0}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}section{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:22px;margin:14px 0;box-shadow:0 3px 12px #20315005}section>a:first-child{font-weight:750;font-size:19px}small{color:var(--muted);font-size:13px}section>small{display:inline-block;border-radius:6px;padding:3px 8px;background:#eef2f8}form{margin:12px 0}input,select,button{font:inherit;min-height:46px;max-width:100%;border-radius:10px}input,select{display:block;width:100%;padding:11px 13px;border:1px solid #bdc9dc;background:white;color:var(--ink);margin:5px 0 16px}input[type=hidden]{display:none}input::placeholder{color:#7d8899}label{font-size:14px;font-weight:650;display:block;margin-top:14px}button{padding:11px 18px;border:1px solid transparent;background:var(--accent);color:white;font-weight:650;cursor:pointer}button:hover{background:#1e46b9}button:disabled{opacity:.6;cursor:wait}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #95b2ff;outline-offset:3px}input:focus,select:focus{outline:3px solid #d8e4ff;border-color:var(--accent)}details{margin:12px 0;border:1px solid var(--line);background:white;border-radius:12px;overflow:hidden}summary{padding:14px 18px;cursor:pointer;font-weight:650;color:var(--accent)}details>form{padding:0 18px 16px;margin:0}details[open] summary{border-bottom:1px solid var(--line);margin-bottom:12px}.tools{display:flex;gap:12px;align-items:center;margin:24px 0 10px}.tools input,.tools select{margin:0}.tools input{flex:1}.tools select{width:auto;max-width:45%}.empty{padding:26px;text-align:center;border:1px dashed #bbc8da;border-radius:14px;color:var(--muted);margin:18px 0}.notice{font-size:14px;color:var(--muted);border-left:3px solid #a5b8e2;padding:10px 14px;background:#edf2fb;margin-bottom:20px}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:16px}.metric{background:#f5f7fb;border-radius:9px;padding:10px}.metric span{display:block;color:var(--muted);font-size:12px}.metric strong{font-size:22px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:0 0 24px}.stat{background:white;border:1px solid var(--line);padding:16px;border-radius:12px;font-size:13px;color:var(--muted)}.stat strong{display:block;font-size:26px;color:var(--ink)}.back{display:inline-block;margin-bottom:16px;font-size:14px}footer{font-size:12px;color:var(--muted);margin-top:30px}[hidden]{display:none!important}@media(max-width:600px){.top{padding:16px}.subtitle{display:none}main{padding:24px 16px 110px}nav{position:fixed;bottom:0;left:0;right:0;background:white;z-index:20;border-top:1px solid var(--line);padding:8px 6px calc(8px + env(safe-area-inset-bottom));justify-content:space-around;gap:0}nav a{padding:10px 7px;font-size:12px}section{padding:17px}.stats{gap:8px}.stat{padding:11px}.tools{flex-wrap:wrap}.tools select{max-width:100%;width:100%}.metrics{gap:5px}.metric{padding:8px}}\n</style></head><body><header><div class="top"><div class="brand"><span>VF</span>Audio sandėlys</div><div class="subtitle">Įranga · Case’ai · Išvykos</div></div><nav aria-label="Pagrindinė navigacija"><a href="/">Apžvalga</a><a href="/items">Daiktai</a><a href="/cases">Case’ai</a><a href="/shows">Išvykos</a><a href="/vehicles">Automobiliai</a></nav></header><main>' + body + '<footer>VF · Audio inventoriaus valdymas</footer></main>' + "<script>\n(()=>{\nconst path=location.pathname,main=document.querySelector('main');\ndocument.querySelectorAll('nav a').forEach(a=>{if(a.getAttribute('href')===path||(a.getAttribute('href')==='/cases'&&path.startsWith('/cases/')))a.setAttribute('aria-current','page')});\nif(path==='/login'){document.querySelector('nav').hidden=true;document.querySelector('.subtitle').hidden=true;}\nconst names={name:'Pavadinimas',category_id:'Kategorija',qty:'Kiekis, vnt.',city:'Miestas',date_out:'Išvykimo data',password:'Bendras prisijungimo slaptažodis',item_id:'Daiktas'};\ndocument.querySelectorAll('form input:not([type=hidden]), form select').forEach((el,i)=>{if(el.previousElementSibling?.tagName==='LABEL')return;let text=names[el.name];if(text){el.id='field-'+i;const l=document.createElement('label');l.htmlFor=el.id;l.textContent=text;el.before(l)}});\nconst sections=[...main.querySelectorAll(':scope > section')];\nif(path==='/'){\n const stats=document.createElement('div');stats.className='stats';\n const counts=[['Case’ų',sections.length],['Išvykose',sections.filter(s=>!s.textContent.includes('Šou: Sandėlyje')).length],['Sandėlyje',sections.filter(s=>s.textContent.includes('Šou: Sandėlyje')).length]];\n counts.forEach(([label,value])=>{const d=document.createElement('div');d.className='stat';const n=document.createElement('strong');n.textContent=value;d.append(n,document.createTextNode(label));stats.append(d)});\n main.querySelector('h1')?.after(stats);\n main.querySelector(':scope > p')?.classList.add('notice');\n}\nif(['/items','/cases','/shows','/vehicles'].includes(path)){\n const titles={'/items':'Ieškoti daikto…','/cases':'Ieškoti case’o…','/shows':'Ieškoti išvykos ar miesto…','/vehicles':'Ieškoti automobilio…'};\n const bar=document.createElement('div');bar.className='tools';const input=document.createElement('input');input.type='search';input.placeholder=titles[path];input.setAttribute('aria-label',titles[path]);bar.append(input);\n let filter;\n if(path==='/items'){\n filter=document.createElement('select');filter.setAttribute('aria-label','Filtruoti pagal kategoriją');filter.add(new Option('Visos kategorijos',''));\n [...new Set(sections.map(s=>s.querySelector('small')?.textContent).filter(Boolean))].forEach(v=>filter.add(new Option(v,v)));bar.append(filter);\n }\n const h=main.querySelector('h1');h?.after(bar);\n const empty=document.createElement('div');empty.className='empty';main.append(empty);\n const update=()=>{let n=0;const term=input.value.toLocaleLowerCase('lt').trim();sections.forEach(s=>{const match=s.textContent.toLocaleLowerCase('lt').includes(term)&&(!filter||!filter.value||s.querySelector('small')?.textContent===filter.value);s.hidden=!match;if(match)n++});empty.hidden=n>0;empty.textContent=sections.length?'Nieko nerasta. Pakeiskite paiešką arba kategoriją.':'Sąrašas tuščias. Pridėkite pirmą įrašą naudodami „+“ mygtuką.'};input.addEventListener('input',update);filter?.addEventListener('change',update);update();\n}\nif(path.startsWith('/cases/')){const back=document.createElement('a');back.href='/cases';back.className='back';back.textContent='← Visi case’ai';main.prepend(back);}\n// Only disable repeated submits after the browser has accepted form validation.\ndocument.querySelectorAll('form').forEach(f=>f.addEventListener('submit',()=>{f.querySelectorAll('button').forEach(b=>{b.disabled=true;b.textContent='Saugoma…'})}));\n})();</script>" + '</body></html>')


@app.on_event('startup')
def startup():
    with connect() as c:
        for sql in [
            'CREATE TABLE IF NOT EXISTS categories(id SERIAL PRIMARY KEY, name TEXT UNIQUE NOT NULL)',
            'CREATE TABLE IF NOT EXISTS items(id SERIAL PRIMARY KEY, name TEXT NOT NULL, category_id INTEGER REFERENCES categories(id), qty INTEGER NOT NULL CHECK(qty>0))',
            'CREATE TABLE IF NOT EXISTS vehicles(id SERIAL PRIMARY KEY,name TEXT NOT NULL)',
            'CREATE TABLE IF NOT EXISTS shows(id SERIAL PRIMARY KEY,name TEXT NOT NULL,city TEXT NOT NULL,date_out TEXT NOT NULL)',
            'CREATE TABLE IF NOT EXISTS cases(id SERIAL PRIMARY KEY,name TEXT NOT NULL,show_id INTEGER REFERENCES shows(id),vehicle_id INTEGER REFERENCES vehicles(id))',
            'CREATE TABLE IF NOT EXISTS contents(case_id INTEGER REFERENCES cases(id),item_id INTEGER REFERENCES items(id),qty INTEGER NOT NULL CHECK(qty>0),PRIMARY KEY(case_id,item_id))'
        ]: c.execute(sql)
        for name in ['Mikrofonai','Laidai','Stovai','DI ir splitteriai','Belaidė įranga','Pultai','Kita']:
            c.execute('INSERT INTO categories(name) VALUES(%s) ON CONFLICT DO NOTHING',(name,))

@app.get('/health')
def health(): return {'status':'ok'}

@app.get('/login')
def login_page():
    return shell('<h1>Prisijungimas</h1><form method="post"><input type="password" name="password" required placeholder="Slaptažodis"><button>Prisijungti</button></form>')
@app.post('/login')
async def login(request: Request):
    form=await request.form()
    if hmac.compare_digest(str(form.get('password','')),PASSWORD):
        request.session.clear(); request.session['ok']=True; request.session['csrf']=secrets.token_urlsafe(32)
        return redirect()
    return shell('<p>Neteisingas slaptažodis.</p><a href="/login">Bandyti dar kartą</a>')

def token(request):
    return '<input type="hidden" name="csrf" value="'+esc(request.session['csrf'])+'">'
def form_open(request, action): return '<form method="post" action="'+action+'">'+token(request)
def options(rows, selected=None):
    return ''.join('<option value="'+str(r['id'])+'"'+(' selected' if r['id']==selected else '')+'>'+esc(r['name'])+'</option>' for r in rows)

@app.get('/')
def home(request: Request):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c:
        rows=c.execute('SELECT cs.*,s.name AS show_name,s.city,v.name AS vehicle FROM cases cs LEFT JOIN shows s ON s.id=cs.show_id LEFT JOIN vehicles v ON v.id=cs.vehicle_id ORDER BY s.name,cs.name').fetchall()
    return shell('<h1>Audio sandėlys</h1><p>Case’o priskyrimas automobiliui šiame prototipe reiškia planuojamą pakrovimą, ne patvirtinimą, kad jis fiziškai pakrautas.</p>'+''.join('<section><a href="/cases/'+str(r['id'])+'">'+esc(r['name'])+'</a><p>Šou: '+esc(r['show_name'] or 'Sandėlyje')+' · '+esc(r['city'])+'</p><p>Automobilis: '+esc(r['vehicle'] or 'Nepriskirtas')+'</p></section>' for r in rows))

@app.get('/items')
def items(request: Request):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c:
        cats=c.execute('SELECT * FROM categories ORDER BY name').fetchall()
        rows=c.execute('SELECT i.*,c.name AS category,COALESCE((SELECT SUM(qty) FROM contents WHERE item_id=i.id),0) AS packed FROM items i JOIN categories c ON c.id=i.category_id ORDER BY c.name,i.name').fetchall()
    body='<h1>Daiktai</h1>'+form_open(request,'/actions/item')+'<input name="name" placeholder="Pavadinimas" required><select name="category_id">'+options(cats)+'</select><input type="number" name="qty" min="1" value="1" required><button>Pridėti daiktą</button></form>'
    body+=form_open(request,'/actions/category')+'<input name="name" placeholder="Nauja kategorija" required><button>Pridėti kategoriją</button></form>'
    for r in rows: body+='<section><small>'+esc(r['category'])+'</small><h2>'+esc(r['name'])+'</h2><div class="metrics"><div class="metric"><span>Iš viso</span><strong>'+str(r['qty'])+'</strong></div><div class="metric"><span>Case’uose</span><strong>'+str(r['packed'])+'</strong></div><div class="metric"><span>Nesupakuota</span><strong>'+str(r['qty']-r['packed'])+'</strong></div></div></section>'
    return shell(body)

@app.get('/cases')
def cases(request: Request):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c: rows=c.execute('SELECT * FROM cases ORDER BY name').fetchall()
    return shell('<h1>Case’ai</h1>'+form_open(request,'/actions/case')+'<input name="name" placeholder="Case’o pavadinimas" required><button>Sukurti</button></form>'+''.join('<section><a href="/cases/'+str(r['id'])+'">'+esc(r['name'])+'</a></section>' for r in rows))

@app.get('/cases/{cid}')
def case(request: Request,cid:int):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c:
        cs=c.execute('SELECT * FROM cases WHERE id=%s',(cid,)).fetchone()
        if not cs: return redirect('/cases')
        rows=c.execute('SELECT i.id,i.name,ct.qty FROM contents ct JOIN items i ON i.id=ct.item_id WHERE ct.case_id=%s ORDER BY i.name',(cid,)).fetchall()
        items=c.execute('SELECT * FROM items ORDER BY name').fetchall()
        shows=c.execute('SELECT * FROM shows ORDER BY date_out').fetchall()
        vehicles=c.execute('SELECT * FROM vehicles ORDER BY name').fetchall()
    body='<h1>'+esc(cs['name'])+'</h1><h2>Turinys</h2>'
    for r in rows:
        body+='<section>'+esc(r['name'])+' × '+str(r['qty'])+form_open(request,f'/actions/unpack/{cid}')+'<input type="hidden" name="item_id" value="'+str(r['id'])+'"><button>Išimti visą šią eilutę</button></form></section>'
    body+=form_open(request,f'/actions/pack/{cid}')+'<select name="item_id">'+options(items)+'</select><input type="number" name="qty" min="1" value="1" required><button>Įdėti į case’ą</button></form><h2>Priskyrimas</h2>'
    body+=form_open(request,f'/actions/assign/{cid}')+'<label>Šou</label><select name="show_id"><option value="">Sandėlyje</option>'+options(shows,cs['show_id'])+'</select><label>Automobilis</label><select name="vehicle_id"><option value="">Nepriskirtas</option>'+options(vehicles,cs['vehicle_id'])+'</select><button>Išsaugoti</button></form><p>Grįžus pasirink „Sandėlyje“ ir „Nepriskirtas“. Turinys liks case’e.</p>'
    return shell(body)

@app.get('/shows')
def shows(request: Request):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c: rows=c.execute('SELECT * FROM shows ORDER BY date_out DESC').fetchall()
    return shell('<h1>Šou</h1>'+form_open(request,'/actions/show')+'<input name="name" placeholder="Spektaklis / šou" required><input name="city" placeholder="Miestas" required><input type="date" name="date_out" required><button>Sukurti išvyką</button></form>'+''.join('<section>'+esc(r['name'])+' · '+esc(r['city'])+' · '+esc(r['date_out'])+'</section>' for r in rows))

@app.get('/vehicles')
def vehicles(request: Request):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c: rows=c.execute('SELECT * FROM vehicles ORDER BY name').fetchall()
    return shell('<h1>Automobiliai</h1>'+form_open(request,'/actions/vehicle')+'<input name="name" placeholder="Pvz. Sprinteris ABC123" required><button>Pridėti</button></form>'+''.join('<section>'+esc(r['name'])+'</section>' for r in rows))

@app.post('/actions/{action}')
@app.post('/actions/{action}/{cid}')
async def action(request: Request,action:str,cid:int=0):
    if not request.session.get('ok'): return redirect('/login')
    f=await request.form()
    if not hmac.compare_digest(str(f.get('csrf','')),str(request.session.get('csrf',''))):
        return HTMLResponse('Neteisinga forma. Perkraukite puslapį.',status_code=403)
    try:
        with connect() as c:
            name=str(f.get('name','')).strip()
            if action in ['category','item','case','show','vehicle'] and not name: raise ValueError('Įrašykite pavadinimą.')
            if action=='category': c.execute('INSERT INTO categories(name) VALUES(%s) ON CONFLICT DO NOTHING',(name,)); target='/items'
            elif action=='item': c.execute('INSERT INTO items(name,category_id,qty) VALUES(%s,%s,%s)',(name,int(f['category_id']),int(f['qty']))); target='/items'
            elif action=='case': c.execute('INSERT INTO cases(name) VALUES(%s)',(name,)); target='/cases'
            elif action=='show': c.execute('INSERT INTO shows(name,city,date_out) VALUES(%s,%s,%s)',(name,str(f['city']),str(f['date_out']))); target='/shows'
            elif action=='vehicle': c.execute('INSERT INTO vehicles(name) VALUES(%s)',(name,)); target='/vehicles'
            elif action=='pack':
                iid=int(f['item_id']); qty=int(f['qty'])
                item=c.execute('SELECT qty FROM items WHERE id=%s FOR UPDATE',(iid,)).fetchone()
                used=c.execute('SELECT COALESCE(SUM(qty),0) AS n FROM contents WHERE item_id=%s',(iid,)).fetchone()['n']
                if not item or qty<=0 or used+qty>item['qty']: raise ValueError('Nepakanka nesupakuotų daiktų. Patikrinkite Daiktų skiltį.')
                c.execute('INSERT INTO contents(case_id,item_id,qty) VALUES(%s,%s,%s) ON CONFLICT(case_id,item_id) DO UPDATE SET qty=contents.qty+EXCLUDED.qty',(cid,iid,qty)); target=f'/cases/{cid}'
            elif action=='unpack':
                iid=int(f['item_id']); c.execute('SELECT id FROM items WHERE id=%s FOR UPDATE',(iid,))
                c.execute('DELETE FROM contents WHERE case_id=%s AND item_id=%s',(cid,iid)); target=f'/cases/{cid}'
            elif action=='assign':
                sid=int(f['show_id']) if f.get('show_id') else None
                vid=int(f['vehicle_id']) if f.get('vehicle_id') and sid else None
                c.execute('UPDATE cases SET show_id=%s,vehicle_id=%s WHERE id=%s',(sid,vid,cid)); target=f'/cases/{cid}'
            else: return HTMLResponse('Nežinomas veiksmas',status_code=404)
        return redirect(target)
    except (ValueError,KeyError):
        return shell('<h1>Nepavyko išsaugoti</h1><p>Patikrinkite įvestus laukus ir ar pakanka nesupakuoto kiekio.</p><a href="/">Grįžti</a>')
