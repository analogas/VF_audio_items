
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
        return '<details><summary>'+label+'</summary>'+m.group(0)+'</details>' if label else m.group(0)
    body=re.sub(r'<form method="post" action="([^"]+)">.*?</form>',fold,body,flags=re.S)
    return HTMLResponse('<!doctype html><html lang="lt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>VF · Audio sandėlys</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f7fb;color:#17243b;font:16px/1.55 system-ui,sans-serif}header{background:white;border-bottom:1px solid #dce3ef;padding:20px max(16px,calc((100vw - 960px)/2))}.brand{font-size:22px;font-weight:800;margin-bottom:14px}nav{display:flex;gap:8px;flex-wrap:wrap}nav a{padding:9px 12px;background:#eef3ff;border-radius:9px;font-size:14px}main{max-width:960px;margin:auto;padding:28px 20px 100px}h1{font-size:32px;letter-spacing:-.7px;line-height:1.2}h2{font-size:20px}a{color:#2856db;text-decoration:none}a:hover{text-decoration:underline}section,details{background:white;border:1px solid #dce3ef;border-radius:14px;padding:20px;margin:14px 0}small,.muted{color:#617189}summary{cursor:pointer;color:#2856db;font-weight:650}input,select,button{font:inherit;min-height:46px;border-radius:9px;max-width:100%}input,select{display:block;width:100%;padding:11px 13px;border:1px solid #bdc9dc;background:white;color:#17243b;margin:6px 0 16px}input[type=hidden]{display:none}button,.button{display:inline-block;padding:11px 17px;background:#2856db;color:white;border:0;font-weight:650;cursor:pointer}.button{border-radius:9px}label{display:block;font-size:14px;font-weight:650;margin-top:12px}input:focus,select:focus,button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #a7bfff;outline-offset:2px}.notice{padding:12px 16px;border-left:3px solid #97afe0;background:#edf2fb}.success{background:#e3f5e9;color:#225b37;padding:12px;border-radius:9px}.error{background:#fff0ee;color:#9a2e22;padding:12px;border-radius:9px}.row{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}.tools{margin:18px 0}.metrics{display:flex;gap:10px;flex-wrap:wrap}.metric{background:#eef3fa;border-radius:9px;padding:10px 14px;flex:1}.metric strong{display:block;font-size:24px}.metric span{font-size:12px;color:#617189}.empty{padding:20px;color:#617189;border:1px dashed #bdc9dc;border-radius:10px}.back{display:inline-block;margin-bottom:12px}@media(max-width:600px){main{padding:22px 16px 110px}header{padding:16px}nav{position:fixed;bottom:0;left:0;right:0;z-index:20;justify-content:space-around;flex-wrap:nowrap;background:white;border-top:1px solid #dce3ef;padding:8px 4px calc(8px + env(safe-area-inset-bottom));gap:2px}nav a{background:white;font-size:11px;padding:10px 5px}section{padding:16px}h1{font-size:28px}}</style></head><body><header><div class="brand">VF · Audio sandėlys</div><nav aria-label="Pagrindinė navigacija"><a href="/">Apžvalga</a><a href="/items">Daiktai</a><a href="/cases">Case’ai</a><a href="/shows">Išvykos</a><a href="/vehicles">Automobiliai</a></nav></header><main>' + body + '</main>' + "<script>(()=>{const p=location.pathname;document.querySelectorAll('nav a').forEach(a=>{const h=a.getAttribute('href');if(h===p||(h!=='/'&&p.startsWith(h+'/'))){a.setAttribute('aria-current','page');a.style.background='#dce7ff';a.style.fontWeight='750'}});if(p==='/login')document.querySelector('nav').hidden=true;const main=document.querySelector('main');const cards=[...main.querySelectorAll(':scope > section')];if(['/items','/shows','/cases','/vehicles'].includes(p)&&cards.length){const box=document.createElement('div');box.className='tools';const search=document.createElement('input');search.type='search';search.placeholder='Ieškoti šiame sąraše…';search.setAttribute('aria-label','Paieška');box.append(search);let filter;if(p==='/items'){filter=document.createElement('select');filter.setAttribute('aria-label','Kategorija');filter.add(new Option('Visos kategorijos',''));[...new Set(cards.map(s=>s.querySelector('small')?.textContent).filter(Boolean))].forEach(v=>filter.add(new Option(v,v)));box.append(filter)}main.querySelector('h1')?.after(box);const msg=document.createElement('p');msg.textContent='Nieko nerasta.';msg.hidden=true;main.append(msg);const update=()=>{let count=0;cards.forEach(c=>{const show=c.textContent.toLocaleLowerCase('lt').includes(search.value.toLocaleLowerCase('lt'))&&(!filter?.value||c.querySelector('small')?.textContent===filter.value);c.hidden=!show;if(show)count++});msg.hidden=count!==0};search.addEventListener('input',update);filter?.addEventListener('change',update)}})();</script>" + '</body></html>')

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
    body='<h1>Išvykos</h1>'+form_open(request,'/actions/show')+'<label>Pavadinimas</label><input name="name" required maxlength="200"><label>Miestas</label><input name="city" required maxlength="200"><label>Išvykimo data</label><input type="date" name="date_out" required><button>Sukurti išvyką</button></form>'
    for s in rows:
        body+='<section><div class="row"><h2><a href="/shows/'+str(s['id'])+'">'+esc(s['name'])+'</a></h2><a class="button" href="/shows/'+str(s['id'])+'">Atidaryti</a></div><p>'+esc(s['city'])+' · '+esc(s['date_out'])+'</p><small>Priskirta case’ų: '+str(s['case_count'])+'</small></section>'
    if not rows: body+='<p class="empty">Išvykų dar nėra. Sukurkite pirmą išvyką.</p>'
    return shell(body)

