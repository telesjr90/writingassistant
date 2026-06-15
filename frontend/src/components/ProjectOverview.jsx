function countItems(items) {
  return Array.isArray(items) ? items.length : 0;
}

function getProjectTitle(project) {
  if (!project || typeof project !== 'object') {
    return 'Untitled project';
  }

  const title = project.title ?? project.name;
  return typeof title === 'string' && title.trim() ? title.trim() : 'Untitled project';
}

function getProjectId(project) {
  if (!project || typeof project !== 'object') {
    return 'Unknown project ID';
  }

  const projectId = project.project_id ?? project.projectId ?? project.id;
  return typeof projectId === 'string' && projectId.trim()
    ? projectId.trim()
    : 'Unknown project ID';
}

function getOptionalProjectField(project, fieldName) {
  if (!project || typeof project !== 'object') {
    return 'Not available';
  }

  const value = project[fieldName];
  return typeof value === 'string' && value.trim() ? value.trim() : 'Not available';
}

function getStatusText(status, fallback) {
  if (typeof status === 'string' && status.trim()) {
    return status.trim();
  }

  if (!status || typeof status !== 'object') {
    return fallback;
  }

  if (typeof status.label === 'string' && status.label.trim()) {
    return status.label.trim();
  }

  if (typeof status.status === 'string' && status.status.trim()) {
    return status.status.trim();
  }

  return fallback;
}

function getStatusCount(status, fieldName) {
  if (!status || typeof status !== 'object') {
    return 0;
  }

  return countItems(status[fieldName]);
}

function OverviewAction({ onClick, children }) {
  if (!onClick) {
    return null;
  }

  return (
    <button type="button" onClick={onClick}>
      {children}
    </button>
  );
}

export default function ProjectOverview({
  project,
  scenes,
  notes,
  materials,
  omiStatus,
  approvedMemoryStatus,
  onOpenScenes,
  onOpenNotes,
  onOpenMaterials,
  onOpenOmi,
  onOpenApprovedMemory,
}) {
  const sceneCount = countItems(scenes);
  const noteCount = countItems(notes);
  const materialCount = countItems(materials);
  const omiStatusText = getStatusText(omiStatus, 'OMI workspace status is not available yet.');
  const approvedMemoryText = getStatusText(
    approvedMemoryStatus,
    'No approved memory/canon items shown here yet.',
  );

  return (
    <section className="project-overview" aria-label="Project overview">
      <header className="project-overview__header">
        <p className="project-overview__eyebrow">Project</p>
        <h2>{getProjectTitle(project)}</h2>
        <dl>
          <div>
            <dt>Project ID</dt>
            <dd>{getProjectId(project)}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{getOptionalProjectField(project, 'status')}</dd>
          </div>
          <div>
            <dt>Creation method</dt>
            <dd>{getOptionalProjectField(project, 'creation_method')}</dd>
          </div>
        </dl>
      </header>

      <section className="project-overview__section" aria-label="Scenes">
        <h3>Scenes</h3>
        <p>{sceneCount} scenes</p>
        {sceneCount === 0 ? <p>No scenes yet.</p> : null}
        <OverviewAction onClick={onOpenScenes}>Open scenes</OverviewAction>
      </section>

      <section className="project-overview__section" aria-label="Notes">
        <h3>Notes</h3>
        <p>{noteCount} notes</p>
        {noteCount === 0 ? <p>No notes yet.</p> : null}
        <OverviewAction onClick={onOpenNotes}>Open notes</OverviewAction>
      </section>

      <section className="project-overview__section" aria-label="Materials">
        <h3>Materials</h3>
        <p>{materialCount} materials</p>
        {materialCount === 0 ? <p>No materials yet.</p> : null}
        <OverviewAction onClick={onOpenMaterials}>Open materials</OverviewAction>
      </section>

      <section className="project-overview__section" aria-label="OMI">
        <h3>OMI</h3>
        <p>{omiStatusText}</p>
        <ul>
          <li>{getStatusCount(omiStatus, 'ideas')} ideas</li>
          <li>{getStatusCount(omiStatus, 'candidates')} candidates</li>
        </ul>
        <OverviewAction onClick={onOpenOmi}>Open OMI</OverviewAction>
      </section>

      <section className="project-overview__section" aria-label="Approved Memory / Canon">
        <h3>Approved Memory / Canon</h3>
        <p>{approvedMemoryText}</p>
        <OverviewAction onClick={onOpenApprovedMemory}>Open approved memory</OverviewAction>
      </section>
    </section>
  );
}
