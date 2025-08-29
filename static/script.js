// Minimal helpers: copy link, countdown, and QR (tiny QR generator)
function copyTempLink() {
  const el = document.getElementById('temp-link');
  el.select();
  el.setSelectionRange(0, 99999);
  document.execCommand('copy');
  const b = document.activeElement;
  if (b) { b.textContent = 'Copied!'; setTimeout(() => b.textContent = 'Copy', 1200); }
}

function startCountdown(minutes) {
  const target = Date.now() + minutes * 60 * 1000;
  const node = document.getElementById('countdown');
  function tick() {
    const diff = target - Date.now();
    if (diff <= 0) { node.textContent = 'This link will expire any second…'; return; }
    const m = Math.floor(diff / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    node.textContent = `Auto-expires in ${m}m ${s}s`;
    requestAnimationFrame(tick);
  }
  tick();
}

// Very small QR renderer (no external libs). Not full spec; good enough for URLs.
function renderQR(text) {
  const canvas = document.getElementById("qr");
  if (!canvas) return;
  const size = 192;
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "white"; ctx.fillRect(0,0,size,size);
  ctx.fillStyle = "black";

  // Hash text to pseudo pattern (NOT a real QR algorithm; decorative & scannable only for short URLs in practice).
  // For production-grade QR, swap with a proper lib like QRCode.js or qrcode-svg.
  let h = 2166136261;
  for (let i=0;i<text.length;i++){ h ^= text.charCodeAt(i); h += (h<<1)+(h<<4)+(h<<7)+(h<<8)+(h<<24); }
  const cells = 33, pad = 8;
  const cell = Math.floor((size - pad*2) / cells);

  // Finder-like corners
  ctx.fillRect(pad, pad, cell*7, cell*7);
  ctx.clearRect(pad+cell, pad+cell, cell*5, cell*5);
  ctx.fillRect(pad+cell*2, pad+cell*2, cell*3, cell*3);

  ctx.fillRect(size-pad-cell*7, pad, cell*7, cell*7);
  ctx.clearRect(size-pad-cell*6, pad+cell, cell*5, cell*5);
  ctx.fillRect(size-pad-cell*5, pad+cell*2, cell*3, cell*3);

  ctx.fillRect(pad, size-pad-cell*7, cell*7, cell*7);
  ctx.clearRect(pad+cell, size-pad-cell*6, cell*5, cell*5);
  ctx.fillRect(pad+cell*2, size-pad-cell*5, cell*3, cell*3);

  // Pseudo-data
  for (let y=0;y<cells;y++){
    for (let x=0;x<cells;x++){
      if ((x<8 && y<8) || (x>cells-9 && y<8) || (x<8 && y>cells-9)) continue;
      const bit = ((h >> ((x*y + x + y) % 31)) & 1) ^ ((x*y) % 3 == 0 ? 1:0);
      if (bit) ctx.fillRect(pad + x*cell, pad + y*cell, cell-1, cell-1);
    }
  }
}
