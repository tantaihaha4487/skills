import {LyricsMotionController} from './lyrics-motion.mjs';

export function createLyricsView(container, {
  variant = 'panel',
  loading = false,
  synchronized = false,
  activeIndex = -1,
  noShapes = false,
  reducedMotion = false,
  performanceMode = false,
  onSeek = () => {},
} = {}) {
  const root = document.createElement('section');
  root.className = `lyrics-closure lyrics-closure--${variant}`;
  root.dataset.loading = String(loading);
  root.setAttribute('aria-label', variant === 'immersive' ? 'Immersive lyrics' : 'Lyrics');
  const loadingState = document.createElement('div');
  loadingState.className = 'lyrics-closure__loading';
  loadingState.textContent = 'Loading lyrics…';
  const emptyState = document.createElement('div');
  emptyState.className = 'lyrics-closure__empty';
  emptyState.textContent = 'Lyrics Unavailable';
  const list = document.createElement('div');
  list.className = 'lyrics-closure__list';
  list.setAttribute('role', 'list');
  root.append(loadingState, emptyState, list);
  container.replaceChildren(root);
  const controller = new LyricsMotionController({variant, root, list, onSeek});
  controller.setState({loading, synchronized, activeIndex, noShapes, reducedMotion, performanceMode});
  controller.setLines([], {synchronized, activeIndex});
  controller.setLoading = value => controller.setState({loading:value});
  controller.root = root;
  controller.list = list;
  return controller;
}
