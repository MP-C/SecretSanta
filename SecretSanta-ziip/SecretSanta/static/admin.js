const t=location.pathname.split("/").pop();let S=[],ult="",prox=0;
const row=(p,i)=>`<div class="item"><div class="quem"><span class="nome">${esc(p.nome)}</span><span class="estado ${p.visto?"ok":""}">${p.visto?"✓ Viu em "+esc(p.visto):"Ainda não viu"}</span></div><div class="acoes"><a class="b b-wa" target="_blank" rel="noopener" href="${esc(p.whatsapp)}">${ICON.send}<span>WhatsApp</span></a><button class="b" data-l="${i}" title="Copiar link" aria-label="Copiar link de ${esc(p.nome)}">${ICON.clip}<span class="lbl">Copiar link</span></button><a class="b" target="_blank" rel="noopener" href="${esc(p.link)}" title="Abrir link" aria-label="Abrir link de ${esc(p.nome)}">${ICON.ext}<span class="lbl">Abrir</span></a><button class="b" data-m="${i}" title="Copiar mensagem" aria-label="Copiar mensagem de ${esc(p.nome)}">${ICON.msg}<span class="lbl">Mensagem</span></button></div></div>`;
function fila(){$("#fila").innerHTML=ICON.send+`<span>${prox>=S.length?"Todas abertas":`Abrir WhatsApp ${prox+1} de ${S.length}`}</span>`;$("#fila").disabled=prox>=S.length}
$("#baixar").innerHTML=ICON.down+"<span>Descarregar controlo</span>";$("#apagar").innerHTML=ICON.trash+"<span>Apagar sorteio</span>";
function mostrar(s){const k=JSON.stringify(s);if(k===ult)return;ult=k;S=s.participantes;const c=s.config,v=S.filter(p=>p.visto).length;
$("#info").innerHTML=`<dt>Local</dt><dd>${esc(c.local)}</dd><dt>Valor</dt><dd>${esc(c.valor)}</dd><dt>Data</dt><dd>${esc(c.data)}</dd><dt>Já viram</dt><dd>${v} de ${S.length}</dd>`;
$("#prog").style.width=(S.length?100*v/S.length:0)+"%";$("#lista").innerHTML=S.map(row).join("");$("#cmd").textContent=`python SecretDistribution.py --id ${s.id} --enviar`;fila()}
$("#lista").onclick=e=>{const b=e.target.closest("button");if(b)copiar(b,b.dataset.l!=null?S[b.dataset.l].link:S[b.dataset.m].mensagem)};
$("#fila").onclick=()=>{if(prox<S.length){window.open(S[prox].whatsapp,"_blank","noopener");prox++;fila()}};
$("#baixar").onclick=()=>{if(confirm("Este ficheiro revela quem tirou quem. Continuar?"))location.href="/api/admin/"+t+"/controlo"};
$("#apagar").onclick=()=>{if(confirm("Apagar todos os dados deste sorteio? Os links deixam de funcionar."))api("/api/admin/"+t,{method:"DELETE"}).then(()=>location.href="/").catch(e=>$("#erro").textContent=e.message)};
const carregar=()=>{if(!document.hidden)api("/api/admin/"+t).then(mostrar).catch(e=>$("#erro").textContent=e.message)};
carregar();setInterval(carregar,20000);
