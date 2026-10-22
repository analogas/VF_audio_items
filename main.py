
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
    return HTMLResponse("""<!doctype html><html lang="lt"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Audio sandėlys</title><style>body{font:17px system-ui;background:#151518;color:#eee;max-width:800px;margin:auto;padding:16px}a{color:#ffc258}nav{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:24px}section{background:#242429;padding:16px;border-radius:12px;margin:14px 0}input,select,button{font:inherit;padding:12px;box-sizing:border-box;max-width:100%;margin:5px 0}input,select{display:block;width:100%}button{background:#ffc258;border:0;border-radius:6px}small{color:#bbb}h2{font-size:21px}</style><nav><a href="/">Apžvalga</a><a href="/items">Daiktai</a><a href="/cases">Case'ai</a><a href="/shows">Šou</a><a href="/vehicles">Mašinos</a></nav>""" + body + '</html>')

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
