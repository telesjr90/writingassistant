import { useState } from 'react';
import { DEFAULT_DOCUMENT_TYPE, DOCUMENT_TYPES } from '../sharedDocumentController.js';

function normalizeSceneOrder(scene) {
  const rawOrder = scene.order_index ?? scene.orderIndex ?? scene.order;

  if (rawOrder === null || rawOrder === undefined || rawOrder === '') {
    return null;
  }

  const orderIndex = Number(rawOrder);
  return Number.isFinite(orderIndex) ? orderIndex : null;
}

function normalizeSceneOption(scene, originalIndex = 0) {
  if (typeof scene === 'string') {
    return {
      sceneId: scene,
      title: scene,
      label: scene,
      chapterId: null,
      orderIndex: null,
      metadataExists: false,
      status: 'Scene',
      originalIndex,
    };
  }

  if (!scene || typeof scene !== 'object') {
    return null;
  }

  const sceneId = scene.scene_id ?? scene.sceneId ?? scene.id ?? scene.name;
  const rawTitle = typeof scene.title === 'string' ? scene.title.trim() : '';
  const title = rawTitle || sceneId || '';

  return {
    sceneId,
    title,
    label: title,
    chapterId: scene.chapter_id ?? scene.chapterId ?? null,
    orderIndex: normalizeSceneOrder(scene),
    metadataExists: Boolean(scene.metadata_exists ?? scene.metadataExists),
    status: scene.status ?? 'Scene',
    originalIndex,
  };
}

function getSceneOptionId(sceneOption) {
  return sceneOption.sceneId;
}

function getSceneOptionLabel(sceneOption) {
  return sceneOption.label || sceneOption.sceneId;
}

function isActiveDocument(activeDocumentType, activeDocumentId, documentType, documentId) {
  return activeDocumentType === documentType && activeDocumentId === documentId;
}

