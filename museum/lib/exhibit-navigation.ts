export const EXHIBIT_CHANGE_EVENT = 'bhsm:exhibit-change';

// Retain the latest selection so a subscriber also sees navigation that happened
// before its effect mounted (including initial deep links).
const selections = new WeakMap<EventTarget, string>();

export function announceExhibit(target: EventTarget, slideId: string) {
  if (selections.get(target) === slideId) return;
  selections.set(target, slideId);
  target.dispatchEvent(
    new CustomEvent(EXHIBIT_CHANGE_EVENT, { detail: { slideId } }),
  );
}

export function followExhibit(
  target: EventTarget,
  onSelect: (slideId: string) => void,
) {
  const change = (event: Event) => {
    const slideId = (event as CustomEvent<{ slideId: string }>).detail?.slideId;
    if (slideId) onSelect(slideId);
  };
  target.addEventListener(EXHIBIT_CHANGE_EVENT, change);
  const current = selections.get(target);
  if (current) onSelect(current);
  return () => target.removeEventListener(EXHIBIT_CHANGE_EVENT, change);
}
