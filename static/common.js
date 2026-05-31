const $=(s,e=document)=>e.querySelector(s);
async function api(u,o){const r=await fetch(u,o),j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.erro||`Algo correu mal (erro ${r.status}). Tenta novamente.`);return j}
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const I=d=>`<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
const ICON={
clip:I('<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'),
ext:I('<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'),
msg:I('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
send:I('<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>'),
up:I('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>'),
plus:I('<path d="M5 12h14"/><path d="M12 5v14"/>'),
x:I('<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'),
check:I('<path d="M20 6 9 17l-5-5"/>'),
coffee:I('<path d="M10 2v2"/><path d="M14 2v2"/><path d="M6 2v2"/><path d="M16 8a1 1 0 0 1 1 1v8a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V9a1 1 0 0 1 1-1h14a4 4 0 1 1 0 8h-1"/>')};
function copiar(b,txt){const ok=()=>{const h=b.innerHTML;b.innerHTML=ICON.check+'<span class="lbl">Copiado</span>';setTimeout(()=>b.innerHTML=h,1500)};
(navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(ok,()=>{const a=document.createElement("textarea");a.value=txt;document.body.append(a);a.select();try{document.execCommand("copy");ok()}catch{}a.remove()})}
const cfg=api("/api/config").catch(()=>({}));
const pronto=new Promise(r=>document.readyState!=="loading"?r():document.addEventListener("DOMContentLoaded",r));
const url=u=>/^https?:/i.test(u)?u:"https://"+u;
Promise.all([cfg,pronto]).then(([c])=>{
const o=[["PayPal","Doação rápida e segura",c.paypal,"P","paypal"],["Revolut","Transferência instantânea",c.revolut,"R","revolut"],["Buy Me a Coffee","Oferecer um café virtual",c.bmc,ICON.coffee,"bmc"]].filter(x=>x[2]);
const a=$("#apoio");if(!o.length||!a)return;
a.innerHTML=`<button type="button" class="b b-ouro">${ICON.coffee}<span>Apoiar</span></button>`;
const d=document.createElement("dialog");d.className="apoio";
d.innerHTML=`<div class="topo"><h2>Apoiar o projeto</h2><button type="button" class="b" aria-label="Fechar">${ICON.x}</button></div><p>Se este site te poupou trabalho, podes ajudar a mantê-lo.</p>`+o.map(([t,s,u,i,k])=>`<a class="op op-${k}" href="${esc(url(u))}" target="_blank" rel="noopener"><span class="oi">${i}</span><span><strong>${t}</strong><small>${s}</small></span>${ICON.ext}</a>`).join("");
document.body.append(d);
a.firstChild.onclick=()=>d.showModal();$("button",d).onclick=()=>d.close();d.onclick=e=>{if(e.target===d)d.close()}});