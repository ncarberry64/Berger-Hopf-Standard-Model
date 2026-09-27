type Player = Pick<
  HTMLMediaElement,
  'paused' | 'pause' | 'addEventListener' | 'removeEventListener'
>;
type Channel = Pick<
  BroadcastChannel,
  'postMessage' | 'addEventListener' | 'removeEventListener' | 'close'
>;

export function manageSoundtrackSession({
  windowTarget,
  documentTarget,
  players,
  isActive,
  channel,
  owner,
  onChange,
  onSuspend,
}: {
  windowTarget: EventTarget;
  documentTarget: EventTarget;
  players: Player[];
  isActive: () => boolean;
  channel?: Channel;
  owner: string;
  onChange: (playing: boolean) => void;
  onSuspend: () => void;
}) {
  let disposed = false;
  const update = () => {
    if (!disposed) onChange(players.some((player) => !player.paused));
  };
  function suspend() {
    const wasPlaying = players.some((player) => !player.paused);
    players.forEach((player) => player.pause());
    update();
    if (!disposed && wasPlaying) onSuspend();
  }
  const playListeners = players.map((player) => {
    const onPlay = () => {
      // Also catches a delayed play() promise resolving after the page hides.
      if (disposed || !isActive()) {
        suspend();
        return;
      }
      players.forEach((other) => {
        if (other !== player) other.pause();
      });
      channel?.postMessage({ type: 'playing', owner });
      update();
    };
    player.addEventListener('play', onPlay);
    player.addEventListener('pause', update);
    return onPlay;
  });
  const visibility = () => {
    if (!isActive()) suspend();
  };
  const message = (event: Event) => {
    const data = (event as MessageEvent).data;
    if (data?.type === 'playing' && data.owner !== owner) suspend();
  };
  windowTarget.addEventListener('blur', suspend);
  windowTarget.addEventListener('pagehide', suspend);
  documentTarget.addEventListener('visibilitychange', visibility);
  channel?.addEventListener('message', message);

  return () => {
    disposed = true;
    windowTarget.removeEventListener('blur', suspend);
    windowTarget.removeEventListener('pagehide', suspend);
    documentTarget.removeEventListener('visibilitychange', visibility);
    channel?.removeEventListener('message', message);
    channel?.close();
    players.forEach((player, i) => {
      player.removeEventListener('play', playListeners[i]);
      player.removeEventListener('pause', update);
      player.pause();
    });
  };
}
