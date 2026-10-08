"""Read-only loopback trace viewer. No inference or credentials are required."""
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from token_usage import trace_directory


def load_sessions(directory):
    sessions = {}
    skipped = 0
    for path in sorted(Path(directory).glob("*.jsonl")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        event = json.loads(line)
                        if not isinstance(event, dict):
                            raise ValueError()
                        sid, number = event.get("session_id"), event.get("request")
                        if not isinstance(sid, str):
                            raise ValueError()
                        session = sessions.setdefault(sid, {"id": sid, "project": event.get("project", "Unknown project"), "started": event.get("timestamp", ""), "calls": {}, "events": [], "status": "unknown"})
                        if event.get("event") not in ("started", "finished", None):
                            session["events"].append(event)
                            if event.get("event") in ("session_started", "session_ended"):
                                session["status"] = event.get("status", "unknown")
                            continue
                        if type(number) is not int:
                            raise ValueError()
                        old = session["calls"].get(number, {})
                        session["calls"][number] = {**old, **event}
                    except (ValueError, TypeError):
                        skipped += 1
        except (OSError, UnicodeError):
            skipped += 1
    result = []
    for session in sessions.values():
        session["calls"] = sorted(session["calls"].values(), key=lambda call: call["request"])
        result.append(session)
    return {"sessions": sorted(result, key=lambda s: s["started"], reverse=True), "skipped": skipped}


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Karyo · Trace viewer</title>
<style>
:root{color-scheme:dark;font-family:Inter,ui-sans-serif,system-ui;background:#101216;color:#e8ebf0}*{box-sizing:border-box}body{margin:0}header{height:78px;border-bottom:1px solid #2b3039;display:flex;align-items:center;justify-content:space-between;padding:0 28px}h1{font-size:22px;letter-spacing:-1px;margin:0}h1 span{font-weight:400;color:#8e98a8;margin-left:14px;letter-spacing:0;font-size:14px}.live{font-size:12px;color:#b9e39b}main{display:grid;grid-template-columns:250px 260px minmax(0,1fr);height:calc(100vh - 78px)}aside,nav{border-right:1px solid #2b3039;padding:20px 12px;overflow:auto}h2{font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:#8e98a8;margin:4px 10px 18px}button{font:inherit;color:inherit;background:none;border:1px solid transparent;cursor:pointer}button.item{display:block;width:100%;text-align:left;border-radius:10px;padding:14px;margin-bottom:7px;overflow-wrap:anywhere}.item:hover{background:#1b2028}.item.selected{background:#252d25;border-color:#698b48}.item strong{font-size:13px;display:block;margin-bottom:6px}.sub{font-size:11px;line-height:1.6;color:#939eae}.badge{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#b9e39b}.badge.error{color:#ff9d91}.badge.pending{color:#f1ce88}article{overflow:auto;padding:28px;min-width:0}#heading{font-size:24px;letter-spacing:-.6px;margin-bottom:8px}.metrics{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}.metric{padding:14px 20px;border:1px solid #2b3039;border-radius:10px;min-width:120px}.metric b{display:block;font-size:21px;margin-top:5px}.tabs{display:flex;gap:8px;border-bottom:1px solid #2b3039;margin-bottom:22px}.tabs button{padding:12px;color:#8e98a8}.tabs button.active{color:#d4efb0;border-bottom:2px solid #b7df86}.columns{display:grid;grid-template-columns:1fr 1fr;gap:20px}.panel{min-width:0}h3{font-size:13px;color:#b5beca}details{border:1px solid #303640;border-radius:9px;margin-bottom:12px;background:#171b21}summary{padding:13px;cursor:pointer;font-size:12px;color:#c9d2de}pre{font:12px/1.7 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0;padding:16px;max-height:500px;overflow:auto;color:#d1d8e3}summary .new{color:#c5e997;margin-left:8px}.empty{padding:40px 15px;color:#95a0b0;line-height:1.8}code{color:#c5e997}.note{font-size:12px;color:#9da7b5;line-height:1.7}#filter{width:100%;background:#191e25;border:1px solid #343c47;border-radius:8px;padding:9px;color:inherit;margin-bottom:14px}@media(max-width:1000px){main{grid-template-columns:190px 190px minmax(0,1fr)}.columns{grid-template-columns:1fr}article{padding:16px}}@media(max-width:650px){main{height:auto;display:block}aside,nav{max-height:230px;border-bottom:1px solid #2b3039}header{padding:15px}.columns{display:block}}
</style></head><body><header><h1>Karyo <span>Trace explorer</span></h1><div id="live" class="live">● Connecting</div></header>
<main><aside><h2>Sessions</h2><input id="filter" aria-label="Filter sessions" placeholder="Filter by project…"><div id="sessions"></div></aside><nav><h2>Model calls</h2><div id="calls"></div></nav><article><div id="detail"></div></article></main>
<script>
const $=id=>document.getElementById(id);let sessions=[],sid=null,rid=null,tab='messages',last='',selection='';
const text=(tag,value,cls)=>{const n=document.createElement(tag);n.textContent=value;if(cls)n.className=cls;return n};
const json=x=>JSON.stringify(x,null,2);const num=x=>Number.isInteger(x)?x.toLocaleString():'Unknown';
function item(parent,title,sub,selected,click){const b=text('button','',`item ${selected?'selected':''}`);b.append(text('strong',title),text('div',sub,'sub'));b.onclick=click;parent.append(b);return b}
function lists(){const filtered=sessions.filter(s=>(s.project+' '+s.id).toLowerCase().includes($('filter').value.toLowerCase()));$('sessions').replaceChildren();for(const s of filtered)item($('sessions'),s.project.split('/').filter(Boolean).pop()||s.project,`${s.started ? new Date(s.started).toLocaleString():''} · ${s.calls.length} calls`,sid===s.id,()=>{sid=s.id;rid='session';selection='';render()});if(!filtered.length)$('sessions').append(text('div','No sessions found.','empty'));const s=sessions.find(s=>s.id===sid);$('calls').replaceChildren();if(!s)return;item($('calls'),'Conversation',`${(s.events||[]).length} events · ${s.status}`,rid==='session',()=>{rid='session';selection='';render()});for(const c of s.calls){const b=item($('calls'),`Call ${c.request}`,`In ${num(c.input_tokens)} · Out ${num(c.output_tokens)}`,rid===c.request,()=>{rid=c.request;selection='';render()});b.append(text('span',c.status,'badge '+c.status))}}
function box(parent,label,value,open=false,isNew=false){const d=document.createElement('details');d.open=open;const title=text('summary',label);if(isNew)title.append(text('span','NEW','new'));d.append(title,text('pre',typeof value==='string'?value:json(value)));parent.append(d)}
function render(){if(!sid&&sessions.length)sid=sessions[0].id;const s=sessions.find(s=>s.id===sid);if(s&&rid!=='session'&&!s.calls.some(c=>c.request===rid))rid='session';lists();const c=s?.calls.find(c=>c.request===rid);const key=json([sid,rid,tab,c,rid==='session'?s:null]);if(key===selection)return;selection=key;const root=$('detail');root.replaceChildren();if(s&&rid==='session'){root.append(text('h1','Session conversation'),text('p',`${s.project} · ${s.status}`,'note'));for(const e of s.events||[]){const label=`${e.timestamp ? new Date(e.timestamp).toLocaleTimeString():''} · Turn ${e.turn||0} · ${e.event.replaceAll('_',' ')}`;box(root,label,e.content??e.message??e.tool_call??e.result??e,true)}if(!(s.events||[]).length)root.append(text('p','Older session: select a model call to inspect its messages.','note'));return}if(!c){root.append(text('h2','Your model calls, made visible'),text('div','Start a traced session in another terminal:','empty'),text('pre','uv run karyo'),text('p','This viewer refreshes every second. Existing traces can be opened with --directory.','note'));return}root.append(text('div',`Call ${c.request}`,'heading'));root.firstChild.id='heading';root.append(text('div',s.project,'sub'));const metrics=text('div','','metrics');for(const [label,value] of [['Input tokens',num(c.input_tokens)],['Output tokens',num(c.output_tokens)],['Total tokens',num(c.total_tokens)],['Duration',c.elapsed_ms===undefined?'Pending':`${(c.elapsed_ms/1000).toFixed(2)} s`]]){const m=text('div',label,'metric sub');m.append(text('b',value));metrics.append(m)}root.append(metrics);const tabs=text('div','','tabs');for(const [id,label] of [['messages','Input / Output'],['raw','Raw JSON']]){const b=text('button',label,tab===id?'active':'');b.onclick=()=>{tab=id;render()};tabs.append(b)}root.append(tabs);if(tab==='raw'){box(root,'Complete call record',c,true);return}if(c.status==='pending')root.append(text('p','Awaiting completion. If the agent stopped, this call may remain pending.','note'));const columns=text('div','','columns'),input=text('div','','panel'),output=text('div','','panel');input.append(text('h3','INPUT'));output.append(text('h3','OUTPUT'));columns.append(input,output);root.append(columns);if(!c.input)input.append(text('p','Content not captured. Start Karyo with --trace-content.','note'));else{input.append(text('p',c.input.model||'Model unspecified','note'));const previous=s.calls.filter(x=>x.request<c.request).at(-1);const old=previous?.input?.messages||[];const msgs=c.input.messages||[];let prefix=0;while(prefix<old.length&&prefix<msgs.length&&json(old[prefix])===json(msgs[prefix]))prefix++;msgs.forEach((m,i)=>box(input,`${i+1} · ${m.role||'message'}`,m,i>=prefix,i>=prefix));box(input,'Tool definitions',c.input.tools||[])}if(c.output){for(const choice of c.output.choices||[])box(output,'Assistant response',choice.message,true);if(!(c.output.choices||[]).length)box(output,'Response',c.output,true)}else output.append(text('p',c.status==='error'?'Request failed; no response captured.':'No output captured yet.','note'))}
async function poll(){try{const res=await fetch('api/sessions',{cache:'no-store'});if(!res.ok)throw Error();const data=await res.json();$('live').textContent=`● Live · ${data.sessions.length} sessions${data.skipped?' · '+data.skipped+' unreadable records':''}`;const next=json(data);if(next!==last){last=next;sessions=data.sessions;render()}}catch{$('live').textContent='● Disconnected · retrying'}finally{setTimeout(poll,1000)}}$('filter').oninput=lists;render();poll();
</script></body></html>'''


def make_server(directory, port=0):
    directory = Path(directory).expanduser().resolve()
    secret = secrets.token_urlsafe(32)
    prefix = '/' + secret + '/'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            host = f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host') != host or self.path not in (prefix, prefix + 'api/sessions'):
                self.send_error(404)
                return
            if self.path == prefix:
                data, mime = PAGE.encode(), 'text/html; charset=utf-8'
            else:
                data, mime = json.dumps(load_sessions(directory)).encode(), 'application/json'
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    return server, f'http://127.0.0.1:{server.server_port}{prefix}'


def serve(directory=None, port=0, open_browser=True):
    directory = Path(directory).expanduser() if directory else trace_directory()
    server, url = make_server(directory, port)
    print(f'Traces: {directory}\nViewer: {url}\nPress Ctrl+C to stop.', flush=True)
    if open_browser:
        webbrowser.open(url)
    with server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nTrace viewer stopped.')
