(function(){
  const root=document.getElementById('insightsGrid');
  if(!root)return;
  const dataUrl='https://raw.githubusercontent.com/Andydecreative/Hill-Green-Techno-Solutions-/main/data/insights.json';
  let articles=[],activeCategory='All',query='';
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const dateLabel=value=>{const d=new Date(value);return Number.isNaN(d.getTime())?'':new Intl.DateTimeFormat('en-IN',{day:'numeric',month:'short',year:'numeric',timeZone:'Asia/Kolkata'}).format(d)};
  function render(){
    const filtered=articles.filter(a=>(activeCategory==='All'||a.category===activeCategory)&&(!query||[a.title,a.summary,a.source,a.category].join(' ').toLowerCase().includes(query)));
    document.getElementById('insightsCount').textContent=filtered.length+' '+(filtered.length===1?'update':'updates');
    const featured=document.getElementById('insightsFeatured');
    featured.innerHTML=filtered.length?'<article class="insight-feature-card"><div class="insight-feature-copy"><span class="eyebrow">Featured India update</span><h3>'+esc(filtered[0].title)+'</h3><p>'+esc(filtered[0].summary)+'</p><a class="btn secondary" href="'+esc(filtered[0].url)+'" target="_blank" rel="noopener noreferrer">Read original source ↗</a></div><div class="insight-feature-art" aria-hidden="true"><span>HG</span></div></article>':'';
    root.innerHTML=filtered.slice(1).map(a=>'<article class="insight-card"><div class="insight-card-top"><span class="insight-category">'+esc(a.category)+'</span><time class="insight-date" datetime="'+esc(a.published_at)+'">'+esc(dateLabel(a.published_at))+'</time></div><h3>'+esc(a.title)+'</h3><p>'+esc(a.summary)+'</p><div class="insight-card-foot"><span class="insight-source">'+esc(a.source)+'</span><a class="insight-read" href="'+esc(a.url)+'" target="_blank" rel="noopener noreferrer">Read source ↗</a></div></article>').join('');
    document.getElementById('insightsEmpty').hidden=filtered.length!==0;
    if(filtered.length===1)root.innerHTML='';
  }
  document.getElementById('insightsFilters').addEventListener('click',e=>{const b=e.target.closest('button[data-category]');if(!b)return;activeCategory=b.dataset.category;document.querySelectorAll('.insight-filter').forEach(x=>x.classList.toggle('active',x===b));render()});
  document.getElementById('insightsSearch').addEventListener('input',e=>{query=e.target.value.trim().toLowerCase();render()});
  fetch(dataUrl,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('Feed not available');return r.json()}).then(data=>{
    articles=Array.isArray(data.articles)?data.articles:[];
    const updated=document.getElementById('insightsUpdated');
    updated.textContent=data.updated_at?'Updated '+dateLabel(data.updated_at)+' · India':'Updates will appear after the first scheduled run';
    if(!articles.length)root.innerHTML='<div class="insights-loading">The first automated news collection is being prepared. Please check back soon.</div>';
    render();
  }).catch(()=>{root.innerHTML='<div class="insights-loading">The latest updates could not be loaded right now. Please try again shortly.</div>';document.getElementById('insightsUpdated').textContent='Update temporarily unavailable'});
})();
