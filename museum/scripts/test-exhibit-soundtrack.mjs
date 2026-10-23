import test from 'node:test';
import assert from 'node:assert/strict';
import { announceExhibit, followExhibit } from '../lib/exhibit-navigation.ts';
import { createExhibitSoundtrack } from '../lib/exhibit-soundtrack.ts';
import { manageSoundtrackSession } from '../lib/soundtrack-session.ts';
import { startSoundtrackOnInteraction } from '../lib/start-soundtrack.ts';

class AudioStub extends EventTarget {
  src = '';
  paused = true;
  muted = false;
  played = [];
  loads = 0;
  deferred = false;
  requests = [];
  load() {
    this.loads++;
  }
  play() {
    this.played.push(this.src);
    if (this.deferred)
      return new Promise((resolve, reject) => {
        this.requests.push({ resolve, reject, source: this.src });
      });
    this.start();
    return Promise.resolve();
  }
  start() {
    this.paused = false;
    this.dispatchEvent(new Event('play'));
  }
  pause() {
    if (this.paused) return;
    this.paused = true;
    this.dispatchEvent(new Event('pause'));
  }
}

function setup() {
  const state = {
    audio: new AudioStub(),
    active: true,
    playing: false,
    neededGestures: 0,
  };
  state.player = createExhibitSoundtrack({
    audio: state.audio,
    isActive: () => state.active,
    onChange: (playing) => {
      state.playing = playing;
    },
    onNeedGesture: () => {
      state.neededGestures++;
    },
  });
  return state;
}

const settle = () => new Promise((resolve) => setImmediate(resolve));

test('initial deep links replay to late subscribers; navigation needs no hash event', () => {
  const target = new EventTarget();
  const selected = [];
  announceExhibit(target, 'other-work');
  const stop = followExhibit(target, (slideId) => selected.push(slideId));
  announceExhibit(target, 'other-work');
  announceExhibit(target, 'science-decays');
  assert.deepEqual(selected, ['other-work', 'science-decays']);
  stop();
  announceExhibit(target, 'potential');
  assert.equal(selected.length, 2);
});

test('selection waits for explicit Play and reuses the same muted player across exhibits', async () => {
  const s = setup();
  s.player.select('welcome.mp3');
  assert.deepEqual(s.audio.played, []);
  await s.player.play();
  s.audio.muted = true;
  s.player.select('discovery.mp3');
  await settle();
  assert.deepEqual(s.audio.played, ['welcome.mp3', 'discovery.mp3']);
  assert.equal(s.audio.src, 'discovery.mp3');
  assert.equal(s.audio.muted, true);
  assert.equal(s.playing, true);
  s.player.select('discovery.mp3');
  assert.equal(
    s.audio.loads,
    2,
    'duplicate navigation does not restart the track',
  );
  s.player.dispose();
});

test('denied or suspended Play stays silent through exhibit selection until explicit retry', async () => {
  const s = setup();
  s.audio.deferred = true;
  // A direct link selects its own music without a playback request.
  s.player.select('deeplink.mp3');
  s.player.select('next-exhibit.mp3');
  assert.deepEqual(s.audio.played, []);

  const blocked = s.player.play();
  s.audio.requests[0].reject(new Error('NotAllowedError'));
  await assert.rejects(blocked, /NotAllowedError/);
  s.player.select('another-exhibit.mp3');
  await settle();
  assert.deepEqual(s.audio.played, ['next-exhibit.mp3']);
  assert.equal(s.playing, false);

  s.audio.deferred = false;
  await s.player.play();
  assert.equal(s.audio.src, 'another-exhibit.mp3');
  assert.equal(s.playing, true);
  s.active = false;
  s.player.suspend();
  s.active = true;
  s.player.select('after-tab-return.mp3');
  await settle();
  assert.deepEqual(s.audio.played, ['next-exhibit.mp3', 'another-exhibit.mp3']);
  assert.equal(s.audio.paused, true);
  assert.equal(s.playing, false);

  await s.player.play();
  assert.equal(s.audio.played.at(-1), 'after-tab-return.mp3');
  assert.equal(s.playing, true);
  s.player.dispose();
});

test('manual pause and mute survive navigation and session suspension', async () => {
  const s = setup();
  s.player.select('first.mp3');
  await s.player.play();
  s.audio.muted = true;
  s.player.pause();
  s.player.select('next.mp3');
  s.player.suspend();
  assert.deepEqual(s.audio.played, ['first.mp3']);
  assert.equal(s.player.isManuallyPaused(), true);
  assert.equal(s.audio.muted, true);
  assert.equal(s.neededGestures, 0);
  await s.player.play();
  assert.deepEqual(s.audio.played, ['first.mp3', 'next.mp3']);
  s.player.dispose();
});

test('rapid exhibit changes ignore obsolete play rejections and completions', async () => {
  const s = setup();
  s.audio.deferred = true;
  s.player.select('first.mp3');
  const first = s.player.play().catch(() => {});
  s.player.select('second.mp3');
  s.player.select('third.mp3');
  assert.deepEqual(s.audio.played, ['first.mp3', 'second.mp3', 'third.mp3']);
  s.audio.requests[0].reject(new Error('Aborted old source'));
  s.audio.start();
  s.audio.requests[2].resolve();
  await settle();
  s.audio.requests[1].resolve();
  await first;
  await settle();
  assert.equal(s.audio.src, 'third.mp3');
  assert.equal(s.audio.paused, false);
  assert.equal(s.playing, true);
  assert.equal(s.neededGestures, 0);
  s.player.dispose();
});

