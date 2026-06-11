import { useState } from 'react';

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

function normalizeProject(project) {
  if (!project || typeof project !== 'object') {
    return {
      id: '',
      title: 'Invalid project',
      status: 'invalid',
      warnings: ['invalid project record'],
      selectable: false,
    };
  }

  const id = project.project_id ?? project.id ?? '';
  const status = project.status ?? 'invalid';

  return {
    id,
    title: project.title ?? id ?? 'Untitled project',
    status,
    warnings: Array.isArray(project.warnings) ? project.warnings : [],
    selectable: status === 'valid' && Boolean(id),
  };
}

function buildProjectOptions(projects, activeProjectId) {
  const normalizedProjects = projects.map(normalizeProject);
  const options = [...normalizedProjects];

  if (activeProjectId && !options.some((project) => project.id === activeProjectId)) {
    options.unshift({
      id: activeProjectId,
      title: activeProjectId,
      status: 'valid',
      warnings: [],
      selectable: true,
    });
  }

  return options;
}

function formatProjectOptionLabel(project) {
  if (project.selectable) {
    return project.title === project.id ? project.title : `${project.title} (${project.id})`;
  }

  const statusLabel = project.status === 'warning' ? 'warning' : 'invalid';
  return `${project.title} — ${statusLabel}`;
}

export default function ProjectNav({
  activeProjectId,
  projects,
  projectsLoading,
  projectsError,
  onSelectProject,
  onCreateProject,
  isCreatingProject = false,
  createProjectError = '',
  createProjectStatus = '',
  onRefreshProjects,
  scenes,
  selectedSceneId,
  isLoading,
  error,
  onSelectScene,
}) {
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const trimmedProjectTitle = newProjectTitle.trim();
  const canCreateProject = Boolean(trimmedProjectTitle) && !isCreatingProject;
  const normalizedScenes = scenes.map(normalizeScene).filter((scene) => scene.id);
  const projectOptions = buildProjectOptions(projects, activeProjectId);
  const activeProject = projectOptions.find((project) => project.id === activeProjectId);
  const activeProjectLabel = activeProject?.title ?? activeProjectId ?? 'Project';

  async function handleCreateProjectSubmit(event) {
    event.preventDefault();

    if (!canCreateProject || typeof onCreateProject !== 'function') {
      return;
    }

    const created = await onCreateProject(trimmedProjectTitle);

    if (created) {
      setNewProjectTitle('');
    }
  }

  return (
    <aside className="project-nav" aria-label="Project navigation">
      <div className="panel-header">
        <p className="eyebrow">Project</p>
        <h1>{activeProjectLabel}</h1>
      </div>

      <section className="project-selector" aria-label="Project library">
        <div className="panel-header">
          <p className="eyebrow">Library</p>
        </div>

        {projectsLoading && <p className="muted-copy">Loading projects...</p>}
        {!projectsLoading && projectsError && (
          <p className="error-copy">{projectsError}</p>
        )}

        {!projectsLoading && (
          <label className="project-select-label">
            <span className="muted-copy">Active project</span>
            <select
              className="project-select"
              value={activeProjectId}
              onChange={(event) => onSelectProject(event.target.value)}
              aria-label="Select project"
            >
              {projectOptions.map((project) => (
                <option
                  key={project.id || project.title}
                  value={project.id}
                  disabled={!project.selectable}
                >
                  {formatProjectOptionLabel(project)}
                </option>
              ))}
            </select>
          </label>
        )}

        {!projectsLoading && projectOptions.some((project) => !project.selectable) && (
          <p className="muted-copy">
            Invalid or warning projects are listed but cannot be opened.
          </p>
        )}

        {typeof onCreateProject === 'function' && (
          <form
            className="create-project-form"
            onSubmit={handleCreateProjectSubmit}
            aria-label="Create blank project"
          >
            <label className="project-select-label">
              <span className="muted-copy">Project title</span>
              <input
                className="project-title-input"
                type="text"
                value={newProjectTitle}
                onChange={(event) => setNewProjectTitle(event.target.value)}
                placeholder="Your project title"
                disabled={isCreatingProject}
                aria-label="Project title"
              />
            </label>
            <button
              className="scene-item"
              type="submit"
              disabled={!canCreateProject}
            >
              <span>{isCreatingProject ? 'Creating project...' : 'Create blank project'}</span>
              <small>{isCreatingProject ? 'Please wait' : 'Library'}</small>
            </button>
            {createProjectError && (
              <p className="error-copy">{createProjectError}</p>
            )}
            {!createProjectError && createProjectStatus && (
              <p className="muted-copy">{createProjectStatus}</p>
            )}
          </form>
        )}

        {typeof onRefreshProjects === 'function' && (
          <button
            className="scene-item"
            type="button"
            onClick={onRefreshProjects}
            disabled={projectsLoading}
          >
            <span>Refresh projects</span>
            <small>{projectsLoading ? 'Loading' : 'Library'}</small>
          </button>
        )}
      </section>

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
