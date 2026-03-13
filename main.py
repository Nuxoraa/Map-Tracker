from flask import Flask, render_template_string, jsonify, request
import urllib.request
import urllib.parse
import json
import random
import time

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MyMap</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{--bg:#0d0d0f;--panel:#141418;--border:#222228;--accent:#c8f04a;--accent2:#4af0c8;--text:#e8e8f0;--muted:#6a6a7a;--danger:#f04a6a;--warn:#f0a84a;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden;}
.topbar{display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--panel);border-bottom:1px solid var(--border);z-index:1000;flex-shrink:0;}
.logo{font-size:20px;font-weight:800;letter-spacing:-0.5px;color:var(--accent);white-space:nowrap;user-select:none;}
.logo span{color:var(--text);}
.search-wrap{flex:1;display:flex;gap:8px;max-width:520px;}
.search-input{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:9px 14px;color:var(--text);font-family:'Syne',sans-serif;font-size:14px;outline:none;transition:border-color .2s;}
.search-input:focus{border-color:var(--accent);}
.search-input::placeholder{color:var(--muted);}
.search-btn{background:var(--accent);border:none;border-radius:8px;padding:9px 16px;color:#0d0d0f;font-family:'Syne',sans-serif;font-weight:600;font-size:14px;cursor:pointer;transition:opacity .15s;white-space:nowrap;}
.search-btn:hover{opacity:.85;}
.nav-btn{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:9px 14px;color:var(--text);font-family:'Syne',sans-serif;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s;white-space:nowrap;}
.nav-btn:hover{border-color:var(--accent2);color:var(--accent2);}
.nav-btn.active{background:var(--accent2);border-color:var(--accent2);color:#0d0d0f;}
.coords-display{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);white-space:nowrap;min-width:150px;text-align:right;}
.main{flex:1;display:flex;overflow:hidden;position:relative;}
#map{flex:1;height:100%;background:#111;}
.side-panel{width:340px;background:var(--panel);border-left:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden;transition:width .3s;flex-shrink:0;}
.side-panel.collapsed{width:0;}
.panel-header{padding:13px 16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0;}
.panel-title{font-size:12px;font-weight:600;color:var(--accent2);text-transform:uppercase;letter-spacing:1px;}
.panel-close{background:none;border:none;color:var(--muted);cursor:pointer;font-size:18px;padding:2px 6px;border-radius:4px;}
.panel-close:hover{color:var(--text);background:var(--border);}
.panel-body{padding:14px 16px;overflow-y:auto;flex:1;}
.nav-mode-panel{background:var(--panel);border-bottom:1px solid var(--border);padding:12px 16px;flex-shrink:0;display:none;}
.nav-mode-panel.visible{display:block;}
.nav-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;}
.waypoints-list{display:flex;flex-direction:column;gap:6px;}
.waypoint-row{display:flex;align-items:center;gap:7px;}
.waypoint-badge{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0;}
.wp-a{background:#f04a6a22;border:1px solid var(--danger);color:var(--danger);}
.wp-b{background:#c8f04a22;border:1px solid var(--accent);color:var(--accent);}
.wp-mid{background:#4af0c822;border:1px solid var(--accent2);color:var(--accent2);}
.waypoint-input{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:7px 10px;color:var(--text);font-family:'Syne',sans-serif;font-size:12px;outline:none;transition:border-color .15s;min-width:0;}
.waypoint-input:focus{border-color:var(--accent2);}
.waypoint-input::placeholder{color:var(--muted);}
.wp-pick{background:none;border:none;color:var(--accent2);cursor:pointer;font-size:15px;padding:0 3px;border-radius:4px;flex-shrink:0;}
.wp-pick:hover{color:var(--accent);}
.wp-del{background:none;border:none;color:var(--muted);cursor:pointer;font-size:16px;padding:0 3px;border-radius:4px;flex-shrink:0;}
.wp-del:hover{color:var(--danger);}
.wp-search-results{position:fixed;z-index:9999;background:var(--panel);border:1px solid var(--border);border-radius:8px;max-height:190px;overflow-y:auto;box-shadow:0 4px 20px rgba(0,0,0,.7);}
.wp-result{padding:8px 12px;cursor:pointer;border-bottom:1px solid var(--border);font-size:12px;}
.wp-result:last-child{border-bottom:none;}
.wp-result:hover{background:var(--border);}
.wp-result-name{color:var(--text);font-weight:600;}
.wp-result-sub{color:var(--muted);font-size:11px;}
.add-wp-btn{background:var(--border);border:none;border-radius:6px;padding:7px 12px;color:var(--accent2);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;cursor:pointer;width:100%;margin-top:4px;transition:background .15s;}
.add-wp-btn:hover{background:#2a2a32;}
.route-btn{background:var(--accent);border:none;border-radius:8px;padding:10px;color:#0d0d0f;font-family:'Syne',sans-serif;font-size:13px;font-weight:700;cursor:pointer;width:100%;margin-top:8px;}
.route-btn:hover{opacity:.85;}
.clear-route-btn{background:var(--border);border:none;border-radius:8px;padding:8px;color:var(--danger);font-family:'Syne',sans-serif;font-size:12px;font-weight:600;cursor:pointer;width:100%;margin-top:4px;}
.clear-route-btn:hover{background:#2a2020;}
.route-card{background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:14px;}
.route-card-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;}
.route-dist{font-size:26px;font-weight:800;color:var(--accent);}
.route-dist-unit{font-size:13px;color:var(--muted);font-weight:400;}
.route-time{font-size:20px;font-weight:700;color:var(--text);}
.route-eta{font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:2px;}
.traffic-row{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:7px;margin-bottom:8px;}
.traffic-good{background:#4af0c811;border:1px solid #4af0c844;}
.traffic-medium{background:#f0a84a11;border:1px solid #f0a84a44;}
.traffic-bad{background:#f04a6a11;border:1px solid #f04a6a44;}
.traffic-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;}
.td-good{background:var(--accent2);box-shadow:0 0 6px var(--accent2);}
.td-med{background:var(--warn);box-shadow:0 0 6px var(--warn);}
.td-bad{background:var(--danger);box-shadow:0 0 6px var(--danger);}
.tt-good{color:var(--accent2);}
.tt-med{color:var(--warn);}
.tt-bad{color:var(--danger);}
.traffic-label{font-size:12px;font-weight:600;}
.traffic-sub{font-size:11px;color:var(--muted);margin-left:auto;font-family:'JetBrains Mono',monospace;}
.steps-section{margin-top:4px;}
.steps-title{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;}
.step-item{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid var(--border);}
.step-item:last-child{border-bottom:none;}
.step-num{font-size:10px;color:var(--muted);font-family:'JetBrains Mono',monospace;width:18px;flex-shrink:0;padding-top:1px;}
.step-text{font-size:12px;color:var(--text);line-height:1.4;}
.step-dist{font-size:11px;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-top:2px;}
.info-row{display:flex;flex-direction:column;gap:3px;margin-bottom:14px;}
.info-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;font-family:'JetBrains Mono',monospace;}
.info-value{font-size:14px;color:var(--text);word-break:break-word;}
.info-value.mono{font-family:'JetBrains Mono',monospace;font-size:12px;}
.info-value.accent{color:var(--accent);font-weight:600;}
.tag{display:inline-block;background:var(--border);border-radius:4px;padding:2px 8px;font-size:12px;color:var(--accent2);margin:2px 2px 0 0;font-family:'JetBrains Mono',monospace;}
.divider{height:1px;background:var(--border);margin:14px 0;}
.results-dropdown{position:absolute;top:52px;left:78px;width:400px;max-width:calc(100vw - 100px);background:var(--panel);border:1px solid var(--border);border-radius:10px;z-index:2000;max-height:300px;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.5);display:none;}
.results-dropdown.visible{display:block;}
.result-item{padding:10px 14px;cursor:pointer;border-bottom:1px solid var(--border);transition:background .1s;}
.result-item:last-child{border-bottom:none;}
.result-item:hover{background:var(--border);}
.result-name{font-size:13px;font-weight:600;color:var(--text);}
.result-sub{font-size:11px;color:var(--muted);margin-top:2px;}
.result-type{font-size:10px;color:var(--accent2);text-transform:uppercase;letter-spacing:.5px;font-family:'JetBrains Mono',monospace;float:right;}
.leaflet-control-zoom{display:none;}
.zoom-controls{position:absolute;bottom:88px;right:16px;z-index:800;display:flex;flex-direction:column;gap:4px;}
.zoom-btn{width:36px;height:36px;background:var(--panel);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .15s;line-height:1;}
.zoom-btn:hover{background:var(--border);color:var(--accent);}
.layer-toggle{position:absolute;bottom:16px;right:16px;z-index:800;display:flex;gap:6px;}
.layer-btn{padding:7px 12px;background:var(--panel);border:1px solid var(--border);border-radius:6px;color:var(--muted);font-family:'Syne',sans-serif;font-size:11px;font-weight:600;cursor:pointer;transition:all .15s;text-transform:uppercase;letter-spacing:.5px;}
.layer-btn.active{background:var(--accent);border-color:var(--accent);color:#0d0d0f;}
.layer-btn:not(.active):hover{border-color:var(--muted);color:var(--text);}
.status-bar{position:absolute;bottom:16px;left:16px;z-index:800;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--muted);background:rgba(13,13,15,.85);padding:5px 10px;border-radius:6px;border:1px solid var(--border);}
.loading-bar{position:absolute;top:0;left:0;right:0;height:2px;background:var(--accent);z-index:9999;transform:scaleX(0);transform-origin:left;transition:transform .3s;display:none;}
.loading-bar.active{display:block;transform:scaleX(.7);}
.loading-bar.done{transform:scaleX(1);opacity:0;transition:transform .2s,opacity .3s .2s;}
.pick-hint{position:absolute;top:60px;left:50%;transform:translateX(-50%);z-index:2000;background:var(--accent2);color:#0d0d0f;padding:8px 18px;border-radius:20px;font-size:13px;font-weight:700;pointer-events:none;opacity:0;transition:opacity .2s;white-space:nowrap;}
.pick-hint.visible{opacity:1;}
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
.leaflet-popup-content-wrapper{background:var(--panel)!important;border:1px solid var(--border)!important;border-radius:10px!important;color:var(--text)!important;box-shadow:0 4px 20px rgba(0,0,0,.6)!important;}
.leaflet-popup-tip{background:var(--panel)!important;}
.leaflet-popup-content{font-family:'Syne',sans-serif;font-size:13px;}
</style>
</head>
<body>
<div class="loading-bar" id="loadingBar"></div>
<div class="pick-hint" id="pickHint">Кликните на карту чтобы выбрать точку</div>

<div class="topbar">
  <div class="logo">My<span>Map</span></div>
  <div class="search-wrap">
    <input class="search-input" id="searchInput" type="text" placeholder="Поиск: улица, город, здание..." autocomplete="off"/>
    <button class="search-btn" onclick="doSearch()">Найти</button>
  </div>
  <button class="nav-btn" id="navToggleBtn" onclick="toggleNavMode()">🧭 Маршрут</button>
  <div class="coords-display" id="coordsDisplay">lat: — / lng: —</div>
</div>

<div class="results-dropdown" id="resultsDropdown"></div>

<div class="main">
  <div id="map"></div>

  <div class="side-panel" id="sidePanel">
    <div class="nav-mode-panel" id="navModePanel">
      <div class="nav-label">Точки маршрута</div>
      <div class="waypoints-list" id="waypointsList"></div>
      <button class="add-wp-btn" onclick="addWaypoint()">＋ Добавить промежуточную точку</button>
      <button class="route-btn" onclick="buildRoute()">▶ Построить маршрут</button>
      <button class="clear-route-btn" onclick="clearRoute()">✕ Очистить</button>
    </div>
    <div class="panel-header">
      <div class="panel-title" id="panelTitle">Информация</div>
      <button class="panel-close" onclick="closePanel()">×</button>
    </div>
    <div class="panel-body" id="panelBody">
      <div style="color:var(--muted);font-size:13px;line-height:1.7;">
        Нажмите на объект на карте чтобы узнать информацию.<br><br>
        Для маршрута — нажмите <strong style="color:var(--accent2)">🧭 Маршрут</strong>.<br>
        Точки можно ставить кнопкой ⊕ или кликом на карте.
      </div>
    </div>
  </div>

  <div class="zoom-controls">
    <button class="zoom-btn" onclick="map.zoomIn()">+</button>
    <button class="zoom-btn" onclick="map.zoomOut()">−</button>
  </div>

  <div class="layer-toggle">
    <button class="layer-btn active" id="btnStreet" onclick="setLayer('street')">Карта</button>
    <button class="layer-btn" id="btnSat" onclick="setLayer('satellite')">Спутник</button>
    <button class="layer-btn" id="btnTopo" onclick="setLayer('topo')">Рельеф</button>
  </div>
  <div class="status-bar" id="statusBar">zoom: 13</div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
// =========== MAP ===========
const map = L.map('map',{center:[43.238,76.945],zoom:13,zoomControl:false,attributionControl:false});
const tileLayers={
  street:L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}),
  satellite:L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19}),
  topo:L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',{maxZoom:17})
};
tileLayers.street.addTo(map);
let currentLayer='street';
function setLayer(n){map.removeLayer(tileLayers[currentLayer]);tileLayers[n].addTo(map);currentLayer=n;document.querySelectorAll('.layer-btn').forEach(b=>b.classList.remove('active'));document.getElementById('btn'+n[0].toUpperCase()+n.slice(1)).classList.add('active');}
map.on('zoom',()=>document.getElementById('statusBar').textContent='zoom: '+map.getZoom());
map.on('mousemove',e=>{const{lat,lng}=e.latlng;document.getElementById('coordsDisplay').textContent=`lat: ${lat.toFixed(5)} / lng: ${lng.toFixed(5)}`;});

// =========== LOADING ===========
function showLoading(){const b=document.getElementById('loadingBar');b.classList.remove('done');b.classList.add('active');}
function hideLoading(){const b=document.getElementById('loadingBar');b.classList.add('done');setTimeout(()=>b.classList.remove('active','done'),600);}

// =========== PANEL ===========
function openPanel(title){document.getElementById('sidePanel').classList.remove('collapsed');document.getElementById('panelTitle').textContent=title;}
function closePanel(){document.getElementById('sidePanel').classList.add('collapsed');}

// =========== SEARCH ===========
const searchInput=document.getElementById('searchInput');
const dropdown=document.getElementById('resultsDropdown');
let searchTimeout;
searchInput.addEventListener('input',()=>{clearTimeout(searchTimeout);const q=searchInput.value.trim();if(q.length<3){dropdown.classList.remove('visible');return;}searchTimeout=setTimeout(()=>fetchSuggestions(q),350);});
searchInput.addEventListener('keydown',e=>{if(e.key==='Enter')doSearch();if(e.key==='Escape')dropdown.classList.remove('visible');});
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap')&&!e.target.closest('#resultsDropdown'))dropdown.classList.remove('visible');});
async function fetchSuggestions(q){try{showLoading();const r=await fetch(`/search?q=${encodeURIComponent(q)}&limit=8`);const d=await r.json();hideLoading();renderDropdown(d);}catch(e){hideLoading();}}
function renderDropdown(results){if(!results.length){dropdown.classList.remove('visible');return;}dropdown.innerHTML=results.map(r=>`<div class="result-item" onclick='goTo(${r.lat},${r.lon},${JSON.stringify(r.display_name)},"${r.type||""}")'><span class="result-type">${ttrans(r.type)}</span><div class="result-name">${r.name||r.display_name.split(',')[0]}</div><div class="result-sub">${r.display_name.split(',').slice(1,3).join(',').trim()}</div></div>`).join('');dropdown.classList.add('visible');}
function ttrans(t){const m={street:'улица',road:'дорога',house:'дом',building:'здание',city:'город',town:'город',village:'село',suburb:'район',residential:'жилой',amenity:'объект',shop:'магазин',place:'место',university:'универ',school:'школа',hospital:'больница'};return m[t]||(t||'место');}
function goTo(lat,lon,displayName,type){dropdown.classList.remove('visible');searchInput.value=displayName.split(',')[0];map.setView([lat,lon],17,{animate:true});const mk=L.marker([lat,lon],{icon:L.divIcon({className:'',html:`<div style="width:12px;height:12px;background:var(--accent);border-radius:50%;border:2px solid #0d0d0f;box-shadow:0 0 0 3px var(--accent)44"></div>`,iconSize:[12,12],iconAnchor:[6,6]})}).addTo(map);setTimeout(()=>map.removeLayer(mk),8000);if(!navMode)showObjectInfo({display_name:displayName,lat,lon,type});}
async function doSearch(){const q=searchInput.value.trim();if(!q)return;dropdown.classList.remove('visible');showLoading();try{const r=await fetch(`/search?q=${encodeURIComponent(q)}&limit=1`);const d=await r.json();hideLoading();if(d.length)goTo(d[0].lat,d[0].lon,d[0].display_name,d[0].type);else alert('Ничего не найдено');}catch(e){hideLoading();}}

// =========== MAP CLICK ===========
map.on('click',async(e)=>{
  if(pickMode){handlePickClick(e.latlng.lat,e.latlng.lng);return;}
  if(navMode)return;
  const{lat,lng}=e.latlng;showLoading();
  try{const r=await fetch(`/reverse?lat=${lat}&lng=${lng}`);const d=await r.json();hideLoading();if(d&&d.display_name)showObjectInfo(d,lat,lng);}
  catch(e){hideLoading();}
});

// =========== OBJECT INFO ===========
function showObjectInfo(data,lat,lng){
  openPanel('Объект');
  const parts=(data.display_name||'').split(',');
  const name=parts[0].trim();const address=parts.slice(1,4).join(',').trim();
  const addr=data.address||{};
  const tags=[];if(addr.road)tags.push(addr.road);if(addr.suburb)tags.push(addr.suburb);if(addr.city||addr.town||addr.village)tags.push(addr.city||addr.town||addr.village);if(addr.country)tags.push(addr.country);
  const cLat=lat||data.lat;const cLng=lng||data.lon;
  document.getElementById('panelBody').innerHTML=`
    <div class="info-row"><div class="info-label">Название</div><div class="info-value accent">${name||'—'}</div></div>
    ${address?`<div class="info-row"><div class="info-label">Адрес</div><div class="info-value">${address}</div></div>`:''}
    ${addr.house_number?`<div class="info-row"><div class="info-label">Номер дома</div><div class="info-value">${addr.house_number}</div></div>`:''}
    ${addr.postcode?`<div class="info-row"><div class="info-label">Индекс</div><div class="info-value mono">${addr.postcode}</div></div>`:''}
    <div class="divider"></div>
    <div class="info-row"><div class="info-label">Координаты</div><div class="info-value mono">${parseFloat(cLat).toFixed(6)}, ${parseFloat(cLng).toFixed(6)}</div></div>
    ${tags.length?`<div class="info-row"><div class="info-label">Теги</div><div>${tags.map(t=>`<span class="tag">${t}</span>`).join('')}</div></div>`:''}
    <div class="divider"></div>
    <button onclick="setAsWp(${cLat},${cLng},'A')" style="background:#f04a6a22;border:1px solid var(--danger);color:var(--danger);padding:7px;border-radius:6px;cursor:pointer;font-family:'Syne',sans-serif;font-size:12px;font-weight:600;width:100%;margin-bottom:6px;">📍 Точка А (откуда)</button>
    <button onclick="setAsWp(${cLat},${cLng},'B')" style="background:#c8f04a22;border:1px solid var(--accent);color:var(--accent);padding:7px;border-radius:6px;cursor:pointer;font-family:'Syne',sans-serif;font-size:12px;font-weight:600;width:100%;margin-bottom:6px;">🏁 Точка Б (куда)</button>
    <button onclick="copyCoords(${cLat},${cLng})" style="background:var(--border);border:none;color:var(--text);padding:7px;border-radius:6px;cursor:pointer;font-family:'Syne',sans-serif;font-size:12px;width:100%;">📋 Скопировать координаты</button>`;
}
function copyCoords(lat,lng){navigator.clipboard.writeText(`${parseFloat(lat).toFixed(6)}, ${parseFloat(lng).toFixed(6)}`);}

// =========== NAV MODE ===========
let navMode=false;
let pickMode=false;
let pickTarget=null;
let waypoints=[{lat:null,lng:null,name:''},{lat:null,lng:null,name:''}];
let routeLayers=[];
let wpMarkerMap={};  // index -> L.Marker

function toggleNavMode(){
  navMode=!navMode;
  document.getElementById('navToggleBtn').classList.toggle('active',navMode);
  document.getElementById('navModePanel').classList.toggle('visible',navMode);
  document.getElementById('sidePanel').classList.remove('collapsed');
  if(navMode){renderWaypointsList();openPanel('Маршрут');}
  else{clearRoute();openPanel('Информация');document.getElementById('panelBody').innerHTML='<div style="color:var(--muted);font-size:13px;">Нажмите на объект на карте чтобы узнать информацию.</div>';}
}

function renderWaypointsList(){
  const list=document.getElementById('waypointsList');
  list.innerHTML=waypoints.map((wp,i)=>`
    <div class="waypoint-row" id="wprow-${i}">
      ${i===0?'<div class="waypoint-badge wp-a">А</div>':i===waypoints.length-1?'<div class="waypoint-badge wp-b">Б</div>':`<div class="waypoint-badge wp-mid">${i}</div>`}
      <input class="waypoint-input" id="wpi-${i}" type="text"
        placeholder="${i===0?'Откуда...':i===waypoints.length-1?'Куда...':'Промежуточная...'}"
        value="${wp.name||''}"
        oninput="onWpInput(${i},this.value)" autocomplete="off"/>
      <button class="wp-pick" title="Выбрать на карте" onclick="startPickMode(${i})">⊕</button>
      ${waypoints.length>2&&i>0&&i<waypoints.length-1?`<button class="wp-del" onclick="removeWaypoint(${i})">×</button>`:''}
    </div>`).join('');
}

// WP input search
const wpTimers={};
const wpDds={};
function onWpInput(i,val){
  waypoints[i].name=val;waypoints[i].lat=null;waypoints[i].lng=null;
  clearTimeout(wpTimers[i]);closeWpDd(i);
  if(val.length<3)return;
  wpTimers[i]=setTimeout(()=>fetchWpSugg(i,val),350);
}
async function fetchWpSugg(i,q){
  try{const r=await fetch(`/search?q=${encodeURIComponent(q)}&limit=6`);const d=await r.json();showWpDd(i,d);}catch(e){}
}
function showWpDd(i,results){
  closeWpDd(i);if(!results.length)return;
  const inp=document.getElementById('wpi-'+i);if(!inp)return;
  const rect=inp.getBoundingClientRect();
  const dd=document.createElement('div');
  dd.className='wp-search-results';dd.id='wpdd-'+i;
  dd.style.top=(rect.bottom+2)+'px';dd.style.left=rect.left+'px';dd.style.width=Math.max(rect.width,200)+'px';
  dd.innerHTML=results.map(r=>`<div class="wp-result" onclick='selWpResult(${i},${r.lat},${r.lon},${JSON.stringify(r.display_name)})'><div class="wp-result-name">${r.name||r.display_name.split(',')[0]}</div><div class="wp-result-sub">${r.display_name.split(',').slice(1,3).join(', ')}</div></div>`).join('');
  document.body.appendChild(dd);wpDds[i]=dd;
  setTimeout(()=>document.addEventListener('click',()=>closeWpDd(i),{once:true}),100);
}
function closeWpDd(i){if(wpDds[i]){wpDds[i].remove();delete wpDds[i];}}
function selWpResult(i,lat,lon,displayName){
  waypoints[i]={lat:parseFloat(lat),lng:parseFloat(lon),name:displayName.split(',')[0]};
  const inp=document.getElementById('wpi-'+i);if(inp)inp.value=waypoints[i].name;
  closeWpDd(i);placeWpMarker(i);
}

// Pick mode
function startPickMode(i){
  pickMode=true;pickTarget=i;
  document.getElementById('pickHint').classList.add('visible');
  map.getContainer().style.cursor='crosshair';
}
async function handlePickClick(lat,lng){
  pickMode=false;document.getElementById('pickHint').classList.remove('visible');map.getContainer().style.cursor='';
  const i=pickTarget;showLoading();
  try{
    const r=await fetch(`/reverse?lat=${lat}&lng=${lng}`);const d=await r.json();hideLoading();
    const name=d.display_name?d.display_name.split(',')[0]:`${lat.toFixed(5)},${lng.toFixed(5)}`;
    waypoints[i]={lat,lng,name};renderWaypointsList();placeWpMarker(i);
  }catch(e){hideLoading();waypoints[i]={lat,lng,name:`${lat.toFixed(5)},${lng.toFixed(5)}`};renderWaypointsList();placeWpMarker(i);}
}

// Set from object info
function setAsWp(lat,lng,which){
  if(!navMode){navMode=true;document.getElementById('navToggleBtn').classList.add('active');document.getElementById('navModePanel').classList.add('visible');openPanel('Маршрут');}
  const i=which==='A'?0:waypoints.length-1;
  waypoints[i]={lat,lng,name:`${lat.toFixed(5)}, ${lng.toFixed(5)}`};
  renderWaypointsList();placeWpMarker(i);
}

function addWaypoint(){
  waypoints.splice(waypoints.length-1,0,{lat:null,lng:null,name:''});
  renderWaypointsList();
}
function removeWaypoint(i){
  if(wpMarkerMap[i]){map.removeLayer(wpMarkerMap[i]);delete wpMarkerMap[i];}
  // re-index markers
  const newMap={};
  Object.keys(wpMarkerMap).forEach(k=>{const ki=parseInt(k);if(ki<i)newMap[ki]=wpMarkerMap[ki];else if(ki>i)newMap[ki-1]=wpMarkerMap[ki];});
  Object.assign(wpMarkerMap,newMap);
  waypoints.splice(i,1);
  renderWaypointsList();
}

// WP markers
function markerHtml(label,color){
  return `<div style="width:28px;height:28px;background:${color};border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid #0d0d0f;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,.5);"><span style="transform:rotate(45deg);color:#0d0d0f;font-weight:800;font-size:11px;font-family:Syne,sans-serif;">${label}</span></div>`;
}
function placeWpMarker(i){
  if(wpMarkerMap[i]){map.removeLayer(wpMarkerMap[i]);delete wpMarkerMap[i];}
  const wp=waypoints[i];if(!wp.lat)return;
  const isA=i===0;const isB=i===waypoints.length-1;
  const label=isA?'А':isB?'Б':String(i);
  const color=isA?'#f04a6a':isB?'#c8f04a':'#4af0c8';
  const mk=L.marker([wp.lat,wp.lng],{
    icon:L.divIcon({className:'',html:markerHtml(label,color),iconSize:[28,28],iconAnchor:[14,28]}),
    draggable:true
  }).addTo(map);
  mk.on('dragend',e=>{
    const{lat,lng}=e.target.getLatLng();
    waypoints[i].lat=lat;waypoints[i].lng=lng;
    waypoints[i].name=`${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    renderWaypointsList();
  });
  wpMarkerMap[i]=mk;
  map.panTo([wp.lat,wp.lng],{animate:true,duration:0.5});
}

// =========== BUILD ROUTE ===========
async function buildRoute(){
  const valid=waypoints.filter(w=>w.lat&&w.lng);
  if(valid.length<2){alert('Укажите минимум 2 точки маршрута');return;}
  clearRouteLayers();showLoading();
  try{
    const coords=waypoints.filter(w=>w.lat&&w.lng).map(w=>`${w.lng},${w.lat}`).join(';');
    const r=await fetch(`/route?coords=${encodeURIComponent(coords)}`);
    const data=await r.json();hideLoading();
    if(data.error){alert('Ошибка маршрута: '+data.error);return;}
    drawRoute(data);showRouteInfo(data);
  }catch(e){hideLoading();alert('Ошибка построения маршрута');}
}

function clearRouteLayers(){routeLayers.forEach(l=>map.removeLayer(l));routeLayers=[];}

function clearRoute(){
  clearRouteLayers();
  Object.values(wpMarkerMap).forEach(m=>map.removeLayer(m));
  wpMarkerMap={};
  waypoints=[{lat:null,lng:null,name:''},{lat:null,lng:null,name:''}];
  renderWaypointsList();
  document.getElementById('panelBody').innerHTML='<div style="color:var(--muted);font-size:13px;">Маршрут очищен.</div>';
}

function drawRoute(data){
  const shadow=L.polyline(data.geometry,{color:'#000',weight:9,opacity:.25}).addTo(map);routeLayers.push(shadow);
  const tcolor=data.traffic.level==='good'?'#4af0c8':data.traffic.level==='medium'?'#f0a84a':'#f04a6a';
  const line=L.polyline(data.geometry,{color:tcolor,weight:5,opacity:.9}).addTo(map);routeLayers.push(line);
  data.waypoint_snapped.forEach((wp,i)=>{
    const isA=i===0;const isB=i===data.waypoint_snapped.length-1;
    const c=isA?'#f04a6a':isB?'#c8f04a':'#4af0c8';
    const dot=L.circleMarker([wp[1],wp[0]],{radius:5,color:'#0d0d0f',weight:2,fillColor:c,fillOpacity:1}).addTo(map);
    routeLayers.push(dot);
  });
  map.fitBounds(L.polyline(data.geometry).getBounds(),{padding:[50,50],animate:true});
}

function fmtDist(m){return m>=1000?`${(m/1000).toFixed(1)} км`:`${Math.round(m)} м`;}

function showRouteInfo(data){
  openPanel('Маршрут');
  const km=data.distance>=1000;
  const distVal=km?(data.distance/1000).toFixed(1):Math.round(data.distance);
  const distUnit=km?'км':'м';
  const durMins=Math.round(data.duration/60);
  const durStr=durMins>=60?`${Math.floor(durMins/60)}ч ${durMins%60}м`:`${durMins} мин`;
  const eta=new Date(Date.now()+data.duration*1000).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'});
  const tl=data.traffic.level;
  const tcls=tl==='good'?'traffic-good':tl==='medium'?'traffic-medium':'traffic-bad';
  const tdcls=tl==='good'?'td-good':tl==='medium'?'td-med':'td-bad';
  const ttcls=tl==='good'?'tt-good':tl==='medium'?'tt-med':'tt-bad';
  const tlabel=tl==='good'?'Свободно':tl==='medium'?'Умеренные пробки':'Пробки';
  const tsub=tl==='good'?'без задержек':`задержка +${data.traffic.delay} мин`;
  const steps=data.steps.slice(0,15).map((s,i)=>`
    <div class="step-item">
      <div class="step-num">${i+1}.</div>
      <div><div class="step-text">${s.instruction}</div><div class="step-dist">${fmtDist(s.distance)}</div></div>
    </div>`).join('');
  document.getElementById('panelBody').innerHTML=`
    <div class="route-card">
      <div class="route-card-header">
        <div><div class="route-dist">${distVal}<span class="route-dist-unit"> ${distUnit}</span></div><div style="font-size:11px;color:var(--muted);margin-top:2px;">${waypoints.filter(w=>w.lat).length} точки</div></div>
        <div style="text-align:right"><div class="route-time">${durStr}</div><div class="route-eta">Прибытие: ${eta}</div></div>
      </div>
      <div class="traffic-row ${tcls}"><div class="traffic-dot ${tdcls}"></div><div class="traffic-label ${ttcls}">${tlabel}</div><div class="traffic-sub">${tsub}</div></div>
    </div>
    <div class="steps-section">
      <div class="steps-title">Пошаговый маршрут</div>
      ${steps}
      ${data.steps.length>15?`<div style="font-size:11px;color:var(--muted);padding:6px 0;">... ещё ${data.steps.length-15} шагов</div>`:''}
    </div>`;
}

// My location
map.locate({});
map.on('locationfound',e=>{if(!waypoints[0].lat){waypoints[0]={lat:e.latlng.lat,lng:e.latlng.lng,name:'Моё местоположение'};if(navMode)renderWaypointsList();}});
function goMyLocation(){map.locate({setView:true,maxZoom:16});}

// Loc button
const locCtrl=L.control({position:'bottomright'});
locCtrl.onAdd=()=>{const d=L.DomUtil.create('div');d.innerHTML=`<button onclick="goMyLocation()" title="Моё местоположение" style="width:36px;height:36px;background:var(--panel);border:1px solid var(--border);border-radius:8px;color:var(--accent2);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;margin-bottom:148px;">◎</button>`;return d;};
locCtrl.addTo(map);
</script>
</body>
</html>"""

# ==================== FLASK ROUTES ====================
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    limit = request.args.get('limit', 8)
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&addressdetails=1&limit={limit}&accept-language=ru"
    req = urllib.request.Request(url, headers={'User-Agent': 'MyMapApp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            data = json.loads(r.read())
        return jsonify([{
            'lat': i['lat'], 'lon': i['lon'],
            'display_name': i.get('display_name', ''),
            'name': i.get('namedetails', {}).get('name', ''),
            'type': i.get('type', i.get('class', ''))
        } for i in data])
    except:
        return jsonify([])

@app.route('/reverse')
def reverse():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&addressdetails=1&accept-language=ru"
    req = urllib.request.Request(url, headers={'User-Agent': 'MyMapApp/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=6) as r:
            return jsonify(json.loads(r.read()))
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/route')
def route():
    coords_str = request.args.get('coords', '')
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson&steps=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'MyMapApp/1.0'})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read())

        if data.get('code') != 'Ok' or not data.get('routes'):
            return jsonify({'error': 'Маршрут не найден'})

        rt = data['routes'][0]
        geometry = [(pt[1], pt[0]) for pt in rt['geometry']['coordinates']]
        distance = rt['distance']
        base_dur = rt['duration']

        # Traffic simulation
        hour = time.localtime().tm_hour
        is_rush = (7 <= hour <= 9) or (17 <= hour <= 20)
        is_night = hour < 6 or hour > 22
        rand = random.random()

        if is_night:
            level, delay_f = 'good', 0
        elif is_rush:
            if rand < 0.25:
                level, delay_f = 'medium', random.uniform(0.1, 0.25)
            else:
                level, delay_f = 'bad', random.uniform(0.25, 0.55)
        else:
            if rand < 0.55:
                level, delay_f = 'good', 0
            elif rand < 0.82:
                level, delay_f = 'medium', random.uniform(0.07, 0.2)
            else:
                level, delay_f = 'bad', random.uniform(0.2, 0.4)

        delay_s = int(base_dur * delay_f)
        total_dur = base_dur + delay_s

        # Steps
        steps = []
        for leg in rt.get('legs', []):
            for step in leg.get('steps', []):
                m = step.get('maneuver', {})
                steps.append({
                    'instruction': make_instruction(m.get('type', ''), m.get('modifier', ''), step.get('name', '')),
                    'distance': step.get('distance', 0)
                })

        return jsonify({
            'geometry': geometry,
            'distance': distance,
            'duration': total_dur,
            'traffic': {'level': level, 'delay': round(delay_s / 60)},
            'steps': steps,
            'waypoint_snapped': [wp['location'] for wp in data.get('waypoints', [])]
        })
    except Exception as e:
        return jsonify({'error': str(e)})

def make_instruction(mtype, modifier, name):
    road = f" на {name}" if name else ""
    table = {
        'depart':         {'': f'Начать движение{road}', 'left': f'Начать движение налево{road}', 'right': f'Начать движение направо{road}', 'straight': f'Ехать прямо{road}'},
        'arrive':         {'': 'Прибытие в пункт назначения', 'left': 'Пункт назначения слева', 'right': 'Пункт назначения справа'},
        'turn':           {'left': f'Повернуть налево{road}', 'right': f'Повернуть направо{road}', 'slight left': f'Держаться левее{road}', 'slight right': f'Держаться правее{road}', 'sharp left': f'Резкий поворот налево{road}', 'sharp right': f'Резкий поворот направо{road}', 'uturn': f'Развернуться{road}'},
        'new name':       {'': f'Продолжить{road}', 'straight': f'Ехать прямо{road}'},
        'continue':       {'': f'Продолжить{road}', 'straight': f'Продолжить прямо{road}', 'left': f'Продолжить налево{road}', 'right': f'Продолжить направо{road}'},
        'merge':          {'left': f'Влиться в поток слева{road}', 'right': f'Влиться в поток справа{road}', '': f'Влиться в поток{road}'},
        'on ramp':        {'left': f'Съезд налево{road}', 'right': f'Съезд направо{road}', '': f'Съезд на шоссе{road}'},
        'off ramp':       {'left': f'Съезд с шоссе налево{road}', 'right': f'Съезд с шоссе направо{road}', '': f'Съезд с шоссе{road}'},
        'fork':           {'left': f'На развилке — левее{road}', 'right': f'На развилке — правее{road}', 'slight left': f'На развилке — чуть левее{road}', 'slight right': f'На развилке — чуть правее{road}', '': f'На развилке{road}'},
        'end of road':    {'left': f'В конце дороги налево{road}', 'right': f'В конце дороги направо{road}', '': f'Конец дороги{road}'},
        'roundabout':     {'': f'Въехать в круговое движение{road}'},
        'exit roundabout':{'': f'Выехать из кругового движения{road}'},
        'rotary':         {'': f'Въехать в круговое движение{road}'},
        'exit rotary':    {'': f'Выехать из кругового движения{road}'},
        'notification':   {'': f'Продолжить{road}'},
    }
    row = table.get(mtype, {})
    return row.get(modifier, row.get('', f'Продолжить{road}'))

if __name__ == '__main__':
    print("\n🗺  MyMap запущен: http://localhost:5000\n")
    app.run(debug=True, port=5000)
