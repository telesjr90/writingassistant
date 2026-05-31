function normalizeScene(scene) {
  if (typeof scene === 'string') {
    return {
      id: scene,
      title: scene,
      status: 'Scene',
    };
  }

  const id = scene.id ?? scene.scene_id ?? scene.name;

  return {
    id,
    title: scene.title ?? id ?? '',
    status: scene.status ?? 'Scene',
  };
}

export default function ProjectNav({
  scenes,
  selectedSceneId,
  isLoading,
  error,
  onSelectScene,
}) {
  const normalizedScenes = scenes.map(normalizeScene).filter((scene) => scene.id);

  return (
    <aside className="project-nav" aria-label="Project navigation">
      <div className="panel-header">
        <p className="eyebrow">Project</p>
        <h1>Novel Draft</h1>
      </div>

      <nav className="scene-list" aria-label="Scenes">
        {isLoading && <p className="muted-copy">Loading scenes...</p>}
        {!isLoading && error && <p className="error-copy">{error}</p>}
        {!isLoading && !error && normalizedScenes.length === 0 && (
          <p className="muted-copy">No scenes yet.</p>
        )}
        {normalizedScenes.map((scene) => (
          <button
            className={`scene-item${selectedSceneId === scene.id ? ' is-active' : ''}`}
            type="button"
            key={scene.id}
            onClick={() => onSelectScene(scene.id)}
          >
            <span>{scene.title}</span>
            <small>{scene.status}</small>
          </button>
        ))}
      </nav>
    </aside>
  );
}