function normalizeSceneList(scenes) {
  return scenes
    .map(normalizeSceneOption)
    .filter((scene) => scene?.sceneId)
    .sort((left, right) => {
      const leftHasOrder = left.orderIndex !== null;
      const rightHasOrder = right.orderIndex !== null;

      if (leftHasOrder && rightHasOrder && left.orderIndex !== right.orderIndex) {
        return left.orderIndex - right.orderIndex;
      }

      if (leftHasOrder !== rightHasOrder) {
        return leftHasOrder ? -1 : 1;
      }

      return left.originalIndex - right.originalIndex;
    });
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

function normalizeNoteOption(note, originalIndex = 0) {
  if (typeof note === 'string') {
    return {
      noteId: note,
      title: note,
      label: note,
      status: 'Note',
      originalIndex,
    };
  }

  if (!note || typeof note !== 'object') {
    return null;
  }

  const noteId = note.note_id ?? note.noteId ?? note.id ?? note.name;
  if (!noteId) {
    return null;
  }

  const rawTitle = typeof note.title === 'string' ? note.title.trim() : '';
  const title = rawTitle || noteId;

  return {
    noteId,
    title,
    label: title,
    status: note.status ?? 'Note',
    originalIndex,
  };
}

function normalizeNoteList(notes) {
  return notes
    .map(normalizeNoteOption)
    .filter((note) => note?.noteId);
}

function getNoteOptionId(noteOption) {
  return noteOption.noteId;
}

function getNoteOptionLabel(noteOption) {
  return noteOption.label || noteOption.title || noteOption.noteId;
}

function normalizeMaterialOption(material, originalIndex = 0) {
  if (typeof material === 'string') {
    return {
      materialId: material,
      title: material,
      label: material,
      status: 'Material',
      originalIndex,
    };
  }

  if (!material || typeof material !== 'object') {
    return null;
  }

  const materialId = material.material_id ?? material.materialId ?? material.id ?? material.name;
  if (!materialId) {
    return null;
  }

  const rawTitle = typeof material.title === 'string' ? material.title.trim() : '';
  const title = rawTitle || materialId;

  return {
    materialId,
    title,
    label: title,
    status: material.status ?? 'Material',
    originalIndex,
  };
}

function normalizeMaterialList(materials) {
  return materials
    .map(normalizeMaterialOption)
    .filter((material) => material?.materialId);
}

function getMaterialOptionId(materialOption) {
  return materialOption.materialId;
}

function getMaterialOptionLabel(materialOption) {
  return materialOption.label || materialOption.title || materialOption.materialId;
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
  isLoading,
  error,
  onSelectScene,
  notes = [],
  materials = [],
  activeWorkspaceView = 'overview',
  onSelectOverview,
  onSelectMemoryCanon,
  onSelectOMIDashboard,
  activeDocumentType = DEFAULT_DOCUMENT_TYPE,
  activeDocumentId = '',
  isLoadingNotes = false,
  isLoadingMaterials = false,
  notesError = '',
  materialsError = '',
  onCreateOwnerAuthoredNote,
  onCreateOwnerProvidedMaterial,
  onSelectNote,
  onSelectMaterial,
  selectedStoryCheckSourceId = '',
  storyCheckSourceStatus = 'Story Check requires a selected owner-authored source.',
  storyCheckSourceError = '',
  isImportingStoryCheckSource = false,
  onCreateOrImportStoryCheckSource,
  onSelectStoryCheckSource,
}) {
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const [ownerSourceId, setOwnerSourceId] = useState('');
  const [ownerSourceContent, setOwnerSourceContent] = useState('');
  const [ownerNoteId, setOwnerNoteId] = useState('');
  const [ownerNoteContent, setOwnerNoteContent] = useState('');
  const [ownerMaterialId, setOwnerMaterialId] = useState('');
  const [ownerMaterialContent, setOwnerMaterialContent] = useState('');
  const trimmedProjectTitle = newProjectTitle.trim();
  const trimmedOwnerSourceId = ownerSourceId.trim();
  const trimmedOwnerNoteId = ownerNoteId.trim();
  const trimmedOwnerMaterialId = ownerMaterialId.trim();
  const canCreateProject = Boolean(trimmedProjectTitle) && !isCreatingProject;
  const canImportOwnerSource =
    Boolean(trimmedOwnerSourceId)
    && ownerSourceContent.trim() !== ''
    && !isImportingStoryCheckSource;
  const canCreateOwnerNote =
    Boolean(trimmedOwnerNoteId)
    && ownerNoteContent.trim() !== ''
    && typeof onCreateOwnerAuthoredNote === 'function';
  const canCreateOwnerMaterial =
    Boolean(trimmedOwnerMaterialId)
    && ownerMaterialContent.trim() !== ''
    && typeof onCreateOwnerProvidedMaterial === 'function';
  const normalizedScenes = normalizeSceneList(scenes);
  const normalizedNotes = normalizeNoteList(notes);
  const normalizedMaterials = normalizeMaterialList(materials);
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

  async function handleOwnerSourceImportSubmit(event) {
    event.preventDefault();

    if (!canImportOwnerSource || typeof onCreateOrImportStoryCheckSource !== 'function') {
      return;
    }

    const created = await onCreateOrImportStoryCheckSource({
      sourceId: trimmedOwnerSourceId,
      content: ownerSourceContent,
    });

    if (created) {
      setOwnerSourceId('');
      setOwnerSourceContent('');
    }
  }

  async function handleOwnerNoteCreateSubmit(event) {
    event.preventDefault();

    if (!canCreateOwnerNote) {
      return;
    }

    const created = await onCreateOwnerAuthoredNote({
      noteId: trimmedOwnerNoteId,
      content: ownerNoteContent,
    });

    if (created) {
      setOwnerNoteId('');
      setOwnerNoteContent('');
    }
  }

  async function handleOwnerMaterialCreateSubmit(event) {
    event.preventDefault();

    if (!canCreateOwnerMaterial) {
      return;
    }

    const created = await onCreateOwnerProvidedMaterial({
      materialId: trimmedOwnerMaterialId,
      content: ownerMaterialContent,
    });

    if (created) {
      setOwnerMaterialId('');
      setOwnerMaterialContent('');
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

      <nav className="scene-list" aria-label="Workspace">
        <div className="panel-header">
          <p className="eyebrow">Workspace</p>
        </div>
        <button
          className={`scene-item${activeWorkspaceView === 'overview' ? ' is-active' : ''}`}
          type="button"
          onClick={() => onSelectOverview?.()}
        >
          <span>Overview</span>
          <small>Project status</small>
        </button>
        <button
          className={`scene-item${activeWorkspaceView === 'memory-canon' ? ' is-active' : ''}`}
          type="button"
          onClick={() => onSelectMemoryCanon?.()}
        >
          <span>Memory / Canon</span>
          <small>Approved-only</small>
        </button>
        <button
          className={`scene-item${activeWorkspaceView === 'omi-dashboard' ? ' is-active' : ''}`}
          type="button"
          onClick={() => onSelectOMIDashboard?.()}
          data-testid="omi-workspace-entry"
        >
          <span>OMI</span>
          <small>Review dashboard</small>
        </button>
      </nav>

      <nav className="scene-list" aria-label="Scenes">
        {isLoading && <p className="muted-copy">Loading scenes...</p>}
        {!isLoading && error && <p className="error-copy">{error}</p>}
        {!isLoading && !error && normalizedScenes.length === 0 && (
          <p className="muted-copy">No scenes yet.</p>
        )}
        {normalizedScenes.map((scene) => {
          const sceneId = getSceneOptionId(scene);
          const sceneLabel = getSceneOptionLabel(scene);

          return (
            <button
              className={
                `scene-item${
                  isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.SCENE, sceneId)
                    ? ' is-active'
                    : ''
                }`
              }
              type="button"
              key={sceneId}
              onClick={() => onSelectScene(sceneId)}
            >
              <span>{sceneLabel}</span>
              <small>{scene.status}</small>
            </button>
          );
        })}
      </nav>

      <section
        className="project-selector"
        aria-label="Owner-authored source for Story Check"
        data-testid="ux2-source-create-import"
      >
        <div className="panel-header">
          <p className="eyebrow">Story Check Source</p>
        </div>
        <p className="muted-copy">
          Create or import an owner-authored source, then choose the
          project-scoped selected source for Story Check.
        </p>

        <form
          className="create-project-form"
          onSubmit={handleOwnerSourceImportSubmit}
          aria-label="Create or import owner-authored source"
        >
          <label className="project-select-label">
            <span className="muted-copy">Source ID</span>
            <input
              className="project-title-input"
              type="text"
              value={ownerSourceId}
              onChange={(event) => setOwnerSourceId(event.target.value)}
              placeholder="scene_002"
              disabled={isImportingStoryCheckSource}
              aria-label="Owner-authored source ID"
            />
          </label>
          <label className="project-select-label">
            <span className="muted-copy">Owner-authored source text</span>
            <textarea
              className="project-title-input"
              value={ownerSourceContent}
              onChange={(event) => setOwnerSourceContent(event.target.value)}
              placeholder="Paste owner-authored scene/source text"
              disabled={isImportingStoryCheckSource}
              aria-label="Owner-authored source text"
              rows={5}
            />
          </label>
          <button
            className="scene-item"
            type="submit"
            disabled={!canImportOwnerSource}
            data-testid="ux2-source-import-owner-authored"
          >
            <span>{isImportingStoryCheckSource ? 'Importing source...' : 'Import owner-authored source'}</span>
            <small>Project-scoped source</small>
          </button>
        </form>

        <label className="project-select-label">
          <span className="muted-copy">Selected source</span>
          <select
            className="project-select"
            value={selectedStoryCheckSourceId}
            onChange={(event) => onSelectStoryCheckSource?.(event.target.value)}
            aria-label="Select project-scoped Story Check source"
            data-testid="ux2-selected-story-check-source"
          >
            <option value="">Story Check requires a selected owner-authored source</option>
            {normalizedScenes.map((scene) => {
              const sceneId = getSceneOptionId(scene);
              const sceneLabel = getSceneOptionLabel(scene);

              return (
                <option key={sceneId} value={sceneId}>
                  {sceneLabel}
                </option>
              );
            })}
          </select>
        </label>

        <p className="muted-copy">
          Selected source is not canon, memory, training data, or approved truth.
        </p>
        {storyCheckSourceError ? (
          <p className="error-copy">{storyCheckSourceError}</p>
        ) : (
          <p className="muted-copy">{storyCheckSourceStatus}</p>
        )}
      </section>

      <nav className="scene-list" aria-label="Notes">
        <div className="panel-header">
          <p className="eyebrow">Notes</p>
        </div>
        <form
          className="create-project-form"
          onSubmit={handleOwnerNoteCreateSubmit}
          aria-label="Create owner-authored note"
        >
          <label className="project-select-label">
            <span className="muted-copy">Note ID</span>
            <input
              className="project-title-input"
              type="text"
              value={ownerNoteId}
              onChange={(event) => setOwnerNoteId(event.target.value)}
              placeholder="note_001"
              aria-label="Owner-authored note ID"
            />
          </label>
          <label className="project-select-label">
            <span className="muted-copy">Owner-authored note text</span>
            <textarea
              className="project-title-input"
              value={ownerNoteContent}
              onChange={(event) => setOwnerNoteContent(event.target.value)}
              placeholder="Write owner-authored note text"
              aria-label="Owner-authored note text"
              rows={4}
            />
          </label>
          <button
            className="scene-item"
            type="submit"
            disabled={!canCreateOwnerNote}
            data-testid="ux2-note-create"
          >
            <span>Create owner-authored note</span>
            <small>Project-scoped, not canon by default</small>
          </button>
          <p className="muted-copy">
            This owner-authored note is project-scoped; notes/materials do not mutate memory or canon.
          </p>
        </form>
        {isLoadingNotes && <p className="muted-copy">Loading notes...</p>}
        {!isLoadingNotes && notesError && <p className="error-copy">{notesError}</p>}
        {!isLoadingNotes && !notesError && normalizedNotes.length === 0 && (
          <p className="muted-copy">No notes yet.</p>
        )}
        {normalizedNotes.map((note) => {
          const noteId = getNoteOptionId(note);
          const noteLabel = getNoteOptionLabel(note);

          return (
            <button
              className={
                `scene-item${
                  isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.NOTE, noteId)
                    ? ' is-active'
                    : ''
                }`
              }
              type="button"
              key={noteId}
              onClick={() => onSelectNote?.(noteId)}
            >
              <span>{noteLabel}</span>
              <small>{note.status}</small>
            </button>
          );
        })}
      </nav>

      <nav className="scene-list" aria-label="Materials">
        <div className="panel-header">
          <p className="eyebrow">Materials</p>
        </div>
        <form
          className="create-project-form"
          onSubmit={handleOwnerMaterialCreateSubmit}
          aria-label="Create owner-provided material"
        >
          <label className="project-select-label">
            <span className="muted-copy">Material ID</span>
            <input
              className="project-title-input"
              type="text"
              value={ownerMaterialId}
              onChange={(event) => setOwnerMaterialId(event.target.value)}
              placeholder="material_001"
              aria-label="Owner-provided material ID"
            />
          </label>
          <label className="project-select-label">
            <span className="muted-copy">Owner-provided material text</span>
            <textarea
              className="project-title-input"
              value={ownerMaterialContent}
              onChange={(event) => setOwnerMaterialContent(event.target.value)}
              placeholder="Paste owner-provided material text"
              aria-label="Owner-provided material text"
              rows={4}
            />
          </label>
          <button
            className="scene-item"
            type="submit"
            disabled={!canCreateOwnerMaterial}
            data-testid="ux2-material-create"
          >
            <span>Create owner-provided material</span>
            <small>Project-scoped, not canon by default</small>
          </button>
          <p className="muted-copy">
            This owner-provided material is project-scoped; notes/materials do not mutate memory or canon.
          </p>
        </form>
        {isLoadingMaterials && <p className="muted-copy">Loading materials...</p>}
        {!isLoadingMaterials && materialsError && <p className="error-copy">{materialsError}</p>}
        {!isLoadingMaterials && !materialsError && normalizedMaterials.length === 0 && (
          <p className="muted-copy">No materials yet.</p>
        )}
        {normalizedMaterials.map((material) => {
          const materialId = getMaterialOptionId(material);
          const materialLabel = getMaterialOptionLabel(material);

          return (
            <button
              className={
                `scene-item${
                  isActiveDocument(activeDocumentType, activeDocumentId, DOCUMENT_TYPES.MATERIAL, materialId)
                    ? ' is-active'
                    : ''
                }`
              }
              type="button"
              key={materialId}
              onClick={() => onSelectMaterial?.(materialId)}
            >
              <span>{materialLabel}</span>
              <small>{material.status}</small>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
