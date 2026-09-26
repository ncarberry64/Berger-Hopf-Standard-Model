import test from 'node:test';
import assert from 'node:assert/strict';
import { startSoundtrackOnInteraction } from '../lib/start-soundtrack.ts';

const settle = () => new Promise((resolve) => setImmediate(resolve));
class AudioStub extends EventTarget {
  attempts = 0;
  rejectNext = false;
  play() {
    this.attempts++;
    if (this.rejectNext) {
      this.rejectNext = false;
      return Promise.reject(new Error('Playback denied'));
    }
    this.dispatchEvent(new Event('play'));
    return Promise.resolve();
  }
}

test('click, completed pointer/touch gestures, and keys start playback synchronously', () => {
  for (const gesture of ['click', 'pointerup', 'touchend', 'keydown']) {
    const target = new EventTarget(),
      audio = new AudioStub();
    const dispose = startSoundtrackOnInteraction(target, audio);
    assert.equal(audio.attempts, 0);
    target.dispatchEvent(new Event(gesture));
    assert.equal(audio.attempts, 1);
    target.dispatchEvent(new Event('click'));
    assert.equal(
      audio.attempts,
      1,
      'later navigation must not restart paused music',
    );
    dispose();
  }
});

test('a denied start leaves later interactions able to retry', async () => {
  const target = new EventTarget(),
    audio = new AudioStub();
  audio.rejectNext = true;
  startSoundtrackOnInteraction(target, audio);
  target.dispatchEvent(new Event('pointerup'));
  await settle();
  target.dispatchEvent(new Event('click'));
  assert.equal(audio.attempts, 2);
  await settle();
  target.dispatchEvent(new Event('keydown'));
  assert.equal(audio.attempts, 2);
});

test('manual player use disarms the fallback and excluded controls do not double-toggle', () => {
  const target = new EventTarget(),
    audio = new AudioStub();
  startSoundtrackOnInteraction(
    target,
    audio,
    (event) => event.type !== 'click',
  );
  target.dispatchEvent(new Event('click'));
  assert.equal(audio.attempts, 0);
  audio.dispatchEvent(new Event('play'));
  target.dispatchEvent(new Event('keydown'));
  assert.equal(audio.attempts, 0);
});

test('unmount cleanup removes the interaction listeners', () => {
  const target = new EventTarget(),
    audio = new AudioStub();
  startSoundtrackOnInteraction(target, audio)();
  target.dispatchEvent(new Event('click'));
  assert.equal(audio.attempts, 0);
});
