
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
    labels={'/actions/item': '+ Pridėti daiktą', '/actions/category': '+ Pridėti kategoriją', '/actions/case': '+ Naujas case’as', '/actions/show': '+ Nauja išvyka', '/actions/vehicle': '+ Pridėti automobilį'}
    def fold(m):
        label=labels.get(m.group(1))
        return '<details class="panel"><summary>'+label+'</summary>'+m.group(0)+'</details>' if label else m.group(0)
    body=re.sub(r'<form method="post" action="([^"]+)">.*?</form>',fold,body,flags=re.S)
    return HTMLResponse('<!doctype html><html lang="lt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VF · Audio sandėlys</title><style>*{box-sizing:border-box}body{margin:0;background:#f4f6fa;color:#18243a;font:16px/1.55 system-ui,-apple-system,sans-serif}header{background:white;border-bottom:1px solid #dde4ef}.header,main{max-width:1040px;margin:auto;padding:20px 24px}.brand{font-weight:800;font-size:22px;margin:0 0 14px}nav{display:flex;gap:8px;flex-wrap:wrap}a{color:#2856d9;text-decoration:none}a:hover{text-decoration:underline}nav a{padding:9px 13px;border-radius:9px;font-size:14px}nav a[aria-current=page]{background:#e9efff;font-weight:750}main{padding-top:28px;padding-bottom:110px}h1{font-size:32px;line-height:1.2;letter-spacing:-.8px}h2{font-size:20px;margin:8px 0}h3{font-size:17px;margin:8px 0}section,details.panel{background:white;border:1px solid #dde4ef;border-radius:14px;padding:20px;margin:14px 0}small,.muted{color:#64738b}p{margin:9px 0}summary{cursor:pointer;font-weight:650;color:#2856d9;padding:6px 0}details[open]>summary{margin-bottom:10px}form{margin:10px 0}input,select,button,.button{font:inherit;max-width:100%;min-height:46px;border-radius:9px}input,select{display:block;width:100%;border:1px solid #bac7dc;background:white;color:#18243a;padding:10px 12px;margin:5px 0 14px}input[type=hidden]{display:none}input[type=checkbox]{display:inline-block;width:22px;min-height:22px;height:22px;margin:0;flex:none;accent-color:#2856d9}button,.button{display:inline-block;padding:10px 16px;border:0;background:#2856d9;color:white;font-weight:650;cursor:pointer}.secondary{background:#eaf0fb;color:#254676}.danger{background:#fff0ed;color:#9b3828}label{display:block;font-size:14px;font-weight:600;margin:10px 0 4px}.row{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.inline{display:flex;align-items:end;gap:10px;flex-wrap:wrap}.inline label{flex:1;min-width:170px}.inline select{margin-bottom:0}.check{display:flex;align-items:center;gap:14px;padding:12px;background:#f5f7fc;border-radius:9px}.check span{flex:1}.check small{display:block}.notice,.success,.error{padding:12px 16px;border-radius:9px;font-size:14px;margin:12px 0}.notice{background:#edf2fb;color:#47617f}.success{background:#e4f5e9;color:#245938}.error{background:#fff0ed;color:#9b3828}.stats{display:flex;gap:10px;margin:20px 0}.stat{flex:1;background:white;border:1px solid #dde4ef;border-radius:11px;padding:12px;font-size:12px;color:#64738b}.stat strong{display:block;font-size:25px;color:#18243a}.empty{padding:22px;border:1px dashed #b6c3d6;border-radius:12px;color:#64738b}.tools{margin:20px 0}.back{display:inline-block;margin-bottom:12px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:10px 4px;border-bottom:1px solid #e2e7f0}th{color:#64738b}.table-wrap{overflow-x:auto}button:focus-visible,a:focus-visible,input:focus,select:focus,summary:focus-visible{outline:3px solid #9eb9ff;outline-offset:2px}[hidden]{display:none!important}@media(max-width:600px){.header,main{padding-left:16px;padding-right:16px}nav{position:fixed;bottom:0;left:0;right:0;z-index:20;justify-content:space-around;flex-wrap:nowrap;gap:0;background:white;border-top:1px solid #dde4ef;padding:8px 3px calc(8px + env(safe-area-inset-bottom))}nav a{font-size:11px;padding:11px 6px}h1{font-size:27px}section,details.panel{padding:16px}.inline{align-items:stretch}.inline label{flex-basis:100%}.inline button{width:100%}}</style></head><body><header><div class="header"><div class="brand">VF · Audio sandėlys</div><nav aria-label="Pagrindinis meniu"><a href="/">Apžvalga</a><a href="/shows">Išvykos</a><a href="/cases">Case’ai</a><a href="/items">Inventorius</a><a href="/vehicles">Automobiliai</a></nav></div></header><main>' + body + '</main>' + "<script>(()=>{const p=location.pathname;document.querySelectorAll('nav a').forEach(a=>{const h=a.getAttribute('href');if(h===p||(h!=='/'&&p.startsWith(h+'/')))a.setAttribute('aria-current','page')});if(p==='/login')document.querySelector('nav').hidden=true;\nconst labels={name:'Pavadinimas',category_id:'Kategorija',qty:'Kiekis, vnt.',city:'Miestas',date_out:'Išvykimo data',password:'Slaptažodis',item_id:'Daiktas'};document.querySelectorAll('form input:not([type=hidden]):not([type=checkbox]),form select').forEach((el,i)=>{if(el.closest('label')||el.previousElementSibling?.tagName==='LABEL'||!labels[el.name])return;const l=document.createElement('label');el.id=el.id||'field-'+i;l.htmlFor=el.id;l.textContent=labels[el.name];el.before(l)});\nif(['/items','/shows','/cases','/vehicles'].includes(p)){const main=document.querySelector('main'),cards=[...main.querySelectorAll(':scope > section')];if(cards.length){const bar=document.createElement('div');bar.className='tools';const input=document.createElement('input');input.type='search';input.placeholder='Ieškoti šiame sąraše…';input.setAttribute('aria-label','Ieškoti sąraše');bar.append(input);let filter;if(p==='/items'){filter=document.createElement('select');filter.setAttribute('aria-label','Kategorija');filter.add(new Option('Visos kategorijos',''));[...new Set(cards.map(s=>s.querySelector('small')?.textContent).filter(Boolean))].forEach(v=>filter.add(new Option(v,v)));bar.append(filter)}main.querySelector('h1')?.after(bar);const msg=document.createElement('p');msg.textContent='Nieko nerasta.';msg.hidden=true;main.append(msg);function update(){let n=0;cards.forEach(c=>{const show=c.textContent.toLocaleLowerCase('lt').includes(input.value.toLocaleLowerCase('lt'))&&(!filter?.value||c.querySelector('small')?.textContent===filter.value);c.hidden=!show;if(show)n++});msg.hidden=n>0}input.addEventListener('input',update);filter?.addEventListener('change',update)}}\ndocument.querySelectorAll('[data-case-picker]').forEach(f=>{const input=f.querySelector('[data-picker-search]'),rows=[...f.querySelectorAll('[data-picker-row]')],count=f.querySelector('[data-selection-count]');function update(){let n=0;rows.forEach(r=>{r.hidden=!r.textContent.toLocaleLowerCase('lt').includes(input.value.toLocaleLowerCase('lt'));if(r.querySelector('input').checked)n++});count.textContent='Pasirinkta: '+n}input.addEventListener('input',update);f.addEventListener('change',update);update()});\ndocument.querySelectorAll('[data-confirm]').forEach(f=>f.addEventListener('submit',e=>{if(!confirm(f.dataset.confirm))e.preventDefault()}));})();</script>" + '</body></html>')

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
    for r in rows: body+='<section><small>'+esc(r['category'])+'</small><h2>'+esc(r['name'])+'</h2>Iš viso: '+str(r['qty'])+' · Dėžėse: '+str(r['packed'])+' · Nesupakuota: '+str(r['qty']-r['packed'])+'</section>'
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
    with connect() as c:
        rows=c.execute('SELECT s.*, (SELECT COUNT(*) FROM cases cs WHERE cs.show_id=s.id) AS case_count FROM shows s ORDER BY date_out DESC').fetchall()
    body='<h1>Išvykos</h1>'+form_open(request,'/actions/show')+'<input name="name" required maxlength="200"><input name="city" required maxlength="200"><input type="date" name="date_out" required><button>Sukurti išvyką</button></form>'
    for s in rows:
        body+='<section><div class="row"><h2><a href="/shows/'+str(s['id'])+'">'+esc(s['name'])+'</a></h2><a class="button" href="/shows/'+str(s['id'])+'">Valdyti išvyką</a></div><p>'+esc(s['city'])+' · '+esc(s['date_out'])+'</p><small>Case’ų: '+str(s['case_count'])+'</small></section>'
    if not rows: body+='<p class="empty">Išvykų dar nėra. Sukurkite pirmą išvyką.</p>'
    return shell(body)

