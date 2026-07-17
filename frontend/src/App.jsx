import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ProjectNav from './components/ProjectNav.jsx';
import ProjectOverview from './components/ProjectOverview.jsx';
import MemoryCanonShell from './components/MemoryCanonShell.jsx';
import OMIShell from './components/OMIShell.jsx';
import OmiGuidedProjectCreation from './components/OmiGuidedProjectCreation.jsx';
import Editor from './components/Editor.jsx';
import AnalysisSidebar from './components/AnalysisSidebar.jsx';
import ProjectContext from './components/ProjectContext.jsx';
import OMIPanel from './components/OMIPanel.jsx';
import ReviewQueuePanel from './components/ReviewQueuePanel.jsx';
import {
  DEFAULT_DOCUMENT_TYPE,
  DOCUMENT_TYPES,
  canSaveDocument,
  createDocumentDescriptor,
  getActiveDocumentDescriptor,
  getDocumentResponseContent,
  getDocumentSwitchMessage,
  hasUnsavedDocumentEdits,
  resolveActiveDocumentType,
} from './sharedDocumentController.js';
import {
  PROJECT_ID,
  createOwnerAuthoredNote,
  createOwnerProvidedMaterial,
  createOmiGuidedProject,
  createOrImportOwnerAuthoredSource,
  createProject,
  createOMICandidate,
  createOMIIdea,
  createOMIPromotion,
  fetchBible,
  fetchMaterials,
  fetchMaterial,
  fetchNotes,
  fetchProjectContextReadiness,
  fetchRawArtifactEvidenceStatus,
  fetchNote,
  fetchScene,
  fetchScenes,
  fetchStoryform,
  fetchStoryformContext,
  getOMI,
  listProjects,
  runStoryCheckForSelectedSource,
  saveBible,
  saveMaterial,
  saveNote,
  saveScene,
  saveStoryform,
  reloadProjectScopedNotesMaterials,
  selectStoryCheckSource,
  updateOMICandidateDecision,
  updateOMIIdeaDecision,
} from './api.js';

const UNSAVED_CHANGES_MESSAGE = 'Discard unsaved changes and load another scene?';
const UNSAVED_NOTE_SWITCH_MESSAGE = 'Discard unsaved changes and load another note?';
const UNSAVED_MATERIAL_SWITCH_MESSAGE = 'Discard unsaved changes and load another material?';
const UNSAVED_PROJECT_SWITCH_MESSAGE = 'Discard unsaved document changes and switch projects?';
const UNSAVED_PROJECT_CREATE_MESSAGE =
  'Create a new project and discard unsaved document changes from the current project?';
const DOCUMENT_SWITCH_MESSAGES = {
  [DOCUMENT_TYPES.SCENE]: UNSAVED_CHANGES_MESSAGE,
  [DOCUMENT_TYPES.NOTE]: UNSAVED_NOTE_SWITCH_MESSAGE,
  [DOCUMENT_TYPES.MATERIAL]: UNSAVED_MATERIAL_SWITCH_MESSAGE,
};
const WORKSPACE_VIEWS = {
  OVERVIEW: 'overview',
  MEMORY_CANON: 'memory-canon',
  OMI_DASHBOARD: 'omi-dashboard',
  EDITOR: 'editor',
};

function isNonEmptyString(value) {
  return typeof value === 'string' && value.length > 0;
}

export function requireCompleteOmiGuidedProjectResponse(response) {
  const metadata = response?.project_metadata;
  const guidedMetadata = metadata?.omi_guided_creation;
  const isComplete = response?.status === 'complete'
    && response?.creation_method === 'omi_guided'
    && isNonEmptyString(response?.project_id)
    && isNonEmptyString(response?.omi_idea_id)
    && isNonEmptyString(response?.setup_note_id)
    && metadata
    && typeof metadata === 'object'
    && !Array.isArray(metadata)
    && metadata.project_id === response.project_id
    && metadata.creation_method === 'omi_guided'
    && guidedMetadata?.status === 'complete'
    && guidedMetadata.omi_idea_id === response.omi_idea_id
    && guidedMetadata.setup_note_id === response.setup_note_id;

  if (!isComplete) {
    const error = new Error(
      'Guided creation returned an incomplete response. No project was opened.',
    );
    error.code = 'malformed_guided_creation_response';
    error.payload = response ?? null;
    throw error;
  }

  return metadata;
}

export function upsertGuidedProjectMetadata(currentProjects, metadata) {
  const projectId = metadata.project_id;
  let foundExisting = false;
  const integratedProjects = currentProjects.flatMap((project) => {
    const matches = project?.project_id === projectId
      || project?.projectId === projectId
      || project?.id === projectId;

    if (!matches) {
      return [project];
    }

    if (foundExisting) {
      return [];
    }

    foundExisting = true;
    return [metadata];
  });

  return foundExisting ? integratedProjects : [...integratedProjects, metadata];
}

function formatJson(value) {
  return JSON.stringify(value ?? {}, null, 2);
}

function parseJsonObject(text, label) {
  let parsed;

  try {
    parsed = JSON.parse(text);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Invalid JSON.';
    throw new Error(`Invalid ${label} JSON: ${message}`);
  }

  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`${label} JSON must be an object.`);
  }

  return parsed;
}

export function createOperationGuard(getCurrentSession) {
  const session = getCurrentSession();
  return {
    session,
    isCurrent() {
      const current = getCurrentSession();
      return current.projectId === this.session.projectId
        && current.generation === this.session.generation;
    },
  };
}

