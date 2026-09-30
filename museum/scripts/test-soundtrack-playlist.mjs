import test from 'node:test';
import assert from 'node:assert/strict';
import { advanceSoundtrack } from '../lib/advance-soundtrack.ts';

test('playlist reuses the gesture-approved player and retains mute state', async () => {
  const player = {
    src: 'first.mp3',
    muted: true,
    permission: true,
    played: [],
    play() {
      assert.equal(this, player);
      assert.equal(this.permission, true);
      this.played.push(this.src);
      return Promise.resolve();
    },
  };
  await advanceSoundtrack(player, 'second.mp3');
  await advanceSoundtrack(player, 'first.mp3');
  assert.deepEqual(player.played, ['second.mp3', 'first.mp3']);
  assert.equal(player.muted, true);
});

test('a rejected track transition remains observable so the next tap can retry', async () => {
  const denied = new Error('NotAllowedError');
  const player = { src: 'first.mp3', play: () => Promise.reject(denied) };
  await assert.rejects(advanceSoundtrack(player, 'second.mp3'), denied);
  assert.equal(player.src, 'second.mp3');
});
