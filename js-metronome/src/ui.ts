import { FLASH_DURATION_MS } from './state';

export function updateBpmDisplay(bpm: number): void {
  const el = document.getElementById('bpm-display');
  if (el) el.textContent = String(bpm);
}

export function setTransportState(running: boolean): void {
  const btnStart = document.getElementById('btn-start') as HTMLButtonElement | null;
  const btnStop = document.getElementById('btn-stop') as HTMLButtonElement | null;
  if (btnStart) btnStart.disabled = running;
  if (btnStop) btnStop.disabled = !running;
}

export function flashIndicator(accent: boolean): void {
  const el = document.getElementById('indicator');
  if (!el) return;
  resetIndicator();
  el.classList.add(accent ? 'accent' : 'active');
  setTimeout(() => resetIndicator(), FLASH_DURATION_MS);
}

export function showAudioError(): void {
  const el = document.getElementById('audio-error');
  if (!el) return;
  el.classList.remove('hidden');
  el.style.display = 'block';
}

export function resetIndicator(): void {
  const el = document.getElementById('indicator');
  if (!el) return;
  el.classList.remove('active', 'accent');
}
