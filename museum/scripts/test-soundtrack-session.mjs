import test from 'node:test';
import assert from 'node:assert/strict';
import { manageSoundtrackSession } from '../lib/soundtrack-session.ts';
import { startSoundtrackOnInteraction } from '../lib/start-soundtrack.ts';

class AudioStub extends EventTarget {
  paused = true;
  play() {
    this.paused = false;
    this.dispatchEvent(new Event('play'));
    return Promise.resolve();
  }
  pause() {
    if (this.paused) return;
    this.paused = true;
    this.dispatchEvent(new Event('pause'));
  }
}

class ChannelStub extends EventTarget {
  closed = false;
  peer;
  postMessage(data) {
    this.peer?.dispatchEvent(new MessageEvent('message', { data }));
  }
  close() {
    this.closed = true;
  }
}

function session(options = {}) {
  const state = {
    windowTarget: new EventTarget(),
    documentTarget: new EventTarget(),
    players: [new AudioStub(), new AudioStub()],
    active: true,
    playing: false,
    suspensions: 0,
    ...options,
  };
  state.dispose = manageSoundtrackSession({
    ...state,
    owner: options.owner ?? 'museum',
    isActive: () => state.active,
    onChange: (value) => {
      state.playing = value;
    },
    onSuspend: () => {
      state.suspensions++;
      options.onSuspend?.();
    },
  });
  return state;
}

test('switching away, hiding the page, or leaving it pauses every player', async () => {
  for (const event of ['blur', 'visibilitychange', 'pagehide']) {
    const s = session();
    await s.players[0].play();
    s.active = false;
    const target =
      event === 'visibilitychange' ? s.documentTarget : s.windowTarget;
    target.dispatchEvent(new Event(event));
    assert.ok(
      s.players.every((player) => player.paused),
      event,
    );
    assert.equal(s.playing, false);
    assert.equal(s.suspensions, 1);
    s.active = true;
    s.windowTarget.dispatchEvent(new Event('focus'));
    s.documentTarget.dispatchEvent(new Event('visibilitychange'));
    assert.ok(
      s.players.every((player) => player.paused),
      'returning alone never starts sound',
    );
    s.dispose();
  }
});

test('late playback cannot start while the museum is inactive', async () => {
  const s = session({ active: false });
  await s.players[1].play();
  assert.equal(s.players[1].paused, true);
  assert.equal(s.playing, false);
  s.dispose();
});

test('starting another track stops the prior track without marking playback stopped', async () => {
  const s = session();
  await s.players[0].play();
  await s.players[1].play();
  assert.equal(s.players[0].paused, true);
  assert.equal(s.players[1].paused, false);
  assert.equal(s.playing, true);
  assert.equal(s.suspensions, 0);
  s.dispose();
});

test('a second museum session claims playback and pauses the first', async () => {
  const firstChannel = new ChannelStub(),
    secondChannel = new ChannelStub();
  firstChannel.peer = secondChannel;
  secondChannel.peer = firstChannel;
  const first = session({ owner: 'first', channel: firstChannel });
  const second = session({ owner: 'second', channel: secondChannel });
  await first.players[0].play();
  assert.equal(first.playing, true);
  await second.players[0].play();
  assert.equal(first.playing, false);
  assert.equal(second.playing, true);
  assert.equal(first.suspensions, 1);
  first.dispose();
  second.dispose();
});

test('cleanup stops playback, closes the channel and removes session callbacks', async () => {
  const channel = new ChannelStub();
  const s = session({ channel });
  await s.players[0].play();
  s.dispose();
  assert.ok(s.players.every((player) => player.paused));
  assert.equal(channel.closed, true);
  s.windowTarget.dispatchEvent(new Event('blur'));
  s.documentTarget.dispatchEvent(new Event('visibilitychange'));
  channel.dispatchEvent(
    new MessageEvent('message', { data: { type: 'playing', owner: 'other' } }),
  );
  assert.equal(s.suspensions, 0);
});

test('a fresh gesture resumes suspended music, while a deliberate pause stays paused', async () => {
  let stopGesture = () => {};
  const s = session({ onSuspend: () => arm() });
  function arm() {
    stopGesture();
    stopGesture = startSoundtrackOnInteraction(
      s.windowTarget,
      s.players[0],
      () => s.active,
    );
  }
  arm();
  s.windowTarget.dispatchEvent(new Event('click'));
  await Promise.resolve();
  assert.equal(s.playing, true);
  s.active = false;
  s.windowTarget.dispatchEvent(new Event('blur'));
  s.windowTarget.dispatchEvent(new Event('click'));
  assert.equal(s.playing, false);
  s.active = true;
  s.windowTarget.dispatchEvent(new Event('click'));
  await Promise.resolve();
  assert.equal(s.playing, true);
  stopGesture();
  s.players[0].pause();
  s.windowTarget.dispatchEvent(new Event('click'));
  assert.equal(s.playing, false);
  s.dispose();
});