def trip_form(request,s):
    return form_open(request,f"/shows/{s['id']}/manage")+'<input type="hidden" name="op" value="edit"><label for="trip-name">Pavadinimas</label><input id="trip-name" name="name" value="'+esc(s['name'])+'" maxlength="200" required><label for="trip-city">Miestas</label><input id="trip-city" name="city" value="'+esc(s['city'])+'" maxlength="200" required><label for="trip-date">Išvykimo data</label><input id="trip-date" type="date" name="date_out" value="'+esc(s['date_out'])+'" required><button>Išsaugoti išvyką</button></form>'

def trip_error(show_id,message,status=400,extra=''):
    r=shell('<h1>Pakeitimai neišsaugoti</h1><p class="error" role="alert">'+esc(message)+'</p>'+extra+'<p><a class="button secondary" href="/shows/'+str(show_id)+'">Grįžti į išvyką</a></p>')
    r.status_code=status
    return r

@app.get('/shows/{show_id}')
def show_detail(request: Request,show_id:int):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c:
        show=c.execute('SELECT * FROM shows WHERE id=%s',(show_id,)).fetchone()
        if not show:return trip_error(show_id,'Išvyka nerasta.',404)
        cases=c.execute('SELECT cs.*,v.name AS vehicle_name FROM cases cs LEFT JOIN vehicles v ON v.id=cs.vehicle_id WHERE cs.show_id=%s ORDER BY v.name,cs.name',(show_id,)).fetchall()
        available=c.execute('SELECT cs.*,COALESCE((SELECT SUM(qty) FROM contents WHERE case_id=cs.id),0) AS item_count FROM cases cs WHERE cs.show_id IS NULL ORDER BY cs.name').fetchall()
        busy=c.execute('SELECT cs.id,cs.name,s.name AS show_name FROM cases cs JOIN shows s ON s.id=cs.show_id WHERE cs.show_id<>%s ORDER BY cs.name',(show_id,)).fetchall()
        vehicles=c.execute('SELECT * FROM vehicles ORDER BY name').fetchall()
        contents=c.execute('SELECT ct.case_id,ct.item_id,ct.qty,i.name,cat.name AS category FROM contents ct JOIN cases cs ON cs.id=ct.case_id JOIN items i ON i.id=ct.item_id LEFT JOIN categories cat ON cat.id=i.category_id WHERE cs.show_id=%s ORDER BY i.name',(show_id,)).fetchall()
    by_case={};totals={}
    for r in contents:
        by_case.setdefault(r['case_id'],[]).append(r)
        if r['item_id'] not in totals: totals[r['item_id']]={'name':r['name'],'qty':0,'category':r['category']}
        totals[r['item_id']]['qty']+=r['qty']
    body='<a class="back" href="/shows">← Visos išvykos</a><h1>'+esc(show['name'])+'</h1><p class="muted">'+esc(show['city'])+' · '+esc(show['date_out'])+'</p>'
    notices={'edit':'Išvyka atnaujinta.','add':'Pasirinkti case’ai pridėti.','vehicle':'Automobilis pakeistas.','remove':'Case’as pašalintas iš išvykos. Jo turinys nepakeistas.'}
    notice=notices.get(request.query_params.get('done',''))
    if notice:body+='<p class="success" role="status">'+notice+'</p>'
    missing=sum(1 for cs in cases if cs['vehicle_id'] is None)
    body+='<div class="stats"><div class="stat"><strong>'+str(len(cases))+'</strong>Case’ų</div><div class="stat"><strong>'+str(len({cs['vehicle_id'] for cs in cases if cs['vehicle_id'] is not None}))+'</strong>Automobilių</div><div class="stat"><strong>'+str(missing)+'</strong>Be automobilio</div></div>'
    if missing:body+='<p class="notice">Kitas veiksmas: priskirkite automobilius '+str(missing)+' case’ams.</p>'
    body+='<details class="panel"><summary>Redaguoti išvykos informaciją</summary>'+trip_form(request,show)+'</details>'
    body+='<details class="panel" id="add-cases"><summary>+ Pridėti case’us į išvyką</summary>'
    if available:
        body+='<form method="post" action="/shows/'+str(show_id)+'/manage" data-case-picker>'+token(request)+'<input type="hidden" name="op" value="add"><input type="search" data-picker-search placeholder="Ieškoti laisvo case’o…" aria-label="Ieškoti case’o">'
        for cs in available:
            body+='<label class="check" data-picker-row><input type="checkbox" name="case_ids" value="'+str(cs['id'])+'"><span>'+esc(cs['name'])+'<small>Nepriskirtas išvykai · '+str(cs['item_count'])+' vnt.</small></span></label>'
        body+='<label>Automobilis pasirinktiems case’ams (nebūtina)<select name="vehicle_id"><option value="">Pasirinksiu vėliau</option>'+options(vehicles)+'</select></label><p class="muted" data-selection-count>Pasirinkta: 0</p><button>Pridėti pasirinktus case’us</button></form>'
    else: body+='<p class="empty">Laisvų case’ų nėra. Sukurkite naują arba atkabinkite case’ą nuo kitos išvykos.</p>'
    if busy:
        body+='<details><summary>Kitoms išvykoms priskirti case’ai ('+str(len(busy))+')</summary>'
        for cs in busy:body+='<p>'+esc(cs['name'])+' · '+esc(cs['show_name'])+'</p>'
        body+='</details>'
    body+='</details><h2>Case’ai ir automobiliai</h2><p class="muted">Tai pakrovimo planas, ne fizinio pakrovimo ar grąžinimo patvirtinimas.</p>'
    if not cases:body+='<p class="empty">Pridėkite case’us naudodami „+ Pridėti case’us į išvyką“ aukščiau.</p>'
    current=object()
    for cs in cases:
        if current!=cs['vehicle_id']:
            body+='<h3>'+esc(cs['vehicle_name'] or 'Automobilis nepriskirtas')+'</h3>';current=cs['vehicle_id']
        rows=by_case.get(cs['id'],[])
        body+='<section><div class="row"><h2>'+esc(cs['name'])+'</h2><small>'+str(sum(r['qty'] for r in rows))+' vnt.</small></div>'
        body+='<details><summary>Peržiūrėti turinį ('+str(len(rows))+' eilučių)</summary>'
        if rows:
            body+='<div class="table-wrap"><table><thead><tr><th>Daiktas</th><th>Kiekis</th></tr></thead><tbody>'
            for r in rows:body+='<tr><td>'+esc(r['name'])+'</td><td>'+str(r['qty'])+'</td></tr>'
            body+='</tbody></table></div>'
        else: body+='<p class="notice">Case’as tuščias.</p>'
        body+='<p><a href="/cases/'+str(cs['id'])+'">Redaguoti case’o turinį →</a></p></details>'
        body+=form_open(request,f'/shows/{show_id}/manage')+'<input type="hidden" name="op" value="vehicle"><input type="hidden" name="case_id" value="'+str(cs['id'])+'"><div class="inline"><label>Automobilis<select name="vehicle_id"><option value="">Nepriskirtas</option>'+options(vehicles,cs['vehicle_id'])+'</select></label><button>Išsaugoti automobilį</button></div></form>'
        body+='<form method="post" action="/shows/'+str(show_id)+'/manage" data-confirm="Pašalinti case’ą iš šios išvykos? Case’as ir jo turinys nebus ištrinti.">'+token(request)+'<input type="hidden" name="op" value="remove"><input type="hidden" name="case_id" value="'+str(cs['id'])+'"><button class="danger">Pašalinti iš išvykos</button></form></section>'
    body+='<details class="panel"><summary>Bendras išvykos įrangos sąrašas ('+str(len(totals))+' eilučių)</summary>'
    if totals:
        body+='<div class="table-wrap"><table><thead><tr><th>Daiktas</th><th>Kategorija</th><th>Kiekis</th></tr></thead><tbody>'
        for r in sorted(totals.values(),key=lambda x:x['name'].lower()):body+='<tr><td>'+esc(r['name'])+'</td><td>'+esc(r['category'])+'</td><td>'+str(r['qty'])+'</td></tr>'
        body+='</tbody></table></div>'
    else:body+='<p>Priskirtuose case’uose nėra daiktų.</p>'
    body+='</details><p class="notice">Sąrašas rodo dabartinį case’ų turinį. Ši versija dar nefiksuoja istorinio išvežimo sąrašo. Kitų žmonių pakeitimus matysite perkrovę puslapį.</p>'
    return shell(body)