test('an explicit pause cancels a pending start and blocks late playback', async () => {
  const s = setup();
  s.audio.deferred = true;
  s.player.select('first.mp3');
  const pending = s.player.play();
  s.player.pause();
  s.player.select('second.mp3');
  s.audio.start();
  s.audio.requests[0].resolve();
  await pending;
  assert.equal(s.audio.paused, true);
  assert.equal(s.playing, false);
  assert.equal(s.audio.played.length, 1);
  s.player.dispose();
});

test('denied playback can retry, and simultaneous gesture events share a pending start', async () => {
  const s = setup();
  s.audio.deferred = true;
  s.player.select('first.mp3');
  const first = s.player.play();
  const duplicate = s.player.play();
  assert.equal(first, duplicate);
  assert.equal(s.audio.requests.length, 1);
  s.audio.requests[0].reject(new Error('NotAllowedError'));
  await assert.rejects(first, /NotAllowedError/);
  assert.equal(s.neededGestures, 1);
  s.audio.deferred = false;
  await s.player.play();
  assert.equal(s.audio.paused, false);
  s.player.dispose();
});

test('blur, hidden state, and another session cancel even a pending playback request', async () => {
  for (const event of ['blur', 'visibilitychange', 'message']) {
    const s = setup();
    s.audio.deferred = true;
    s.player.select('first.mp3');
    const windowTarget = new EventTarget();
    const documentTarget = new EventTarget();
    const channel = new EventTarget();
    channel.postMessage = () => {};
    channel.close = () => {};
    const dispose = manageSoundtrackSession({
      windowTarget,
      documentTarget,
      players: [s.audio],
      isActive: () => s.active,
      channel,
      owner: 'this-tab',
      onChange: (playing) => {
        s.playing = playing;
      },
      onBeforeSuspend: s.player.suspend,
      onSuspend: () => {},
    });
    const pending = s.player.play();
    if (event === 'message')
      channel.dispatchEvent(
        new MessageEvent('message', {
          data: { type: 'playing', owner: 'other-tab' },
        }),
      );
    else {
      s.active = false;
      (event === 'blur' ? windowTarget : documentTarget).dispatchEvent(
        new Event(event),
      );
    }
    s.active = true;
    s.player.select('second.mp3');
    s.audio.start();
    s.audio.requests[0].resolve();
    await pending;
    assert.equal(s.audio.paused, true, event);
    assert.equal(s.playing, false, event);
    assert.equal(
      s.audio.played.length,
      1,
      'return and navigation do not resume music',
    );
    assert.equal(s.neededGestures, 1);
    s.audio.deferred = false;
    await s.player.play();
    assert.equal(
      s.playing,
      true,
      'a fresh gesture can resume the current exhibit',
    );
    s.player.dispose();
    dispose();
  }
});

test('cleanup stops playback and prevents old requests from restarting sound', async () => {
  const s = setup();
  s.audio.deferred = true;
  s.player.select('first.mp3');
  const pending = s.player.play();
  s.player.dispose();
  s.player.select('second.mp3');
  s.audio.start();
  s.audio.requests[0].resolve();
  await pending;
  assert.equal(s.audio.paused, true);
  assert.equal(s.audio.src, 'first.mp3');
});

test('a late rejected play event cannot consume the gesture rearmed after suspension', async () => {
  const s = setup();
  s.audio.deferred = true;
  s.player.select('first.mp3');
  const windowTarget = new EventTarget();
  const documentTarget = new EventTarget();
  let stopGesture = () => {};
  const arm = () => {
    stopGesture();
    stopGesture = startSoundtrackOnInteraction(
      windowTarget,
      {
        get paused() {
          return s.audio.paused;
        },
        play: () => s.player.play(),
        addEventListener: s.audio.addEventListener.bind(s.audio),
        removeEventListener: s.audio.removeEventListener.bind(s.audio),
      },
      () => s.active,
    );
  };
  const dispose = manageSoundtrackSession({
    windowTarget,
    documentTarget,
    players: [s.audio],
    isActive: () => s.active,
    owner: 'this-tab',
    onChange: (playing) => {
      s.playing = playing;
    },
    onBeforeSuspend: () => {
      s.player.suspend();
      arm();
    },
    onSuspend: () => {},
  });
  arm();
  windowTarget.dispatchEvent(new Event('click'));
  s.active = false;
  windowTarget.dispatchEvent(new Event('blur'));
  s.active = true;
  s.audio.start();
  s.audio.requests[0].resolve();
  await settle();
  assert.equal(s.audio.paused, true);
  s.audio.deferred = false;
  windowTarget.dispatchEvent(new Event('click'));
  await settle();
  assert.deepEqual(s.audio.played, ['first.mp3', 'first.mp3']);
  assert.equal(s.playing, true);
  stopGesture();
  s.player.dispose();
  dispose();
});