@app.get('/shows/{show_id}')
def show_detail(request: Request, show_id: int):
    if not request.session.get('ok'): return redirect('/login')
    with connect() as c:
        show=c.execute('SELECT * FROM shows WHERE id=%s',(show_id,)).fetchone()
        if not show: return HTMLResponse('Išvyka nerasta. <a href="/shows">Visos išvykos</a>',status_code=404)
        cases=c.execute('SELECT cs.*,v.name AS vehicle_name,COALESCE((SELECT SUM(qty) FROM contents WHERE case_id=cs.id),0) AS item_count FROM cases cs LEFT JOIN vehicles v ON v.id=cs.vehicle_id WHERE cs.show_id=%s ORDER BY v.name,cs.name',(show_id,)).fetchall()
    body='<a class="back" href="/shows">← Visos išvykos</a><h1>'+esc(show['name'])+'</h1><p class="muted">'+esc(show['city'])+' · '+esc(show['date_out'])+'</p>'
    if request.query_params.get('saved')=='1': body+='<p class="success" role="status">Išvykos pakeitimai išsaugoti.</p>'
    body+='<details><summary>Redaguoti išvyką</summary>'+show_edit_form(request,show)+'</details>'
    body+='<h2>Priskirti case’ai ('+str(len(cases))+')</h2><p class="muted">Automobilio priskyrimas yra planas, ne fizinio pakrovimo patvirtinimas.</p>'
    group=None
    for cs in cases:
        vehicle=cs['vehicle_name'] or 'Automobilis nepriskirtas'
        if group!=vehicle: body+='<h2>'+esc(vehicle)+'</h2>';group=vehicle
        body+='<section><div class="row"><h2>'+esc(cs['name'])+'</h2><a class="button" href="/cases/'+str(cs['id'])+'">Turinys ir priskyrimas</a></div><small>Turinys: '+str(cs['item_count'])+' vnt.</small></section>'
    if not cases: body+='<p class="empty">Šiai išvykai dar nepriskirtas nė vienas case’as.</p>'
    body+='<p><a class="button" href="/cases">Pasirinkti case’us</a></p><p class="muted">Atidarykite case’ą ir skiltyje „Priskyrimas“ pasirinkite šią išvyką bei automobilį. Norėdami atkabinti case’ą, pasirinkite „Sandėlyje“.</p>'
    return shell(body)

def show_edit_form(request, show):
    return form_open(request,'/shows/'+str(show['id'])+'/edit')+'<label for="show-name">Pavadinimas</label><input id="show-name" name="name" maxlength="200" value="'+esc(show['name'])+'" required><label for="show-city">Miestas</label><input id="show-city" name="city" maxlength="200" value="'+esc(show['city'])+'" required><label for="show-date">Išvykimo data</label><input id="show-date" type="date" name="date_out" value="'+esc(show['date_out'])+'" required><button>Išsaugoti pakeitimus</button></form>'

@app.post('/shows/{show_id}/edit')
async def show_edit(request: Request, show_id: int):
    if not request.session.get('ok'): return redirect('/login')
    f=await request.form()
    expected=str(request.session.get('csrf',''))
    if not expected or not hmac.compare_digest(str(f.get('csrf','')),expected):
        return HTMLResponse('Neteisinga forma. Perkraukite išvykos puslapį ir bandykite dar kartą.',status_code=403)
    from datetime import date
    name=str(f.get('name','')).strip()
    city=str(f.get('city','')).strip()
    date_out=str(f.get('date_out','')).strip()
    valid=True
    try:
        date_out=date.fromisoformat(date_out).isoformat()
    except ValueError: valid=False
    if not name or not city or len(name)>200 or len(city)>200: valid=False
    with connect() as c:
        found=c.execute('SELECT id FROM shows WHERE id=%s',(show_id,)).fetchone()
        if not found: return HTMLResponse('Išvyka nerasta.',status_code=404)
        if valid:
            c.execute('UPDATE shows SET name=%s,city=%s,date_out=%s WHERE id=%s',(name,city,date_out,show_id))
    if not valid:
        body='<h1>Patikrinkite išvykos duomenis</h1><p class="error" role="alert">Pavadinimas ir miestas privalomi (iki 200 simbolių). Įveskite galiojančią išvykimo datą. Pakeitimai neišsaugoti.</p>'
        body+=show_edit_form(request,{'id':show_id,'name':name,'city':city,'date_out':date_out})+'<a href="/shows/'+str(show_id)+'">Atšaukti</a>'
        response=shell(body);response.status_code=400;return response
    return redirect('/shows/'+str(show_id)+'?saved=1')

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