@app.post('/shows/{show_id}/manage')
async def manage_show(request: Request,show_id:int):
    if not request.session.get('ok'):return redirect('/login')
    f=await request.form()
    expected=str(request.session.get('csrf',''))
    if not expected or not hmac.compare_digest(str(f.get('csrf','')),expected):return trip_error(show_id,'Forma paseno. Perkraukite puslapį.',403)
    op=str(f.get('op',''))
    try:
        with connect() as c:
            show=c.execute('SELECT * FROM shows WHERE id=%s FOR UPDATE',(show_id,)).fetchone()
            if not show:return trip_error(show_id,'Išvyka nerasta.',404)
            if op=='edit':
                from datetime import date
                name=str(f.get('name','')).strip();city=str(f.get('city','')).strip();raw=str(f.get('date_out','')).strip()
                values={'id':show_id,'name':name,'city':city,'date_out':raw}
                try:out=date.fromisoformat(raw).isoformat()
                except ValueError:return trip_error(show_id,'Įveskite galiojančią išvykimo datą.',extra=trip_form(request,values))
                if not name or not city or len(name)>200 or len(city)>200:return trip_error(show_id,'Pavadinimas ir miestas privalomi, iki 200 simbolių.',extra=trip_form(request,values))
                c.execute('UPDATE shows SET name=%s,city=%s,date_out=%s WHERE id=%s',(name,city,out,show_id))
            elif op in ('add','vehicle','remove'):
                vehicle_id=int(f['vehicle_id']) if f.get('vehicle_id') else None
                if vehicle_id is not None and not c.execute('SELECT id FROM vehicles WHERE id=%s',(vehicle_id,)).fetchone():return trip_error(show_id,'Automobilis nerastas.')
                if op=='add':
                    ids=sorted(set(int(x) for x in f.getlist('case_ids')))
                    if not ids:return trip_error(show_id,'Pasirinkite bent vieną case’ą.')
                    # Lock and validate the entire selection before changing any assignment.
                    selected=c.execute('SELECT id,show_id FROM cases WHERE id=ANY(%s) ORDER BY id FOR UPDATE',(ids,)).fetchall()
                    if len(selected)!=len(ids):return trip_error(show_id,'Vienas iš pasirinktų case’ų nebeegzistuoja. Perkraukite puslapį.')
                    if any(r['show_id'] is not None and r['show_id']!=show_id for r in selected):return trip_error(show_id,'Vieną iš pasirinktų case’ų jau priskyrė kitai išvykai. Nieko nepridėta. Perkraukite puslapį.',409)
                    c.execute('UPDATE cases SET show_id=%s,vehicle_id=%s WHERE id=ANY(%s) AND show_id IS NULL',(show_id,vehicle_id,ids))
                else:
                    cid=int(f['case_id'])
                    cs=c.execute('SELECT id,show_id FROM cases WHERE id=%s FOR UPDATE',(cid,)).fetchone()
                    if not cs or cs['show_id']!=show_id:return trip_error(show_id,'Case’as nebepriklauso šiai išvykai. Perkraukite puslapį.',409)
                    if op=='vehicle':c.execute('UPDATE cases SET vehicle_id=%s WHERE id=%s',(vehicle_id,cid))
                    else:c.execute('UPDATE cases SET show_id=NULL,vehicle_id=NULL WHERE id=%s',(cid,))
            else:return trip_error(show_id,'Nežinomas veiksmas.')
        return redirect(f'/shows/{show_id}?done={op}')
    except (ValueError,KeyError):return trip_error(show_id,'Patikrinkite pasirinktus laukus ir bandykite dar kartą.')

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
    if not request.session.get('csrf') or not hmac.compare_digest(str(f.get('csrf','')),str(request.session.get('csrf',''))):
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
                cs=c.execute('SELECT show_id FROM cases WHERE id=%s FOR UPDATE',(cid,)).fetchone()
                if not cs: raise ValueError('Case’as nerastas.')
                if sid is not None and cs['show_id'] is not None and cs['show_id']!=sid:
                    return shell('<h1>Case’as jau priskirtas kitai išvykai</h1><p>Pirmiausia atkabinkite jį nuo ankstesnės išvykos. Keitimai neišsaugoti.</p><a href="/cases">Grįžti</a>')
                c.execute('UPDATE cases SET show_id=%s,vehicle_id=%s WHERE id=%s',(sid,vid,cid)); target=f'/cases/{cid}'
            else: return HTMLResponse('Nežinomas veiksmas',status_code=404)
        return redirect(target)
    except (ValueError,KeyError):
        return shell('<h1>Nepavyko išsaugoti</h1><p>Patikrinkite įvestus laukus ir ar pakanka nesupakuoto kiekio.</p><a href="/">Grįžti</a>')
