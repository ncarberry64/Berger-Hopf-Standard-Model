/**
 * Preferences for voices actually exposed by the browser's getVoices().
 * Web Speech supplies neither gender nor release/version metadata. Match known
 * male voice names, prefer advertised modern voice families, and never imply
 * that an Azure catalog entry is installed or available in the browser.
 * Names checked against Microsoft's catalog on 2026-11-28:
 * https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=text-to-speech
 * Browser capability contract:
 * https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/getVoices
 * https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice
 */
export type NarrationVoice = Pick<
  SpeechSynthesisVoice,
  'name' | 'lang' | 'voiceURI' | 'localService'
>;

// The order is a narration preference, not an inferred release chronology.
const maleNames = [
  'andrew3',
  'andrew2',
  'andrew',
  'guy',
  'ryan',
  'brian',
  'ethan',
  'jimmie',
  'grant',
  'jasper',
  'adam',
  'caleb',
  'lewis',
  'steffan',
  'tyler',
  'vance',
  'juno',
  'davis',
  'jason',
  'christopher',
  'brandon',
  'derek',
  'dustin',
  'eric',
  'jacob',
  'roger',
  'samuel',
  'tony',
  'kai',
  'ash',
  'alloy',
  'echo',
  'onyx',
  'goldenspark',
  // Familiar installed system voices are retained as an explicit fallback.
  'david',
  'mark',
  'george',
  'daniel',
  'alex',
  'fred',
  'ralph',
  'albert',
  'oliver',
  'thomas',
  'james',
  'lee',
  'aaron',
  'arthur',
  'gordon',
  'reed',
  'rishi',
  'russell',
  'sean',
  'tom',
  'liam',
  'luke',
];
const malePatterns = maleNames.map(
  (name) =>
    new RegExp(
      `(?:^|[^a-z0-9])${name}(?=$|[^a-z0-9]|multilingual|neural|online|desktop|turbo)`,
      'i',
    ),
);

export function narrationVoiceKey(voice: NarrationVoice) {
  return [voice.voiceURI, voice.name, voice.lang]
    .map(encodeURIComponent)
    .join('|');
}

function preference(voice: NarrationVoice): [number, number, number] | null {
  if (!/^en(?:[-_]|$)/i.test(voice.lang)) return null;
  const name = `${voice.name} ${voice.voiceURI}`;
  if (/\bfemale\b/i.test(name)) return null;
  const knownIndex = malePatterns.findIndex((pattern) => pattern.test(name));
  const explicitlyMale = /\bmale\b/i.test(name);
  if (knownIndex < 0 && !explicitlyMale) return null;
  const maleIndex = knownIndex < 0 ? maleNames.length : knownIndex;
  const latestFamily = /dragonhd\w*latest|mai[- ]?voice[- ]?2/i.test(name);
  const modernFamily = /neural|natural|online/i.test(name);
  const googleMale = /google.*english.*\bmale\b/i.test(name);
  const tier = latestFamily ? 0 : modernFamily ? 1 : googleMale ? 2 : 3;
  const locale = /^en[-_]us$/i.test(voice.lang)
    ? 0
    : /^en[-_]gb$/i.test(voice.lang)
      ? 1
      : 2;
  return [tier, maleIndex, locale];
}

/** Return a stable, deduplicated preference list; unknown defaults are excluded. */
export function maleEnglishNarrationVoices<T extends NarrationVoice>(
  voices: readonly T[],
): T[] {
  const unique = new Map<
    string,
    { voice: T; rank: [number, number, number] }
  >();
  for (const voice of voices) {
    const rank = preference(voice);
    if (rank) unique.set(narrationVoiceKey(voice), { voice, rank });
  }
  return [...unique.values()]
    .sort(
      (a, b) =>
        a.rank[0] - b.rank[0] ||
        a.rank[1] - b.rank[1] ||
        a.rank[2] - b.rank[2] ||
        narrationVoiceKey(a.voice).localeCompare(
          narrationVoiceKey(b.voice),
          'en',
        ),
    )
    .map(({ voice }) => voice);
}

/** An explicit visitor selection wins; automatic choice upgrades on refresh. */
export function selectNarrationVoice<T extends NarrationVoice>(
  voices: readonly T[],
  preferredKey = '',
): T | null {
  const maleVoices = maleEnglishNarrationVoices(voices);
  return (
    maleVoices.find((voice) => narrationVoiceKey(voice) === preferredKey) ??
    maleVoices[0] ??
    null
  );
}
