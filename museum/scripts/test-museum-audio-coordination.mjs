import test from 'node:test';
import assert from 'node:assert/strict';
import { coordinateMuseumAudio } from '../lib/museum-audio-coordination.ts';

function setup() {
  const target = new EventTarget();
  const audio = { volume: 0.8, muted: false };
  let active = true;
  let playing = false;
  let starts = 0;
  const stop = coordinateMuseumAudio({
    target,
    audio,
    isLifecycleActive: () => active,
    player: {
      play: () => {
        starts++;
        playing = true;
        return Promise.resolve();
      },
      pause: () => {
        playing = false;
      },
    },
  });
  return {
    target,
    audio,
    stop,
    send: (name) => target.dispatchEvent(new Event(name)),
    setActive: (value) => {
      active = value;
    },
    starts: () => starts,
    playing: () => playing,
  };
}

test('lifecycle play starts synchronously and pause cancels only on the active lifecycle exhibit', () => {
  const s = setup();
  s.send('bhsm:lifecycle-play');
  assert.equal(s.starts(), 1);
  assert.equal(s.playing(), true);
  s.setActive(false);
  s.send('bhsm:lifecycle-pause');
  assert.equal(s.playing(), true);
  s.send('bhsm:lifecycle-play');
  assert.equal(s.starts(), 1);
  s.setActive(true);
  s.send('bhsm:lifecycle-pause');
  assert.equal(s.playing(), false);
  s.stop();
});

test('narration ducks once, keeps playing music and restores its prior volume without a new play request', () => {
  const s = setup();
  s.send('bhsm:play-music');
  s.send('bhsm:narration-start');
  s.send('bhsm:narration-start');
  assert.ok(Math.abs(s.audio.volume - 0.144) < 1e-10);
  assert.equal(s.playing(), true);
  s.send('bhsm:narration-end');
  assert.equal(s.audio.volume, 0.8);
  assert.equal(s.starts(), 1);
  s.stop();
});

test('ending narration never starts unrequested, manually paused or hidden-page music and preserves mute', () => {
  const s = setup();
  s.audio.muted = true;
  s.send('bhsm:narration-start');
  s.send('bhsm:narration-end');
  assert.equal(s.starts(), 0);
  s.send('bhsm:lifecycle-play');
  s.send('bhsm:narration-start');
  s.send('bhsm:lifecycle-pause');
  s.setActive(false);
  s.send('bhsm:narration-end');
  assert.equal(s.starts(), 1);
  assert.equal(s.playing(), false);
  assert.equal(s.audio.muted, true);
  assert.equal(s.audio.volume, 0.8);
  s.stop();
});

test('cleanup restores volume, removes event listeners and never resumes playback', () => {
  const s = setup();
  s.send('bhsm:narration-start');
  s.stop();
  assert.equal(s.audio.volume, 0.8);
  s.send('bhsm:lifecycle-play');
  s.send('bhsm:narration-start');
  assert.equal(s.starts(), 0);
  assert.equal(s.audio.volume, 0.8);
});
