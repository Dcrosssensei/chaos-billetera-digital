import json,csv,glob,datetime as dt,statistics as st
out={}
for f in sorted(glob.glob('results/*.journal.json')):
    tag=f.split('/')[-1].replace('.journal.json',''); c=f.replace('.journal.json','.csv')
    t0=float(open(c+'.t0').read()); j=json.load(open(f))
    T=lambda s: dt.datetime.fromisoformat(s).timestamp()-t0
    inj=T(j['run'][0]['start']); rb_end=T(j['rollbacks'][-1]['end']) if j['rollbacks'] else None
    rb_start=T(j['rollbacks'][0]['start'])
    rows=[dict(t=float(r['t']),op=r['op'],ok=r['status']=='200',lat=float(r['lat_ms']),deg=r['degradado']=='1') for r in csv.DictReader(open(c))]
    def m(sel):
        if not sel: return {}
        lats=sorted(x['lat'] for x in sel)
        g=lambda op: [x for x in sel if x['op']==op]
        av=lambda s: round(100*sum(x['ok'] for x in s)/len(s),1) if s else None
        return dict(n=len(sel), disp=av(sel), disp_saldo=av(g('saldo')), disp_transf=av(g('transferir')),
                    p50=round(st.median(lats)), p95=round(lats[int(.95*(len(lats)-1))]), deg=sum(x['deg'] for x in sel),
                    rps=round(len(sel)/max(1e-9,(max(x['t'] for x in sel)-min(x['t'] for x in sel))),1))
    pre=[x for x in rows if x['t']<inj]; dur=[x for x in rows if inj<=x['t']<rb_start]; post=[x for x in rows if x['t']>=rb_end]
    rec=next((x['t']-rb_start for x in rows if x['t']>=rb_start and x['ok'] and not x['deg'] and x['lat']<1000),None)
    out[tag]=dict(inj=round(inj,2),rb_start=round(rb_start,2),rb_end=round(rb_end,2),status=j['status'],deviated=j['deviated'],
        ssh_before=[p['output'] if not isinstance(p['output'],dict) else p['output']['status'] for p in j['steady_states']['before']['probes']],
        ssh_after=[p['output'] if not isinstance(p['output'],dict) else p['output']['status'] for p in j['steady_states']['after']['probes']],
        durante_probe=[r['output'] for r in j['run'] if r['activity']['type']=='probe'],
        pre=m(pre),dur=m(dur),post=m(post),recuperacion_s=round(rec,2) if rec is not None else None)
json.dump(out,open('results/metrics.json','w'),indent=1)
for k,v in out.items():
    print(k, v['status'],'dev',v['deviated'],'ssh',v['ssh_before'],'->',v['ssh_after'],'probe',v['durante_probe'],'rec',v['recuperacion_s'], 'win',v['inj'],v['rb_start'])
    for p in ['pre','dur','post']: print('   ',p,v[p])
