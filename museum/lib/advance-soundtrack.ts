// Mobile media permission belongs to the element. Reuse the visitor-activated
// player across the playlist instead of starting another locked audio element.
export async function advanceSoundtrack(
  audio: Pick<HTMLAudioElement, 'src' | 'play'>,
  source: string,
) {
  audio.src = source;
  return audio.play();
}
