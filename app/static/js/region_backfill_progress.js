document.addEventListener('DOMContentLoaded', ()=>{
  const bar = document.getElementById('region-backfill-bar');
  const label = document.getElementById('region-backfill-label');
  const startBtn = document.getElementById('region-backfill-start');
  const reportDiv = document.getElementById('region-backfill-report');
  const abortBtn = document.getElementById('region-backfill-abort');
  if(!bar||!label||!startBtn) return;

  let currentTaskId = null;
  let polling = false;

  function updateBar(pct){
    bar.style.width = pct+'%';
    bar.setAttribute('aria-valuenow', pct);
  }

  function formatETA(seconds){
    if(!seconds || seconds < 0) return '';
    const s = Math.round(seconds);
    const m = Math.floor(s/60);
    const r = s%60;
    return `${m}:${r.toString().padStart(2,'0')}`;
  }

  async function fetchStatus(){
    try {
      const resp = await fetch('/bird/region-backfill/progress/');
      if(!resp.ok){
        label.textContent = 'Status-Fehler ('+resp.status+')';
        return;
      }
      const data = await resp.json();
      if(!data.task_id){
        updateBar(0);
        label.textContent='Kein aktiver Task';
        startBtn.disabled=false;
        return;
      }
      currentTaskId = data.task_id;
      const pct = data.percent || 0;
      updateBar(pct);
      if(data.stale){
        label.textContent = 'Abgebrochen / keine Aktivität (stale). Bitte erneut starten.';
        startBtn.disabled=false;
        polling=false;
        return;
      }
      if(data.active){
        const eta = formatETA(data.eta_seconds);
        label.textContent = `Läuft: ${pct}% (${data.processed}/${data.total})${eta?` ETA ${eta}`:''}`;
        startBtn.disabled=true;
        if(abortBtn){ abortBtn.style.display='inline-block'; abortBtn.disabled=false; }
      } else if(data.finished){
        label.textContent = `Abgeschlossen: ${data.success} erfolgreich, ${data.errors} Fehler`;
        polling=false;
        startBtn.disabled=false;
        if(abortBtn){ abortBtn.style.display='none'; }
        if(data.errors>0){
          reportDiv.textContent = `Fertig. Erfolgreich: ${data.success}, Fehler: ${data.errors}. Details siehe GeocodeAttempt / Patienten ohne Region.`;
        } else {
          reportDiv.textContent = `Fertig. Alle ${data.success} Patienten erhielten eine Region.`;
        }
      } else {
        label.textContent = 'Wartet…';
        if(abortBtn){ abortBtn.style.display='none'; }
      }
    } catch(e){
      label.textContent='Status konnte nicht geladen werden';
    }
  }
  async function abortTask(){
    if(!abortBtn) return;
    abortBtn.disabled=true;
    try {
      const resp = await fetch('/bird/region-backfill/abort/');
      const data = await resp.json();
      if(data.aborted){
        label.textContent='Abbruch angefordert…';
        // Weiter pollen bis finished flag kommt (Thread beendet sich bei nächstem Schleifendurchlauf)
        polling=true;
        pollLoop();
      } else {
        label.textContent='Abbruch nicht möglich: '+(data.reason||'Unbekannt');
        abortBtn.disabled=false;
      }
    } catch(e){
      label.textContent='Abbruch fehlgeschlagen (Netzwerk)';
      abortBtn.disabled=false;
    }
  }

  async function startTask(){
    startBtn.disabled=true;
    label.textContent='Starte…';
    try {
      const resp = await fetch('/bird/region-backfill/start/');
      if(!resp.ok){
        label.textContent='Start fehlgeschlagen ('+resp.status+')';
        startBtn.disabled=false;
        return;
      }
      const data = await resp.json();
      if(data.started){
        label.textContent='Gestartet…';
        polling=true;
        pollLoop();
      } else if(data.task_id){
        label.textContent='Läuft bereits (Task '+data.task_id+')';
        polling=true;
        pollLoop();
      } else {
        label.textContent='Start nicht möglich: '+(data.reason||'Unbekannt');
        startBtn.disabled=false;
      }
    } catch(e){
      label.textContent='Start fehlgeschlagen (Netzwerk)';
      startBtn.disabled=false;
    }
  }

  function pollLoop(){
    if(!polling) return;
    fetchStatus();
    setTimeout(pollLoop, 2500);
  }

  startBtn.addEventListener('click', startTask);
  if(abortBtn){ abortBtn.addEventListener('click', abortTask); }
  // Initial Status prüfen (Task kann schon laufen)
  polling=true; pollLoop();
});