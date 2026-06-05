const lista=$("#lista");
const norm=s=>String(s??"").trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
const modo=v=>({sim:"sim",aleatorio:"aleatorio"}[norm(v)]||"nao");
function linha(v={}){const d=document.createElement("div");d.className="linha";
d.innerHTML=`<input class="n" aria-label="Nome" placeholder="Nome"><input class="t" aria-label="Telefone" placeholder="+351 912 345 678" inputmode="tel"><select class="m" aria-label="Missão secreta"><option value="aleatorio">Missão à sorte</option><option value="sim">Com missão</option><option value="nao">Sem missão</option></select><input class="g" aria-label="Grupo" placeholder="Grupo (opcional)"><button type="button" class="b b-verm x" aria-label="Remover">${ICON.x}</button>`;
$(".n",d).value=v.nome||"";$(".t",d).value=v.telefone||"";$(".m",d).value=v.missao===undefined?"aleatorio":modo(v.missao);$(".g",d).value=v.grupo||"";
$(".x",d).onclick=()=>d.remove();lista.append(d)}
const vazias=()=>[...lista.children].filter(d=>!$(".n",d).value&&!$(".t",d).value).forEach(d=>d.remove());
function ler(txt){try{const j=JSON.parse(txt);if(Array.isArray(j))return j.map(p=>typeof p==="string"?{nome:p}:p)}catch{}
return txt.split(/\r?\n/).map(l=>l.trim()).filter(l=>l&&!l.startsWith("#")).map(l=>{const [nome,telefone,missao,grupo]=l.split(/[;\t|,]/).map(x=>x.trim());return{nome,telefone,missao,grupo}})}
$("#mais").onclick=()=>linha();
$("#ficheiro").onclick=()=>$("#fx").click();
$("#fx").onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const a=ler(await f.text());if(!a.length)throw 0;vazias();a.forEach(linha);$("#erro").textContent=""}catch{$("#erro").textContent="Não consegui ler o ficheiro. Usa JSON ou linhas 'Nome; telefone; missão; grupo'."}e.target.value=""};
api("/api/participantes").catch(()=>[]).then(r=>(r.length?r:[{},{},{}]).forEach(linha));
cfg.then(c=>{$("#local").value=c.local||"";$("#valor").value=c.valor||"";$("#data").value=c.data||"";$("#contacto").value=c.contacto||"";$("#senhaBox").hidden=!c.precisa_senha});
$("#criar").onclick=async()=>{$("#erro").textContent="";
const participantes=[...lista.children].map(d=>({nome:$(".n",d).value,telefone:$(".t",d).value,missao:$(".m",d).value,grupo:$(".g",d).value})).filter(p=>p.nome||p.telefone);
try{const r=await api("/api/sorteios",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({local:$("#local").value,valor:$("#valor").value,data:$("#data").value,contacto:$("#contacto").value,senha:$("#senha").value,participantes})});location.href="/admin/"+r.admin_token}catch(e){$("#erro").textContent=e.message}};
$("#ficheiro").insertAdjacentHTML("afterbegin",ICON.up);$("#mais").insertAdjacentHTML("afterbegin",ICON.plus);
