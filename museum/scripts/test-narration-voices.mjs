import test from 'node:test';
import assert from 'node:assert/strict';
import {
  maleEnglishNarrationVoices,
  narrationVoiceKey,
  selectNarrationVoice,
} from '../lib/narration-voices.ts';

const voice = (name, lang = 'en-US', localService = true) => ({
  name,
  lang,
  localService,
  voiceURI: name,
});

test('excludes female, unidentified default and non-English voices', () => {
  const female = voice('Microsoft Zira Desktop - English (United States)');
  const unidentified = { ...voice('Google US English'), default: true };
  assert.deepEqual(
    maleEnglishNarrationVoices([
      female,
      unidentified,
      voice('Microsoft AvaNeural'),
      voice('Google UK English Female', 'en-GB'),
      voice('Alexandra'),
      voice('Daniel', 'fr-FR'),
      voice('Microsoft David Desktop'),
    ]).map((item) => item.name),
    ['Microsoft David Desktop'],
  );
  assert.equal(selectNarrationVoice([female, unidentified]), null);
  assert.equal(selectNarrationVoice([]), null);
});

test('prefers browser-exposed latest families over natural, Google male and legacy voices', () => {
  const voices = [
    voice('Microsoft David Desktop'),
    voice('Google UK English Male', 'en-GB', false),
    voice(
      'Microsoft Andrew Online (Natural) - English (United States)',
      'en-US',
      false,
    ),
    voice('en-US-Ethan:MAI-Voice-2', 'en-US', false),
    voice('en-US-Andrew2:DragonHDLatestNeural', 'en-US', false),
    voice('en-US-Andrew3:DragonHDLatestNeural', 'en-US', false),
  ];
  const sorted = maleEnglishNarrationVoices(voices);
  assert.equal(sorted[0].name, 'en-US-Andrew3:DragonHDLatestNeural');
  assert.equal(sorted[1].name, 'en-US-Andrew2:DragonHDLatestNeural');
  assert.equal(sorted[2].name, 'en-US-Ethan:MAI-Voice-2');
  assert.match(sorted[3].name, /Andrew Online/);
  assert.equal(sorted[4].name, 'Google UK English Male');
  assert.match(sorted[5].name, /David/);
  assert.deepEqual(maleEnglishNarrationVoices([...voices].reverse()), sorted);
});

test('a later voiceschanged list upgrades automatic choice without overriding an explicit choice', () => {
  const david = voice('Microsoft David Desktop');
  const guy = voice('Microsoft Guy Online (Natural)', 'en-US', false);
  assert.equal(selectNarrationVoice([david]), david);
  assert.equal(selectNarrationVoice([david, guy]), guy);
  assert.equal(
    selectNarrationVoice([david, guy], narrationVoiceKey(david)),
    david,
  );
  assert.equal(selectNarrationVoice([guy], narrationVoiceKey(david)), guy);
});

test('matches installed male names without substring false positives and removes duplicate identities', () => {
  const daniel = voice('Daniel', 'en-GB');
  assert.deepEqual(
    maleEnglishNarrationVoices([
      voice('Alexandra'),
      voice('Google UK English Female', 'en-GB'),
      voice('Microsoft Mark Desktop'),
      daniel,
      daniel,
      voice('Alex'),
      voice('George'),
    ]).map((item) => item.name),
    ['Microsoft Mark Desktop', 'George', 'Daniel', 'Alex'],
  );
});