export default function App() {
  const [activeProjectId, setActiveProjectId] = useState(PROJECT_ID);
  const currentProjectIdRef = useRef(activeProjectId);
  currentProjectIdRef.current = activeProjectId;
  const projectGenRef = useRef(0);
  const [projects, setProjects] = useState([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState('');
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [createProjectError, setCreateProjectError] = useState('');
  const [createProjectStatus, setCreateProjectStatus] = useState('');
  const [scenes, setScenes] = useState([]);
  const [selectedSceneId, setSelectedSceneId] = useState('');
  const [sceneContent, setSceneContent] = useState('');
  const [lastSavedContent, setLastSavedContent] = useState('');
  const [storyformContext, setStoryformContext] = useState('');
  const [contextReadinessLoading, setContextReadinessLoading] = useState(true);
  const [contextReadinessError, setContextReadinessError] = useState('');
  const [bibleReadinessState, setBibleReadinessState] = useState('loading');
  const [bibleReadinessReason, setBibleReadinessReason] = useState('');
  const [bibleDirectError, setBibleDirectError] = useState('');
  const [storyformReadinessState, setStoryformReadinessState] = useState('loading');
  const [storyformReadinessReason, setStoryformReadinessReason] = useState('');
  const [storyformDirectError, setStoryformDirectError] = useState('');
  const [storyformContextReadinessState, setStoryformContextReadinessState] = useState('loading');
  const [storyformContextReadinessReason, setStoryformContextReadinessReason] = useState('');
  const [storyformContextDirectError, setStoryformContextDirectError] = useState('');
  const [isRetryingContextReadiness, setIsRetryingContextReadiness] = useState(false);
  const [bibleText, setBibleText] = useState('{}');
  const [lastSavedBibleText, setLastSavedBibleText] = useState('{}');
  const [storyformText, setStoryformText] = useState('{}');
  const [lastSavedStoryformText, setLastSavedStoryformText] = useState('{}');
  const [omiData, setOmiData] = useState({ index: null, ideas: [], candidates: [] });
  const [analysisReport, setAnalysisReport] = useState(null);
  const [selectedStoryCheckSourceId, setSelectedStoryCheckSourceId] = useState('');
  const [selectedStoryCheckSource, setSelectedStoryCheckSource] = useState(null);
  const [storyCheckSourceStatus, setStoryCheckSourceStatus] = useState(
    'Story Check requires a selected owner-authored source.',
  );
  const [storyCheckSourceError, setStoryCheckSourceError] = useState('');
  const [isImportingStoryCheckSource, setIsImportingStoryCheckSource] = useState(false);
  const [sceneError, setSceneError] = useState('');
  const [isLoadingScenes, setIsLoadingScenes] = useState(true);
  const [isLoadingScene, setIsLoadingScene] = useState(false);
  const [isLoadingOMI, setIsLoadingOMI] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isSavingBible, setIsSavingBible] = useState(false);
  const [isSavingStoryform, setIsSavingStoryform] = useState(false);
  const [isCreatingOMIIdea, setIsCreatingOMIIdea] = useState(false);
  const [isCreatingOMICandidate, setIsCreatingOMICandidate] = useState(false);
  const [isCreatingOMIPromotion, setIsCreatingOMIPromotion] = useState(false);
  const [isUpdatingOMI, setIsUpdatingOMI] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const [bibleStatus, setBibleStatus] = useState('');
  const [storyformStatus, setStoryformStatus] = useState('');
  const [omiStatus, setOmiStatus] = useState('');
  const [omiError, setOmiError] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  // Notes / materials minimal shell (PHASE7-IMPL-005-T006)
  const [notes, setNotes] = useState([]);
  const [materials, setMaterials] = useState([]);
  const [selectedDocumentType, setSelectedDocumentType] = useState('');
  const [selectedNoteId, setSelectedNoteId] = useState('');
  const [selectedMaterialId, setSelectedMaterialId] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [lastSavedNoteContent, setLastSavedNoteContent] = useState('');
  const [materialContent, setMaterialContent] = useState('');
  const [lastSavedMaterialContent, setLastSavedMaterialContent] = useState('');
  const [isLoadingNotes, setIsLoadingNotes] = useState(true);
  const [isLoadingMaterials, setIsLoadingMaterials] = useState(true);
  const [isLoadingNote, setIsLoadingNote] = useState(false);
  const [isLoadingMaterial, setIsLoadingMaterial] = useState(false);
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [isSavingMaterial, setIsSavingMaterial] = useState(false);
  const [notesError, setNotesError] = useState('');
  const [materialsError, setMaterialsError] = useState('');
  const [noteError, setNoteError] = useState('');
  const [materialError, setMaterialError] = useState('');
  const [noteSaveStatus, setNoteSaveStatus] = useState('');
  const [materialSaveStatus, setMaterialSaveStatus] = useState('');
  const [activeWorkspaceView, setActiveWorkspaceView] = useState(WORKSPACE_VIEWS.OVERVIEW);
  const isDirty = selectedSceneId !== '' && sceneContent !== lastSavedContent;
  const isNoteDirty =
    selectedNoteId !== '' && noteContent !== lastSavedNoteContent;
  const isMaterialDirty =
    selectedMaterialId !== '' && materialContent !== lastSavedMaterialContent;
  const hasUnsavedDocumentChanges = hasUnsavedDocumentEdits({
    scene: isDirty,
    note: isNoteDirty,
    material: isMaterialDirty,
  });
  const activeDocumentType = resolveActiveDocumentType(selectedDocumentType);

  const loadProjects = useCallback(async () => {
    setProjectsLoading(true);
    setProjectsError('');

    try {
      const payload = await listProjects();
      setProjects(Array.isArray(payload) ? payload : payload.projects ?? []);
    } catch (error) {
      setProjects([]);
      setProjectsError(error instanceof Error ? error.message : 'Failed to load projects.');
    } finally {
      setProjectsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleSelectProject = useCallback((projectId, options = {}) => {
    if (!projectId || projectId === activeProjectId) {
      return;
    }

    if (
      !options.skipUnsavedConfirmation
      && hasUnsavedDocumentChanges
      && !window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)
    ) {
      return;
    }

    setActiveProjectId(projectId);
  }, [activeProjectId, hasUnsavedDocumentChanges]);

  const handleCreateProject = useCallback(async (title) => {
    const trimmedTitle = typeof title === 'string' ? title.trim() : '';

    if (!trimmedTitle) {
      setCreateProjectError('Enter a project title.');
      setCreateProjectStatus('');
      return false;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_CREATE_MESSAGE)) {
      return false;
    }

    if (isCreatingProject) {
      return false;
    }

    setIsCreatingProject(true);
    setCreateProjectError('');
    setCreateProjectStatus('Creating project...');

    try {
      const metadata = await createProject(trimmedTitle);
      const newProjectId = metadata?.project_id;

      if (!newProjectId) {
        throw new Error('Created project did not return a project ID.');
      }

      await loadProjects();
      setActiveProjectId(newProjectId);
      setCreateProjectStatus('Project created');
      setCreateProjectError('');
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to create project.';
      setCreateProjectError(message);
      setCreateProjectStatus('');
      return false;
    } finally {
      setIsCreatingProject(false);
    }
  }, [hasUnsavedDocumentChanges, isCreatingProject, loadProjects]);

  const handleCreateOmiGuidedProject = useCallback(async ({
    title,
    rawIdea,
    setupNotes,
  } = {}) => {
    if (
      typeof title !== 'string'
      || typeof rawIdea !== 'string'
      || typeof setupNotes !== 'string'
    ) {
      const error = new Error('Guided creation requires a title, setup idea, and setup notes.');
      error.code = 'invalid_guided_creation_request';
      throw error;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_CREATE_MESSAGE)) {
      const error = new Error('Guided project creation was cancelled.');
      error.code = 'guided_creation_cancelled';
      throw error;
    }

    if (isCreatingProject) {
      const error = new Error('Guided project creation is already in progress.');
      error.code = 'guided_creation_pending';
      throw error;
    }

    setIsCreatingProject(true);
    setCreateProjectError('');
    setCreateProjectStatus('Creating guided project...');

    try {
      const response = await createOmiGuidedProject({ title, rawIdea, setupNotes });
      const metadata = requireCompleteOmiGuidedProjectResponse(response);
      const newProjectId = response.project_id;

      setProjects((currentProjects) => (
        upsertGuidedProjectMetadata(currentProjects, metadata)
      ));
      handleSelectProject(newProjectId, { skipUnsavedConfirmation: true });
      setCreateProjectStatus('Guided project created');
      setCreateProjectError('');
      return { success: true, projectId: newProjectId, response };
    } catch (error) {
      const message = error instanceof Error
        ? error.message
        : 'Failed to create guided project.';
      setCreateProjectError(message);
      setCreateProjectStatus('');
      throw error;
    } finally {
      setIsCreatingProject(false);
    }
  }, [handleSelectProject, hasUnsavedDocumentChanges, isCreatingProject]);

  useEffect(() => {
    let isMounted = true;

    setSelectedSceneId('');
    setSelectedStoryCheckSourceId('');
    setSelectedStoryCheckSource(null);
    setStoryCheckSourceStatus('Story Check requires a selected owner-authored source.');
    setStoryCheckSourceError('');
    setSceneContent('');
    setLastSavedContent('');
    setAnalysisReport(null);
    setSaveStatus('');
    setSelectedDocumentType('');
    setSelectedNoteId('');
    setSelectedMaterialId('');
    setNoteContent('');
    setLastSavedNoteContent('');
    setMaterialContent('');
    setLastSavedMaterialContent('');
    setNoteSaveStatus('');
    setMaterialSaveStatus('');
    setNoteError('');
    setMaterialError('');
    setScenes([]);
    setNotes([]);
    setMaterials([]);
    setBibleText('{}');
    setLastSavedBibleText('{}');
    setBibleStatus('Checking availability...');
    setBibleDirectError('');
    setStoryformText('{}');
    setLastSavedStoryformText('{}');
    setStoryformStatus('Checking availability...');
    setStoryformDirectError('');
    setStoryformContext('');
    setStoryformContextDirectError('');
    setContextReadinessLoading(true);
    setContextReadinessError('');
    setBibleReadinessState('loading');
    setBibleReadinessReason('');
    setStoryformReadinessState('loading');
    setStoryformReadinessReason('');
    setStoryformContextReadinessState('loading');
    setStoryformContextReadinessReason('');
    setIsRetryingContextReadiness(false);
    setOmiData({ index: null, ideas: [], candidates: [], promotions: [] });
    setOmiStatus('Loading OMI status...');
    setOmiError('');
    setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW);

    projectGenRef.current += 1;
    setIsSavingStoryform(false);

    async function loadInitialData() {
      const capturedProjectId = activeProjectId;
      setContextReadinessLoading(true);
      setContextReadinessError('');
      setBibleReadinessState('loading');
      setStoryformReadinessState('loading');
      setStoryformContextReadinessState('loading');
      setBibleDirectError('');
      setStoryformDirectError('');
      setStoryformContextDirectError('');
      setIsLoadingScenes(true);
      setIsLoadingNotes(true);
      setIsLoadingMaterials(true);
      setIsLoadingOMI(true);
      setSceneError('');
      setNotesError('');
      setMaterialsError('');

      const unrelatedSettled = Promise.allSettled([
        fetchScenes(capturedProjectId),
        fetchNotes(capturedProjectId),
        fetchMaterials(capturedProjectId),
        getOMI(capturedProjectId),
      ]);

      unrelatedSettled.then((results) => {
        const [sceneResult, notesResult, materialsResult, omiResult] = results;
        if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
          return;
        }

        if (sceneResult.status === 'fulfilled') {
          const scenePayload = sceneResult.value;
          setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? []);
        } else {
          const message = sceneResult.reason instanceof Error
            ? sceneResult.reason.message
            : 'Failed to load scenes.';
          setSceneError(message);
        }

        if (notesResult.status === 'fulfilled') {
          const notesPayload = notesResult.value;
          setNotes(notesPayload?.notes ?? []);
        } else {
          const message = notesResult.reason instanceof Error
            ? notesResult.reason.message
            : 'Failed to load notes.';
          setNotesError(message);
        }

        if (materialsResult.status === 'fulfilled') {
          const materialsPayload = materialsResult.value;
          setMaterials(materialsPayload?.materials ?? []);
        } else {
          const message = materialsResult.reason instanceof Error
            ? materialsResult.reason.message
            : 'Failed to load materials.';
          setMaterialsError(message);
        }

        if (omiResult.status === 'fulfilled') {
          const omiPayload = omiResult.value;
          setOmiData(omiPayload);
          setOmiStatus('Ready');
        } else {
          const message = omiResult.reason instanceof Error
            ? omiResult.reason.message
            : 'Failed to load OMI data.';
          setOmiData({ index: null, ideas: [], candidates: [], promotions: [] });
          setOmiStatus('Load failed');
          setOmiError(message);
        }

        setIsLoadingScenes(false);
        setIsLoadingNotes(false);
        setIsLoadingMaterials(false);
        setIsLoadingOMI(false);
      });

      try {
        const readiness = await fetchProjectContextReadiness(capturedProjectId);
        if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
          return;
        }

        const bibleRes = readiness.resources.bible;
        const storyformRes = readiness.resources.storyform;
        const contextRes = readiness.resources.storyform_context;

        setBibleReadinessState(bibleRes.state);
        setBibleReadinessReason(bibleRes.reason_code || '');
        setStoryformReadinessState(storyformRes.state);
        setStoryformReadinessReason(storyformRes.reason_code || '');
        setStoryformContextReadinessState(contextRes.state);
        setStoryformContextReadinessReason(contextRes.reason_code || '');

        if (bibleRes.ready && bibleRes.state === 'ready') {
          try {
            const biblePayload = await fetchBible(capturedProjectId);
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            const formattedBible = formatJson(biblePayload);
            setBibleText(formattedBible);
            setLastSavedBibleText(formattedBible);
            setBibleStatus('Saved');
          } catch (error) {
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            const message = error instanceof Error ? error.message : 'Failed to load Bible.';
            setBibleText('{}');
            setLastSavedBibleText('{}');
            setBibleStatus(`Failed to load Bible: ${message}`);
            setBibleDirectError(message);
          }
        } else if (bibleRes.state === 'absent') {
          setBibleText('{}');
          setLastSavedBibleText('{}');
          setBibleStatus('No Bible stored for this project.');
        } else if (bibleRes.state === 'invalid') {
          setBibleText('{}');
          setLastSavedBibleText('{}');
          const reasonMsg = bibleRes.diagnostics && bibleRes.diagnostics[0]
            ? bibleRes.diagnostics[0]
            : 'Bible resource is invalid.';
          setBibleStatus(`Bible not available: ${reasonMsg}`);
        } else {
          setBibleText('{}');
          setLastSavedBibleText('{}');
          setBibleStatus('Bible is not available.');
        }

        if (storyformRes.ready && storyformRes.state === 'ready') {
          try {
            const storyformPayload = await fetchStoryform(capturedProjectId);
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            const formattedStoryform = formatJson(storyformPayload);
            setStoryformText(formattedStoryform);
            setLastSavedStoryformText(formattedStoryform);
            setStoryformStatus('Saved');
          } catch (error) {
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            const message = error instanceof Error ? error.message : 'Failed to load storyform.';
            setStoryformText('{}');
            setLastSavedStoryformText('{}');
            setStoryformStatus(`Failed to load storyform: ${message}`);
            setStoryformDirectError(message);
          }
        } else if (storyformRes.state === 'absent') {
          setStoryformText('{}');
          setLastSavedStoryformText('{}');
          setStoryformStatus('No storyform stored for this project.');
        } else if (storyformRes.state === 'invalid') {
          setStoryformText('{}');
          setLastSavedStoryformText('{}');
          const reasonMsg = storyformRes.diagnostics && storyformRes.diagnostics[0]
            ? storyformRes.diagnostics[0]
            : 'Storyform resource is invalid.';
          setStoryformStatus(`Storyform not available: ${reasonMsg}`);
        } else {
          setStoryformText('{}');
          setLastSavedStoryformText('{}');
          setStoryformStatus('Storyform is not available.');
        }

        if (contextRes.ready && contextRes.state === 'ready') {
          try {
            const contextPayload = await fetchStoryformContext(capturedProjectId);
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            setStoryformContext(contextPayload.context ?? '');
          } catch (error) {
            if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
              return;
            }
            const message = error instanceof Error ? error.message : 'Failed to load storyform context.';
            setStoryformContext('');
            setStoryformContextDirectError(message);
          }
        } else if (contextRes.state === 'unavailable') {
          setStoryformContext('');
        } else {
          setStoryformContext('');
        }

        setContextReadinessLoading(false);
      } catch (error) {
        if (!isMounted || currentProjectIdRef.current !== capturedProjectId) {
          return;
        }
        const message = error instanceof Error ? error.message : 'Failed to check context availability.';
        setContextReadinessError(message);
        setBibleReadinessState('error');
        setStoryformReadinessState('error');
        setStoryformContextReadinessState('error');
        setBibleStatus('Availability could not be checked.');
        setStoryformStatus('Availability could not be checked.');
        setStoryformContext('');
        setContextReadinessLoading(false);
      }
    }

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [activeProjectId]);

  useEffect(() => {
    if (!selectedStoryCheckSourceId) {
      return;
    }

    const sourceStillBelongsToProject = scenes.some((scene) => {
      if (typeof scene === 'string') {
        return scene === selectedStoryCheckSourceId;
      }

      const sceneId = scene?.scene_id ?? scene?.sceneId ?? scene?.id ?? scene?.name;
      return sceneId === selectedStoryCheckSourceId;
    });

    if (!sourceStillBelongsToProject) {
      setSelectedStoryCheckSourceId('');
      setSelectedStoryCheckSource(null);
      setStoryCheckSourceStatus('Story Check requires a selected owner-authored source.');
    }
  }, [scenes, selectedStoryCheckSourceId]);

  const handleSelectOverview = useCallback(() => {
    if (activeWorkspaceView === WORKSPACE_VIEWS.OVERVIEW) {
      return;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)) {
      return;
    }

    setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW);
  }, [activeWorkspaceView, hasUnsavedDocumentChanges]);

  const handleSelectMemoryCanon = useCallback(() => {
    if (activeWorkspaceView === WORKSPACE_VIEWS.MEMORY_CANON) {
      return;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)) {
      return;
    }

    setActiveWorkspaceView(WORKSPACE_VIEWS.MEMORY_CANON);
  }, [activeWorkspaceView, hasUnsavedDocumentChanges]);

  const handleSelectOMIDashboard = useCallback(() => {
    if (activeWorkspaceView === WORKSPACE_VIEWS.OMI_DASHBOARD) {
      return;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)) {
      return;
    }

    setActiveWorkspaceView(WORKSPACE_VIEWS.OMI_DASHBOARD);
  }, [activeWorkspaceView, hasUnsavedDocumentChanges]);

  const handleOpenEditorWorkspace = useCallback(() => {
    setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
  }, []);

  const refreshOMI = useCallback(async () => {
    setIsLoadingOMI(true);
    setOmiError('');

    try {
      const payload = await getOMI(activeProjectId);
      setOmiData(payload);
      setOmiStatus('Ready');
      return payload;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load OMI data.';
      setOmiError(message);
      setOmiStatus('Load failed');
      throw error;
    } finally {
      setIsLoadingOMI(false);
    }
  }, [activeProjectId]);

  const handleSelectScene = useCallback(async (sceneId) => {
    if (selectedDocumentType === DOCUMENT_TYPES.SCENE && sceneId === selectedSceneId) {
      return;
    }

    if (
      hasUnsavedDocumentChanges
      && !window.confirm(getDocumentSwitchMessage(DOCUMENT_TYPES.SCENE, DOCUMENT_SWITCH_MESSAGES))
    ) {
      return;
    }

    setSelectedDocumentType(DOCUMENT_TYPES.SCENE);
    setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
    setSelectedSceneId(sceneId);
    setSceneContent('');
    setLastSavedContent('');
    setAnalysisReport(null);
    setSaveStatus('');
    setSceneError('');
    setIsLoadingScene(true);

    try {
      const data = await fetchScene(sceneId, activeProjectId);
      const loadedContent = getDocumentResponseContent(data);
      setSceneContent(loadedContent);
      setLastSavedContent(loadedContent);
      setSaveStatus('Saved');
    } catch (error) {
      setSceneError(error instanceof Error ? error.message : 'Failed to load scene.');
      setSelectedSceneId('');
      setSceneContent('');
      setLastSavedContent('');
    } finally {
      setIsLoadingScene(false);
    }
  }, [activeProjectId, hasUnsavedDocumentChanges, selectedDocumentType, selectedSceneId]);

  const handleSceneContentChange = useCallback((nextContent) => {
    setSceneContent(nextContent);
    setSaveStatus((currentStatus) => (
      currentStatus.startsWith('Save failed') ? 'Unsaved changes' : currentStatus
    ));
  }, []);

  const handleSelectNote = useCallback(async (noteId) => {
    if (!noteId || (selectedDocumentType === DOCUMENT_TYPES.NOTE && noteId === selectedNoteId)) {
      return;
    }

    if (
      hasUnsavedDocumentChanges
      && !window.confirm(getDocumentSwitchMessage(DOCUMENT_TYPES.NOTE, DOCUMENT_SWITCH_MESSAGES))
    ) {
      return;
    }

    setSelectedDocumentType(DOCUMENT_TYPES.NOTE);
    setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
    setSelectedNoteId(noteId);
    setNoteContent('');
    setLastSavedNoteContent('');
    setNoteSaveStatus('');
    setNoteError('');
    setIsLoadingNote(true);

    try {
      const data = await fetchNote(noteId, activeProjectId);
      const loadedContent = getDocumentResponseContent(data);
      setNoteContent(loadedContent);
      setLastSavedNoteContent(loadedContent);
      setNoteSaveStatus('Saved');
    } catch (error) {
      setNoteError(error instanceof Error ? error.message : 'Failed to load note.');
      setSelectedNoteId('');
      setNoteContent('');
      setLastSavedNoteContent('');
    } finally {
      setIsLoadingNote(false);
    }
  }, [activeProjectId, hasUnsavedDocumentChanges, selectedDocumentType, selectedNoteId]);

  const handleSelectMaterial = useCallback(async (materialId) => {
    if (
      !materialId
      || (
        selectedDocumentType === DOCUMENT_TYPES.MATERIAL
        && materialId === selectedMaterialId
      )
    ) {
      return;
    }

    if (
      hasUnsavedDocumentChanges
      && !window.confirm(getDocumentSwitchMessage(DOCUMENT_TYPES.MATERIAL, DOCUMENT_SWITCH_MESSAGES))
    ) {
      return;
    }

    setSelectedDocumentType(DOCUMENT_TYPES.MATERIAL);
    setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
    setSelectedMaterialId(materialId);
    setMaterialContent('');
    setLastSavedMaterialContent('');
    setMaterialSaveStatus('');
    setMaterialError('');
    setIsLoadingMaterial(true);

    try {
      const data = await fetchMaterial(materialId, activeProjectId);
      const loadedContent = getDocumentResponseContent(data);
      setMaterialContent(loadedContent);
      setLastSavedMaterialContent(loadedContent);
      setMaterialSaveStatus('Saved');
    } catch (error) {
      setMaterialError(error instanceof Error ? error.message : 'Failed to load material.');
      setSelectedMaterialId('');
      setMaterialContent('');
      setLastSavedMaterialContent('');
    } finally {
      setIsLoadingMaterial(false);
    }
  }, [activeProjectId, hasUnsavedDocumentChanges, selectedDocumentType, selectedMaterialId]);

  const handleNoteContentChange = useCallback((nextContent) => {
    setNoteContent(nextContent);
    setNoteSaveStatus((currentStatus) => (
      currentStatus.startsWith('Save failed') ? 'Unsaved changes' : currentStatus
    ));
  }, []);

  const handleMaterialContentChange = useCallback((nextContent) => {
    setMaterialContent(nextContent);
    setMaterialSaveStatus((currentStatus) => (
      currentStatus.startsWith('Save failed') ? 'Unsaved changes' : currentStatus
    ));
  }, []);

  const handleSaveNote = useCallback(async () => {
    if (!selectedNoteId || isSavingNote) {
      return;
    }

    setIsSavingNote(true);
    setNoteSaveStatus('');

    try {
      await saveNote(selectedNoteId, noteContent, activeProjectId);
      const reloaded = await reloadProjectScopedNotesMaterials(activeProjectId, {
        noteId: selectedNoteId,
      });
      const reloadedContent = getDocumentResponseContent(reloaded.note);
      setNotes(reloaded.notes);
      setMaterials(reloaded.materials);
      setNoteContent(reloadedContent);
      setLastSavedNoteContent(reloadedContent);
      setNoteSaveStatus('Saved and reloaded owner-authored note; not canon by default.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setNoteSaveStatus(`Save failed: ${message}`);
    } finally {
      setIsSavingNote(false);
    }
  }, [activeProjectId, isSavingNote, noteContent, selectedNoteId]);

  const handleSaveMaterial = useCallback(async () => {
    if (!selectedMaterialId || isSavingMaterial) {
      return;
    }

    setIsSavingMaterial(true);
    setMaterialSaveStatus('');

    try {
      await saveMaterial(selectedMaterialId, materialContent, activeProjectId);
      const reloaded = await reloadProjectScopedNotesMaterials(activeProjectId, {
        materialId: selectedMaterialId,
      });
      const reloadedContent = getDocumentResponseContent(reloaded.material);
      setNotes(reloaded.notes);
      setMaterials(reloaded.materials);
      setMaterialContent(reloadedContent);
      setLastSavedMaterialContent(reloadedContent);
      setMaterialSaveStatus('Saved and reloaded owner-provided material; not canon by default.');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setMaterialSaveStatus(`Save failed: ${message}`);
    } finally {
      setIsSavingMaterial(false);
    }
  }, [activeProjectId, isSavingMaterial, materialContent, selectedMaterialId]);

  const handleCreateOwnerAuthoredNote = useCallback(async ({ noteId, content }) => {
    if (
      hasUnsavedDocumentChanges
      && !window.confirm(getDocumentSwitchMessage(DOCUMENT_TYPES.NOTE, DOCUMENT_SWITCH_MESSAGES))
    ) {
      return false;
    }

    setNotesError('');
    setNoteError('');
    setNoteSaveStatus('Creating owner-authored note...');

    try {
      const note = await createOwnerAuthoredNote(activeProjectId, { noteId, content });
      const reloaded = await reloadProjectScopedNotesMaterials(activeProjectId, {
        noteId: note.note_id,
      });
      const reloadedContent = getDocumentResponseContent(reloaded.note);
      setNotes(reloaded.notes);
      setMaterials(reloaded.materials);
      setSelectedDocumentType(DOCUMENT_TYPES.NOTE);
      setSelectedNoteId(note.note_id);
      setNoteContent(reloadedContent);
      setLastSavedNoteContent(reloadedContent);
      setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
      setNoteSaveStatus('Created, saved, and reloaded owner-authored note; not canon by default.');
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Create note failed.';
      setNoteError(message);
      setNoteSaveStatus(`Save failed: ${message}`);
      return false;
    }
  }, [activeProjectId, hasUnsavedDocumentChanges]);

  const handleCreateOwnerProvidedMaterial = useCallback(async ({ materialId, content }) => {
    if (
      hasUnsavedDocumentChanges
      && !window.confirm(getDocumentSwitchMessage(DOCUMENT_TYPES.MATERIAL, DOCUMENT_SWITCH_MESSAGES))
    ) {
      return false;
    }

    setMaterialsError('');
    setMaterialError('');
    setMaterialSaveStatus('Creating owner-provided material...');

    try {
      const material = await createOwnerProvidedMaterial(activeProjectId, { materialId, content });
      const reloaded = await reloadProjectScopedNotesMaterials(activeProjectId, {
        materialId: material.material_id,
      });
      const reloadedContent = getDocumentResponseContent(reloaded.material);
      setNotes(reloaded.notes);
      setMaterials(reloaded.materials);
      setSelectedDocumentType(DOCUMENT_TYPES.MATERIAL);
      setSelectedMaterialId(material.material_id);
      setMaterialContent(reloadedContent);
      setLastSavedMaterialContent(reloadedContent);
      setActiveWorkspaceView(WORKSPACE_VIEWS.EDITOR);
      setMaterialSaveStatus('Created, saved, and reloaded owner-provided material; not canon by default.');
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Create material failed.';
      setMaterialError(message);
      setMaterialSaveStatus(`Save failed: ${message}`);
      return false;
    }
  }, [activeProjectId, hasUnsavedDocumentChanges]);

  const handleBibleTextChange = useCallback((nextText) => {
    setBibleText(nextText);
    setBibleStatus(nextText === lastSavedBibleText ? 'Saved' : 'Unsaved changes');
  }, [lastSavedBibleText]);

  const handleStoryformTextChange = useCallback((nextText) => {
    setStoryformText(nextText);
    setStoryformStatus(nextText === lastSavedStoryformText ? 'Saved' : 'Unsaved changes');
  }, [lastSavedStoryformText]);

  useEffect(() => {
    function handleBeforeUnload(event) {
      if (!hasUnsavedDocumentChanges) {
        return;
      }

      event.preventDefault();
      event.returnValue = '';
    }

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedDocumentChanges]);

  const handleSave = useCallback(async () => {
    if (!selectedSceneId || isSaving) {
      return;
    }

    setIsSaving(true);
    setSaveStatus('');

    try {
      await saveScene(selectedSceneId, sceneContent, activeProjectId);
      setLastSavedContent(sceneContent);
      setSaveStatus('Saved');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setSaveStatus(`Save failed: ${message}`);
    } finally {
      setIsSaving(false);
    }
  }, [activeProjectId, isSaving, sceneContent, selectedSceneId]);

  const handleCreateOrImportStoryCheckSource = useCallback(async ({ sourceId, content }) => {
    if (isImportingStoryCheckSource) {
      return false;
    }

    setIsImportingStoryCheckSource(true);
    setStoryCheckSourceError('');
    setStoryCheckSourceStatus('Saving owner-authored source...');

    try {
      const source = await createOrImportOwnerAuthoredSource(activeProjectId, {
        sourceId,
        content,
      });
      const refreshedScenes = await fetchScenes(activeProjectId);
      setScenes(Array.isArray(refreshedScenes) ? refreshedScenes : refreshedScenes.scenes ?? []);
      const selectedSource = selectStoryCheckSource(activeProjectId, source.source_id);
      setSelectedStoryCheckSourceId(selectedSource.source_id);
      setSelectedStoryCheckSource(selectedSource);
      setStoryCheckSourceStatus(
        'Selected owner-authored source saved as the project-scoped selected source for Story Check.',
      );
      return true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Source import failed.';
      setStoryCheckSourceError(message);
      setStoryCheckSourceStatus('Story Check requires a selected owner-authored source.');
      return false;
    } finally {
      setIsImportingStoryCheckSource(false);
    }
  }, [activeProjectId, isImportingStoryCheckSource]);

  const handleSelectStoryCheckSource = useCallback((sourceId) => {
    if (!sourceId) {
      setSelectedStoryCheckSourceId('');
      setSelectedStoryCheckSource(null);
      setStoryCheckSourceStatus('Story Check requires a selected owner-authored source.');
      return;
    }

    try {
      const selectedSource = selectStoryCheckSource(activeProjectId, sourceId);
      setSelectedStoryCheckSourceId(selectedSource.source_id);
      setSelectedStoryCheckSource(selectedSource);
      setStoryCheckSourceError('');
      setStoryCheckSourceStatus(
        'Selected owner-authored source is the project-scoped selected source for Story Check.',
      );
    } catch (error) {
      setSelectedStoryCheckSourceId('');
      setSelectedStoryCheckSource(null);
      setStoryCheckSourceError(
        error instanceof Error ? error.message : 'Source selection failed.',
      );
      setStoryCheckSourceStatus('Story Check requires a selected owner-authored source.');
    }
  }, [activeProjectId]);

  const handleSaveBible = useCallback(async () => {
    if (isSavingBible) {
      return;
    }

    setIsSavingBible(true);

    try {
      const parsed = parseJsonObject(bibleText, 'Bible');
      await saveBible(parsed, activeProjectId);
      const formatted = formatJson(parsed);
      setBibleText(formatted);
      setLastSavedBibleText(formatted);
      setBibleStatus('Saved');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setBibleStatus(`Save failed: ${message}`);
    } finally {
      setIsSavingBible(false);
    }
  }, [activeProjectId, bibleText, isSavingBible]);

  const handleSaveStoryform = useCallback(async () => {
    if (isSavingStoryform) {
      return;
    }

    const saveGuard = createOperationGuard(() => ({
      projectId: currentProjectIdRef.current,
      generation: projectGenRef.current,
    }));
    setIsSavingStoryform(true);

    try {
      const parsed = parseJsonObject(storyformText, 'Storyform');
      await saveStoryform(parsed, saveGuard.session.projectId);

      if (!saveGuard.isCurrent()) {
        return;
      }

      const formatted = formatJson(parsed);
      setStoryformText(formatted);
      setLastSavedStoryformText(formatted);
      setStoryformStatus('Saved');
      setStoryformDirectError('');

      try {
        const readiness = await fetchProjectContextReadiness(saveGuard.session.projectId);

        if (!saveGuard.isCurrent()) {
          return;
        }

        const contextRes = readiness.resources.storyform_context;

        setStoryformContextReadinessState(contextRes.state);
        setStoryformContextReadinessReason(contextRes.reason_code || '');

        if (contextRes.ready && contextRes.state === 'ready') {
          try {
            const contextPayload = await fetchStoryformContext(saveGuard.session.projectId);

            if (!saveGuard.isCurrent()) {
              return;
            }

            setStoryformContext(contextPayload.context ?? '');
            setStoryformContextDirectError('');
          } catch (error) {
            if (!saveGuard.isCurrent()) {
              return;
            }
            const message = error instanceof Error ? error.message : 'Failed to load storyform context.';
            setStoryformContext('');
            setStoryformContextDirectError(message);
          }
        } else if (contextRes.state === 'unavailable') {
          setStoryformContext('');
          setStoryformContextDirectError('');
        } else {
          setStoryformContext('');
        }
        setContextReadinessError('');
      } catch (error) {
        if (!saveGuard.isCurrent()) {
          return;
        }
        const message = error instanceof Error ? error.message : 'Failed to check context availability.';
        setContextReadinessError(message);
        setStoryformContext('');
        setStoryformContextDirectError('');
      }
    } catch (error) {
      if (!saveGuard.isCurrent()) {
        return;
      }
      const message = error instanceof Error ? error.message : 'Save failed.';
      setStoryformStatus(`Save failed: ${message}`);
    } finally {
      if (saveGuard.isCurrent()) {
        setIsSavingStoryform(false);
      }
    }
  }, [activeProjectId, isSavingStoryform, storyformText]);

  const handleRetryContextReadiness = useCallback(async () => {
    if (isRetryingContextReadiness) {
      return;
    }

    const retryGuard = createOperationGuard(() => ({
      projectId: currentProjectIdRef.current,
      generation: projectGenRef.current,
    }));
    setIsRetryingContextReadiness(true);
    setContextReadinessError('');
    setBibleDirectError('');
    setStoryformDirectError('');
    setStoryformContextDirectError('');
    setContextReadinessLoading(true);
    setBibleReadinessState('loading');
    setStoryformReadinessState('loading');
    setStoryformContextReadinessState('loading');
    setBibleStatus('Checking availability...');
    setStoryformStatus('Checking availability...');

    try {
      const readiness = await fetchProjectContextReadiness(retryGuard.session.projectId);

      if (!retryGuard.isCurrent()) {
        return;
      }

      const bibleRes = readiness.resources.bible;
      const storyformRes = readiness.resources.storyform;
      const contextRes = readiness.resources.storyform_context;

      setBibleReadinessState(bibleRes.state);
      setBibleReadinessReason(bibleRes.reason_code || '');
      setStoryformReadinessState(storyformRes.state);
      setStoryformReadinessReason(storyformRes.reason_code || '');
      setStoryformContextReadinessState(contextRes.state);
      setStoryformContextReadinessReason(contextRes.reason_code || '');

      if (bibleRes.ready && bibleRes.state === 'ready') {
        try {
          const biblePayload = await fetchBible(retryGuard.session.projectId);
          if (!retryGuard.isCurrent()) {
            return;
          }
          const formattedBible = formatJson(biblePayload);
          setBibleText(formattedBible);
          setLastSavedBibleText(formattedBible);
          setBibleStatus('Saved');
        } catch (error) {
          if (!retryGuard.isCurrent()) {
            return;
          }
          const message = error instanceof Error ? error.message : 'Failed to load Bible.';
          setBibleText('{}');
          setLastSavedBibleText('{}');
          setBibleStatus(`Failed to load Bible: ${message}`);
          setBibleDirectError(message);
        }
      } else if (bibleRes.state === 'absent') {
        setBibleText('{}');
        setLastSavedBibleText('{}');
        setBibleStatus('No Bible stored for this project.');
      } else if (bibleRes.state === 'invalid') {
        setBibleText('{}');
        setLastSavedBibleText('{}');
        const reasonMsg = bibleRes.diagnostics && bibleRes.diagnostics[0]
          ? bibleRes.diagnostics[0]
          : 'Bible resource is invalid.';
        setBibleStatus(`Bible not available: ${reasonMsg}`);
      } else {
        setBibleText('{}');
        setLastSavedBibleText('{}');
        setBibleStatus('Bible is not available.');
      }

      if (storyformRes.ready && storyformRes.state === 'ready') {
        try {
          const storyformPayload = await fetchStoryform(retryGuard.session.projectId);
          if (!retryGuard.isCurrent()) {
            return;
          }
          const formattedStoryform = formatJson(storyformPayload);
          setStoryformText(formattedStoryform);
          setLastSavedStoryformText(formattedStoryform);
          setStoryformStatus('Saved');
        } catch (error) {
          if (!retryGuard.isCurrent()) {
            return;
          }
          const message = error instanceof Error ? error.message : 'Failed to load storyform.';
          setStoryformText('{}');
          setLastSavedStoryformText('{}');
          setStoryformStatus(`Failed to load storyform: ${message}`);
          setStoryformDirectError(message);
        }
      } else if (storyformRes.state === 'absent') {
        setStoryformText('{}');
        setLastSavedStoryformText('{}');
        setStoryformStatus('No storyform stored for this project.');
      } else if (storyformRes.state === 'invalid') {
        setStoryformText('{}');
        setLastSavedStoryformText('{}');
        const reasonMsg = storyformRes.diagnostics && storyformRes.diagnostics[0]
          ? storyformRes.diagnostics[0]
          : 'Storyform resource is invalid.';
        setStoryformStatus(`Storyform not available: ${reasonMsg}`);
      } else {
        setStoryformText('{}');
        setLastSavedStoryformText('{}');
        setStoryformStatus('Storyform is not available.');
      }

      if (contextRes.ready && contextRes.state === 'ready') {
        try {
          const contextPayload = await fetchStoryformContext(retryGuard.session.projectId);
          if (!retryGuard.isCurrent()) {
            return;
          }
          setStoryformContext(contextPayload.context ?? '');
          setStoryformContextDirectError('');
        } catch (error) {
          if (!retryGuard.isCurrent()) {
            return;
          }
          const message = error instanceof Error ? error.message : 'Failed to load storyform context.';
          setStoryformContext('');
          setStoryformContextDirectError(message);
        }
      } else {
        setStoryformContext('');
        setStoryformContextDirectError('');
      }

      setContextReadinessError('');
    } catch (error) {
      if (!retryGuard.isCurrent()) {
        return;
      }
      const message = error instanceof Error ? error.message : 'Failed to check context availability.';
      setContextReadinessError(message);
      setBibleReadinessState('error');
      setStoryformReadinessState('error');
      setStoryformContextReadinessState('error');
      setBibleText('{}');
      setLastSavedBibleText('{}');
      setBibleStatus('Availability could not be checked.');
      setStoryformText('{}');
      setLastSavedStoryformText('{}');
      setStoryformStatus('Availability could not be checked.');
      setStoryformContext('');
    } finally {
      if (retryGuard.isCurrent()) {
        setContextReadinessLoading(false);
        setIsRetryingContextReadiness(false);
      }
    }
  }, [activeProjectId, isRetryingContextReadiness]);

  const handleCreateOMIIdea = useCallback(async (rawIdea) => {
    if (isCreatingOMIIdea) {
      return null;
    }

    setIsCreatingOMIIdea(true);
    setOmiError('');
    setOmiStatus('Creating idea...');

    try {
      const idea = await createOMIIdea(activeProjectId, { raw_idea: rawIdea });
      await refreshOMI();
      setOmiStatus('Idea created');
      return idea;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Create idea failed.';
      setOmiError(message);
      setOmiStatus('Error');
      throw error;
    } finally {
      setIsCreatingOMIIdea(false);
    }
  }, [activeProjectId, isCreatingOMIIdea, refreshOMI]);

  const handleCreateOMICandidate = useCallback(async (payload) => {
    if (isCreatingOMICandidate) {
      return null;
    }

    setIsCreatingOMICandidate(true);
    setOmiError('');
    setOmiStatus('Creating candidate...');

    try {
      const candidate = await createOMICandidate(activeProjectId, payload);
      await refreshOMI();
      setOmiStatus('Candidate created');
      return candidate;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Create candidate failed.';
      setOmiError(message);
      setOmiStatus('Error');
      throw error;
    } finally {
      setIsCreatingOMICandidate(false);
    }
  }, [activeProjectId, isCreatingOMICandidate, refreshOMI]);

  const handleUpdateOMIIdeaDecision = useCallback(async (ideaId, payload) => {
    if (isUpdatingOMI) {
      return null;
    }

    setIsUpdatingOMI(true);
    setOmiError('');
    setOmiStatus('Updating idea...');

    try {
      const idea = await updateOMIIdeaDecision(activeProjectId, ideaId, payload);
      await refreshOMI();
      setOmiStatus('Idea updated');
      return idea;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Idea update failed.';
      setOmiError(message);
      setOmiStatus('Error');
      throw error;
    } finally {
      setIsUpdatingOMI(false);
    }
  }, [activeProjectId, isUpdatingOMI, refreshOMI]);

  const handleUpdateOMICandidateDecision = useCallback(async (candidateId, payload) => {
    if (isUpdatingOMI) {
      return null;
    }

    setIsUpdatingOMI(true);
    setOmiError('');
    setOmiStatus('Updating candidate...');

    try {
      const candidate = await updateOMICandidateDecision(activeProjectId, candidateId, payload);
      await refreshOMI();
      setOmiStatus('Candidate updated');
      return candidate;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Candidate update failed.';
      setOmiError(message);
      setOmiStatus('Error');
      throw error;
    } finally {
      setIsUpdatingOMI(false);
    }
  }, [activeProjectId, isUpdatingOMI, refreshOMI]);

  const handleCreateOMIPromotion = useCallback(async (payload) => {
    if (isCreatingOMIPromotion) {
      return null;
    }

    setIsCreatingOMIPromotion(true);
    setOmiError('');
    setOmiStatus('Creating promotion record...');

    try {
      const promotion = await createOMIPromotion(activeProjectId, payload);
      await refreshOMI();
      setOmiStatus('Promotion record created');
      return promotion;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Promotion record create failed.';
      setOmiError(message);
      setOmiStatus('Error');
      throw error;
    } finally {
      setIsCreatingOMIPromotion(false);
    }
  }, [activeProjectId, isCreatingOMIPromotion, refreshOMI]);

  useEffect(() => {
    function handleKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        if (activeWorkspaceView !== WORKSPACE_VIEWS.EDITOR) {
          return;
        }
        if (activeDocumentType === DOCUMENT_TYPES.NOTE) {
          handleSaveNote();
          return;
        }
        if (activeDocumentType === DOCUMENT_TYPES.MATERIAL) {
          handleSaveMaterial();
          return;
        }
        handleSave();
      }
    }

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeDocumentType, activeWorkspaceView, handleSave, handleSaveMaterial, handleSaveNote]);

  const handleRunStoryCheck = useCallback(async () => {
    if (!selectedStoryCheckSourceId) {
      setAnalysisReport({
        error: 'Story Check requires a selected owner-authored source.',
      });
      return;
    }

    setIsAnalyzing(true);
    setAnalysisReport(null);

    try {
      const data = await runStoryCheckForSelectedSource({
        projectId: activeProjectId,
        selectedStoryCheckSourceId,
        selectedStoryCheckSource,
      });
      setAnalysisReport({
        ...data,
        ux2_story_check_boundary: {
          source_id: selectedStoryCheckSourceId,
          source_kind: selectedStoryCheckSource?.source_kind ?? 'owner-authored source',
          result_type: 'diagnostic-only analysis-only result',
          model_output_boundary: 'model output is not canon',
          confidence_boundary: 'confidence is not truth',
          approved_memory_boundary: 'output cannot become approved memory automatically',
        },
      });
    } catch (error) {
      setAnalysisReport({
        error: error instanceof Error ? error.message : 'Story check failed.',
        ux2_story_check_boundary: {
          source_id: selectedStoryCheckSourceId,
          source_kind: selectedStoryCheckSource?.source_kind ?? 'owner-authored source',
          result_type: 'diagnostic-only analysis-only result',
          model_output_boundary: 'model output is not canon',
          confidence_boundary: 'confidence is not truth',
          approved_memory_boundary: 'output cannot become approved memory automatically',
        },
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [activeProjectId, selectedStoryCheckSource, selectedStoryCheckSourceId]);

  const sceneDocument = createDocumentDescriptor({
    type: DOCUMENT_TYPES.SCENE,
    id: selectedSceneId,
    content: sceneContent,
    isDirty,
    isLoading: isLoadingScene,
    isSaving,
    error: sceneError,
    saveStatus,
    onChange: handleSceneContentChange,
    onSave: handleSave,
  });
  const noteDocument = createDocumentDescriptor({
    type: DOCUMENT_TYPES.NOTE,
    id: selectedNoteId,
    content: noteContent,
    isDirty: isNoteDirty,
    isLoading: isLoadingNote,
    isSaving: isSavingNote,
    error: noteError,
    saveStatus: noteSaveStatus,
    onChange: handleNoteContentChange,
    onSave: handleSaveNote,
  });
  const materialDocument = createDocumentDescriptor({
    type: DOCUMENT_TYPES.MATERIAL,
    id: selectedMaterialId,
    content: materialContent,
    isDirty: isMaterialDirty,
    isLoading: isLoadingMaterial,
    isSaving: isSavingMaterial,
    error: materialError,
    saveStatus: materialSaveStatus,
    onChange: handleMaterialContentChange,
    onSave: handleSaveMaterial,
  });
  const activeDocument = getActiveDocumentDescriptor(activeDocumentType, {
    [DOCUMENT_TYPES.SCENE]: sceneDocument,
    [DOCUMENT_TYPES.NOTE]: noteDocument,
    [DOCUMENT_TYPES.MATERIAL]: materialDocument,
  });
  const activeEditorDocument =
    activeDocument.type === DOCUMENT_TYPES.NOTE && activeDocument.id
      ? activeDocument
      : activeDocument.type === DOCUMENT_TYPES.MATERIAL && activeDocument.id
        ? activeDocument
        : sceneDocument;
  const activeProject =
    projects.find((project) => (
      project?.project_id === activeProjectId
      || project?.projectId === activeProjectId
      || project?.id === activeProjectId
    )) ?? { project_id: activeProjectId, title: activeProjectId, status: 'Not available' };
  const rawArtifactEvidenceStatus = useMemo(
    () => fetchRawArtifactEvidenceStatus(activeProjectId),
    [activeProjectId],
  );

  return (
    <div className="app-shell">
      <ProjectNav
        activeProjectId={activeProjectId}
        projects={projects}
        projectsLoading={projectsLoading}
        projectsError={projectsError}
        onSelectProject={handleSelectProject}
        onCreateProject={handleCreateProject}
        isCreatingProject={isCreatingProject}
        createProjectError={createProjectError}
        createProjectStatus={createProjectStatus}
        onRefreshProjects={loadProjects}
        scenes={scenes}
        isLoading={isLoadingScenes}
        error={sceneError}
        onSelectScene={handleSelectScene}
        notes={notes}
        materials={materials}
        activeWorkspaceView={activeWorkspaceView}
        onSelectOverview={handleSelectOverview}
        onSelectMemoryCanon={handleSelectMemoryCanon}
        onSelectOMIDashboard={handleSelectOMIDashboard}
        activeDocumentType={activeDocumentType || DEFAULT_DOCUMENT_TYPE}
        activeDocumentId={activeDocument.id}
        isLoadingNotes={isLoadingNotes}
        isLoadingMaterials={isLoadingMaterials}
        notesError={notesError}
        materialsError={materialsError}
        onCreateOwnerAuthoredNote={handleCreateOwnerAuthoredNote}
        onCreateOwnerProvidedMaterial={handleCreateOwnerProvidedMaterial}
        onSelectNote={handleSelectNote}
        onSelectMaterial={handleSelectMaterial}
        selectedStoryCheckSourceId={selectedStoryCheckSourceId}
        storyCheckSourceStatus={storyCheckSourceStatus}
        storyCheckSourceError={storyCheckSourceError}
        isImportingStoryCheckSource={isImportingStoryCheckSource}
        onCreateOrImportStoryCheckSource={handleCreateOrImportStoryCheckSource}
        onSelectStoryCheckSource={handleSelectStoryCheckSource}
      />
      <main className="editor-column" aria-label="Project workspace">
        {activeWorkspaceView === WORKSPACE_VIEWS.OVERVIEW ? (
          <>
            <OmiGuidedProjectCreation
              onCreateGuidedProject={handleCreateOmiGuidedProject}
              disabled={isCreatingProject}
              onCancel={() => {
                setCreateProjectError('');
                setCreateProjectStatus('');
              }}
              onComplete={() => {
                setActiveWorkspaceView(WORKSPACE_VIEWS.OVERVIEW);
              }}
            />
            <ProjectOverview
              project={activeProject}
              scenes={scenes}
              notes={notes}
              materials={materials}
              omiStatus={{
                status: isLoadingOMI ? 'Loading OMI status...' : omiStatus || 'Ready',
                ideas: omiData?.ideas,
                candidates: omiData?.candidates,
              }}
              approvedMemoryStatus="No approved memory/canon items shown here yet."
              onOpenScenes={handleOpenEditorWorkspace}
              onOpenNotes={handleOpenEditorWorkspace}
              onOpenMaterials={handleOpenEditorWorkspace}
              onOpenOmi={handleSelectOMIDashboard}
            />
          </>
        ) : activeWorkspaceView === WORKSPACE_VIEWS.MEMORY_CANON ? (
          <MemoryCanonShell
            projectTitle={activeProject.title}
            approvedRecordsByCategory={{}}
          />
        ) : activeWorkspaceView === WORKSPACE_VIEWS.OMI_DASHBOARD ? (
          <OMIShell
            activeProjectId={activeProjectId}
            projectTitle={activeProject.title}
            omiData={omiData}
            isLoading={isLoadingOMI}
            isUpdating={isUpdatingOMI}
            status={omiStatus}
            error={omiError}
            onUpdateCandidateDecision={handleUpdateOMICandidateDecision}
          />
        ) : (
          <>
            <ProjectContext
              bibleText={bibleText}
              bibleStatus={bibleStatus}
              isSavingBible={isSavingBible}
              onBibleChange={handleBibleTextChange}
              onSaveBible={handleSaveBible}
              storyformText={storyformText}
              storyformStatus={storyformStatus}
              isSavingStoryform={isSavingStoryform}
              onStoryformChange={handleStoryformTextChange}
              onSaveStoryform={handleSaveStoryform}
              storyformContext={storyformContext}
              bibleReadinessState={bibleReadinessState}
              bibleReadinessReason={bibleReadinessReason}
              bibleDirectError={bibleDirectError}
              storyformReadinessState={storyformReadinessState}
              storyformReadinessReason={storyformReadinessReason}
              storyformDirectError={storyformDirectError}
              storyformContextReadinessState={storyformContextReadinessState}
              storyformContextReadinessReason={storyformContextReadinessReason}
              storyformContextDirectError={storyformContextDirectError}
              readinessError={contextReadinessError}
              isLoadingReadiness={contextReadinessLoading}
              isRetryingReadiness={isRetryingContextReadiness}
              onRetryReadiness={handleRetryContextReadiness}
            />

            <OMIPanel
              omiData={omiData}
              isLoading={isLoadingOMI}
              status={omiStatus}
              error={omiError}
              isCreatingIdea={isCreatingOMIIdea}
              isCreatingCandidate={isCreatingOMICandidate}
              isCreatingPromotion={isCreatingOMIPromotion}
              isUpdating={isUpdatingOMI}
              onCreateIdea={handleCreateOMIIdea}
              onCreateCandidate={handleCreateOMICandidate}
              onCreatePromotion={handleCreateOMIPromotion}
              onUpdateIdeaDecision={handleUpdateOMIIdeaDecision}
              onUpdateCandidateDecision={handleUpdateOMICandidateDecision}
            />

            <ReviewQueuePanel projectId={activeProjectId} />

            <Editor
              key={`${activeEditorDocument.type}-${activeEditorDocument.id}`}
              documentType={activeEditorDocument.type}
              content={activeEditorDocument.content}
              disabled={!activeEditorDocument.id || activeEditorDocument.isLoading}
              isDirty={activeEditorDocument.isDirty}
              isLoading={activeEditorDocument.isLoading}
              isSaving={activeEditorDocument.isSaving}
              onChange={activeEditorDocument.onChange}
              onSave={activeEditorDocument.onSave}
              saveDisabled={!canSaveDocument(activeEditorDocument)}
              saveStatus={activeEditorDocument.saveStatus}
              documentError={activeEditorDocument.error}
              selectedDocumentId={activeEditorDocument.id}
            />
          </>
        )}
      </main>
      <AnalysisSidebar
        report={analysisReport}
        selectedSceneId={selectedSceneId}
        selectedStoryCheckSourceId={selectedStoryCheckSourceId}
        selectedStoryCheckSource={selectedStoryCheckSource}
        rawArtifactEvidenceStatus={rawArtifactEvidenceStatus}
        isAnalyzing={isAnalyzing}
        onRunStoryCheck={handleRunStoryCheck}
      />
    </div>
  );
}
