export interface IAudioEngine {
  scheduleNote(audioTime: number, accent: boolean): void;
  resume(): Promise<void>;
  close(): Promise<void>;
  currentTime(): number;
}

export class AudioEngine implements IAudioEngine {
  private _ctx: AudioContext;

  constructor() {
    if (typeof AudioContext === 'undefined') {
      throw new Error('AudioContext is not available in this environment');
    }
    this._ctx = new AudioContext();
  }

  scheduleNote(audioTime: number, accent: boolean): void {
    const frequency = accent ? 1500 : 1000;
    const duration = 0.020;

    const osc = this._ctx.createOscillator();
    const gain = this._ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = frequency;

    gain.gain.setValueAtTime(1.0, audioTime);
    gain.gain.linearRampToValueAtTime(0.0, audioTime + duration);

    osc.connect(gain);
    gain.connect(this._ctx.destination);

    osc.start(audioTime);
    osc.stop(audioTime + duration);
  }

  resume(): Promise<void> {
    return this._ctx.resume();
  }

  close(): Promise<void> {
    return this._ctx.close();
  }

  currentTime(): number {
    return this._ctx.currentTime;
  }
}

export class SilentAudioEngine implements IAudioEngine {
  scheduleNote(_audioTime: number, _accent: boolean): void {}

  resume(): Promise<void> {
    return Promise.resolve();
  }

  close(): Promise<void> {
    return Promise.resolve();
  }

  currentTime(): number {
    return 0;
  }
}
