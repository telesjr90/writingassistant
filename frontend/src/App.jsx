import { useCallback, useEffect, useState } from 'react';
import ProjectNav from './components/ProjectNav.jsx';
import Editor from './components/Editor.jsx';
import AnalysisSidebar from './components/AnalysisSidebar.jsx';
import ProjectContext from './components/ProjectContext.jsx';
import OMIPanel from './components/OMIPanel.jsx';
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
  createProject,
  createOMICandidate,
  createOMIIdea,
  createOMIPromotion,
  fetchBible,
  fetchMaterials,
  fetchMaterial,
  fetchNotes,
  fetchNote,
  fetchScene,
  fetchScenes,
  fetchStoryform,
  fetchStoryformContext,
  getOMI,
  listProjects,
  runStoryCheck,
  saveBible,
  saveMaterial,
  saveNote,
  saveScene,
  saveStoryform,
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

export default function App() {
  const [activeProjectId, setActiveProjectId] = useState(PROJECT_ID);
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
  const [bibleText, setBibleText] = useState('{}');
  const [lastSavedBibleText, setLastSavedBibleText] = useState('{}');
  const [storyformText, setStoryformText] = useState('{}');
  const [lastSavedStoryformText, setLastSavedStoryformText] = useState('{}');
  const [omiData, setOmiData] = useState({ index: null, ideas: [], candidates: [] });
  const [analysisReport, setAnalysisReport] = useState(null);
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

  const handleSelectProject = useCallback((projectId) => {
    if (!projectId || projectId === activeProjectId) {
      return;
    }

    if (hasUnsavedDocumentChanges && !window.confirm(UNSAVED_PROJECT_SWITCH_MESSAGE)) {
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

  useEffect(() => {
    let isMounted = true;

    setSelectedSceneId('');
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

    async function loadInitialData() {
      setIsLoadingScenes(true);
      setIsLoadingNotes(true);
      setIsLoadingMaterials(true);
      setSceneError('');
      setNotesError('');
      setMaterialsError('');

      try {
        const [
          scenePayload,
          notesPayload,
          materialsPayload,
          biblePayload,
          storyformPayload,
          contextPayload,
          omiPayload,
        ] = await Promise.all([
          fetchScenes(activeProjectId),
          fetchNotes(activeProjectId),
          fetchMaterials(activeProjectId),
          fetchBible(activeProjectId),
          fetchStoryform(activeProjectId),
          fetchStoryformContext(activeProjectId),
          getOMI(activeProjectId),
        ]);

        if (!isMounted) {
          return;
        }

        setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? []);
        setNotes(notesPayload?.notes ?? []);
        setMaterials(materialsPayload?.materials ?? []);
        const formattedBible = formatJson(biblePayload);
        const formattedStoryform = formatJson(storyformPayload);
        setBibleText(formattedBible);
        setLastSavedBibleText(formattedBible);
        setBibleStatus('Saved');
        setStoryformText(formattedStoryform);
        setLastSavedStoryformText(formattedStoryform);
        setStoryformStatus('Saved');
        setStoryformContext(contextPayload.context ?? '');
        setOmiData(omiPayload);
        setOmiStatus('Ready');
      } catch (error) {
        if (isMounted) {
          const message = error instanceof Error ? error.message : 'Failed to load project data.';
          setSceneError(message);
          setNotesError(message);
          setMaterialsError(message);
        }
      } finally {
        if (isMounted) {
          setIsLoadingScenes(false);
          setIsLoadingNotes(false);
          setIsLoadingMaterials(false);
        }
      }
    }

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [activeProjectId]);

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
      setLastSavedNoteContent(noteContent);
      setNoteSaveStatus('Saved');
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
      setLastSavedMaterialContent(materialContent);
      setMaterialSaveStatus('Saved');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setMaterialSaveStatus(`Save failed: ${message}`);
    } finally {
      setIsSavingMaterial(false);
    }
  }, [activeProjectId, isSavingMaterial, materialContent, selectedMaterialId]);

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

    setIsSavingStoryform(true);

    try {
      const parsed = parseJsonObject(storyformText, 'Storyform');
      await saveStoryform(parsed, activeProjectId);
      const formatted = formatJson(parsed);
      setStoryformText(formatted);
      setLastSavedStoryformText(formatted);
      setStoryformStatus('Saved');

      try {
        const contextPayload = await fetchStoryformContext(activeProjectId);
        setStoryformContext(contextPayload.context ?? '');
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Context refresh failed.';
        setStoryformStatus(`Saved; prompt context refresh failed: ${message}`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setStoryformStatus(`Save failed: ${message}`);
    } finally {
      setIsSavingStoryform(false);
    }
  }, [activeProjectId, isSavingStoryform, storyformText]);

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
  }, [activeDocumentType, handleSave, handleSaveMaterial, handleSaveNote]);

  const handleRunStoryCheck = useCallback(async () => {
    if (!selectedSceneId) {
      return;
    }

    setIsAnalyzing(true);
    setAnalysisReport(null);

    try {
      const data = await runStoryCheck(selectedSceneId, activeProjectId);
      setAnalysisReport(data);
    } catch (error) {
      setAnalysisReport({
        error: error instanceof Error ? error.message : 'Story check failed.',
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [activeProjectId, selectedSceneId]);

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
        selectedSceneId={selectedSceneId}
        isLoading={isLoadingScenes}
        error={sceneError}
        onSelectScene={handleSelectScene}
        notes={notes}
        materials={materials}
        selectedNoteId={selectedNoteId}
        selectedMaterialId={selectedMaterialId}
        activeDocumentType={activeDocumentType || DEFAULT_DOCUMENT_TYPE}
        isLoadingNotes={isLoadingNotes}
        isLoadingMaterials={isLoadingMaterials}
        notesError={notesError}
        materialsError={materialsError}
        onSelectNote={handleSelectNote}
        onSelectMaterial={handleSelectMaterial}
      />
      <main className="editor-column" aria-label="Document editor">
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

        <Editor
          key={`${activeEditorDocument.type}-${activeEditorDocument.id}`}
          documentType={activeEditorDocument.type}
          content={activeEditorDocument.content}
          disabled={!activeEditorDocument.id || activeEditorDocument.isLoading}
          hasUnsavedChanges={activeEditorDocument.isDirty}
          isLoading={activeEditorDocument.isLoading}
          isSaving={activeEditorDocument.isSaving}
          onChange={activeEditorDocument.onChange}
          onSave={activeEditorDocument.onSave}
          saveDisabled={!canSaveDocument(activeEditorDocument)}
          saveStatus={activeEditorDocument.saveStatus}
          documentError={activeEditorDocument.error}
          selectedDocumentId={activeEditorDocument.id}
        />
      </main>
      <AnalysisSidebar
        report={analysisReport}
        selectedSceneId={selectedSceneId}
        isAnalyzing={isAnalyzing}
        onRunStoryCheck={handleRunStoryCheck}
      />
    </div>
  );
}
