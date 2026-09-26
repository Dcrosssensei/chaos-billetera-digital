import os,json,csv,collections,matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
M=json.load(open('results/metrics.json'))
os.makedirs('results/fig',exist_ok=True)
C={'monolitico':'#eb6834','resiliente':'#2a78d6'}; LBL={'monolitico':'Arquitectura monolítica (1 nodo)','resiliente':'Arquitectura resiliente (2 nodos + failover)'}
INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'axes.edgecolor':INK2,'axes.labelcolor':INK,'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False})
def load(tag):
    return [dict(t=float(r['t']),op=r['op'],ok=r['status']=='200',lat=float(r['lat_ms']),deg=r['degradado']=='1') for r in csv.DictReader(open(f'results/{tag}.csv'))]
def per_sec(rows,f):
    b=collections.defaultdict(list)
    for x in rows: b[int(x['t'])].append(x)
    ks=sorted(k for k in b if k<45); return ks,[f(b[k]) for k in ks]
def shade(ax,tag,label=True):
    m=M[tag]; ax.axvspan(m['inj'],m['rb_start'],color='#d9d8d3',alpha=.5,lw=0)
    if label: ax.text((m['inj']+min(m['rb_start'],44))/2,1.02,'falla inyectada por Chaos Toolkit',transform=ax.get_xaxis_transform(),ha='center',fontsize=8.5,color=INK2)
# Fig 2: E1
fig,ax=plt.subplots(figsize=(7,3.6))
shade(ax,'monolitico_E1_caida_nodo')
for a in ['monolitico','resiliente']:
    ks,v=per_sec(load(f'{a}_E1_caida_nodo'),lambda s:100*sum(x['ok'] for x in s)/len(s))
    ax.plot(ks,v,color=C[a],lw=2,label=LBL[a],marker='o',ms=3)
ax.set_ylim(-5,108); ax.set_xlim(0,44); ax.set_xlabel('Tiempo del experimento (s)'); ax.set_ylabel('Operaciones exitosas (%)')
ax.grid(axis='y',color=GRID,lw=.8); ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2,fontsize=8.5)
fig.tight_layout(); fig.savefig('results/fig/fig2_e1.png',dpi=200); plt.close()
# Fig 3: E2 latency
fig,ax=plt.subplots(figsize=(7,3.6))
shade(ax,'resiliente_E2_latencia')
for a in ['monolitico','resiliente']:
    ks,v=per_sec(load(f'{a}_E2_latencia'),lambda s:sorted(x['lat'] for x in s)[int(.95*(len(s)-1))])
    ax.plot(ks,v,color=C[a],lw=2,label=LBL[a],marker='o',ms=3)
ax.set_yscale('log'); ax.set_xlim(0,44); ax.set_xlabel('Tiempo del experimento (s)'); ax.set_ylabel('Latencia p95 (ms, escala log)')
ax.axhline(1000,color=INK2,lw=.8,ls='--'); ax.text(25,1200,'umbral de la hipótesis: 1 s',fontsize=8,color=INK2)
ax.grid(axis='y',color=GRID,lw=.8); ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2,fontsize=8.5)
fig.tight_layout(); fig.savefig('results/fig/fig3_e2.png',dpi=200); plt.close()
# Fig 4: E3 resiliente por operación
fig,ax=plt.subplots(figsize=(7,3.6))
tag='resiliente_E3_caida_total'; rows=load(tag); shade(ax,tag)
for op,col,lab in [('saldo','#2a78d6','Consulta de saldo (servida desde caché = modo degradado)'),('transferir','#e34948','Transferencias')]:
    ks,v=per_sec([x for x in rows if x['op']==op],lambda s:100*sum(x['ok'] for x in s)/len(s))
    ax.plot(ks,v,color=col,lw=2,label=lab,marker='o',ms=3)
ax.set_ylim(-5,108); ax.set_xlim(0,44); ax.set_xlabel('Tiempo del experimento (s)'); ax.set_ylabel('Operaciones exitosas (%)')
ax.grid(axis='y',color=GRID,lw=.8); ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.22),ncol=2,fontsize=8.5)
fig.tight_layout(); fig.savefig('results/fig/fig4_e3.png',dpi=200); plt.close()
# Fig 5: resumen disponibilidad útil (<1s) durante la falla
def util(tag):
    r=load(tag); m=M[tag]; s=[x for x in r if m['inj']<=x['t']<m['rb_start']]
    return 100*sum(x['ok'] and x['lat']<1000 for x in s)/len(s)
exps=[('E1_caida_nodo','E1 · Caída de\nun servidor'),('E2_latencia','E2 · Latencia\nde 3 s'),('E3_caida_total','E3 · Caída de\ntodo el backend')]
fig,ax=plt.subplots(figsize=(7,3.7)); w=.36
for i,a in enumerate(['monolitico','resiliente']):
    vals=[util(f'{a}_{e}') for e,_ in exps]
    xs=[j+(i-.5)*w for j in range(3)]
    bars=ax.bar(xs,vals,w-.03,color=C[a],label=LBL[a])
    for x,v in zip(xs,vals): ax.text(x,v+2,f'{v:.0f} %',ha='center',fontsize=9,color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels([l for _,l in exps]); ax.set_ylim(0,115); ax.set_ylabel('Operaciones útiles (%)\n(éxito y < 1 s)')
ax.grid(axis='y',color=GRID,lw=.8); ax.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.2),ncol=2,fontsize=8.5); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig('results/fig/fig5_resumen.png',dpi=200); plt.close()
print({f'{a}_{e}':round(util(f'{a}_{e}'),1) for a in ['monolitico','resiliente'] for e,_ in exps})
# Fig 1: arquitectura
fig,axs=plt.subplots(1,2,figsize=(7.2,3.2))
def box(ax,x,y,w,h,t,fc):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.04',fc=fc,ec=INK2,lw=1)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=8.5)
def arr(ax,x1,y1,x2,y2,t=''):
    ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=INK2,lw=1.1))
    if t: ax.text((x1+x2)/2+.03,(y1+y2)/2,t,fontsize=7,color=INK2)
for ax,titulo in zip(axs,['(a) Monolítica — réplica del incidente','(b) Resiliente — propuesta']):
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off'); ax.set_title(titulo,fontsize=9.5)
    box(ax,.3,.84,.4,.12,'Usuarios\n(generador de carga)','#f3f2ee')
    arr(ax,.5,.84,.5,.70)
ax=axs[0]; box(ax,.25,.52,.5,.17,'API Gateway\n(sin timeout, sin reintentos)','#fbe3d8'); arr(ax,.5,.52,.5,.36)
box(ax,.28,.18,.44,.17,'Nodo core 9001\n(punto único de falla)','#fbe3d8')
ax=axs[1]; box(ax,.12,.50,.76,.20,'API Gateway\ntimeout 0,5 s · failover · circuit breaker\ncaché de saldo (degradación)','#dbe8f8')
arr(ax,.32,.50,.24,.36); arr(ax,.68,.50,.76,.36)
box(ax,.04,.18,.40,.17,'Nodo core 9001\n(primario)','#dbe8f8'); box(ax,.56,.18,.40,.17,'Nodo core 9002\n(réplica)','#dbe8f8')
fig.text(.5,.03,'Chaos Toolkit inyecta las fallas sobre los nodos core y mide la hipótesis a través del gateway.',ha='center',fontsize=7.8,color=INK2,wrap=True)
fig.tight_layout(rect=(0,.06,1,1)); fig.savefig('results/fig/fig1_arquitectura.png',dpi=200); plt.close()
