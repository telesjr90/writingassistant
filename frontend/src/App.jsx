import { useCallback, useEffect, useState } from 'react';
import ProjectNav from './components/ProjectNav.jsx';
import Editor from './components/Editor.jsx';
import AnalysisSidebar from './components/AnalysisSidebar.jsx';
import ProjectContext from './components/ProjectContext.jsx';
import OMIPanel from './components/OMIPanel.jsx';
import {
  PROJECT_ID,
  createOMICandidate,
  createOMIIdea,
  fetchBible,
  fetchScene,
  fetchScenes,
  fetchStoryform,
  fetchStoryformContext,
  getOMI,
  runStoryCheck,
  saveBible,
  saveScene,
  saveStoryform,
} from './api.js';

const UNSAVED_CHANGES_MESSAGE = 'Discard unsaved changes and load another scene?';

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
  const [saveStatus, setSaveStatus] = useState('');
  const [bibleStatus, setBibleStatus] = useState('');
  const [storyformStatus, setStoryformStatus] = useState('');
  const [omiStatus, setOmiStatus] = useState('');
  const [omiError, setOmiError] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const isDirty = selectedSceneId !== '' && sceneContent !== lastSavedContent;

  useEffect(() => {
    let isMounted = true;

    async function loadInitialData() {
      setIsLoadingScenes(true);
      setSceneError('');

      try {
        const [scenePayload, biblePayload, storyformPayload, contextPayload, omiPayload] = await Promise.all([
          fetchScenes(),
          fetchBible(),
          fetchStoryform(),
          fetchStoryformContext(),
          getOMI(PROJECT_ID),
        ]);

        if (!isMounted) {
          return;
        }

        setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? []);
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
          setSceneError(error instanceof Error ? error.message : 'Failed to load project data.');
        }
      } finally {
        if (isMounted) {
          setIsLoadingScenes(false);
        }
      }
    }

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, []);

  const refreshOMI = useCallback(async () => {
    setIsLoadingOMI(true);
    setOmiError('');

    try {
      const payload = await getOMI(PROJECT_ID);
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
  }, []);

  const handleSelectScene = useCallback(async (sceneId) => {
    if (sceneId === selectedSceneId) {
      return;
    }

    if (isDirty && !window.confirm(UNSAVED_CHANGES_MESSAGE)) {
      return;
    }

    setSelectedSceneId(sceneId);
    setSceneContent('');
    setLastSavedContent('');
    setAnalysisReport(null);
    setSaveStatus('');
    setSceneError('');
    setIsLoadingScene(true);

    try {
      const data = await fetchScene(sceneId);
      const loadedContent = data.content ?? '';
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
  }, [isDirty, selectedSceneId]);

  const handleSceneContentChange = useCallback((nextContent) => {
    setSceneContent(nextContent);
    setSaveStatus((currentStatus) => (
      currentStatus.startsWith('Save failed') ? 'Unsaved changes' : currentStatus
    ));
  }, []);

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
      if (!isDirty) {
        return;
      }

      event.preventDefault();
      event.returnValue = '';
    }

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isDirty]);

  const handleSave = useCallback(async () => {
    if (!selectedSceneId || isSaving) {
      return;
    }

    setIsSaving(true);
    setSaveStatus('');

    try {
      await saveScene(selectedSceneId, sceneContent);
      setLastSavedContent(sceneContent);
      setSaveStatus('Saved');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed.';
      setSaveStatus(`Save failed: ${message}`);
    } finally {
      setIsSaving(false);
    }
  }, [isSaving, sceneContent, selectedSceneId]);

  const handleSaveBible = useCallback(async () => {
    if (isSavingBible) {
      return;
    }

    setIsSavingBible(true);

    try {
      const parsed = parseJsonObject(bibleText, 'Bible');
      await saveBible(parsed);
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
  }, [bibleText, isSavingBible]);

  const handleSaveStoryform = useCallback(async () => {
    if (isSavingStoryform) {
      return;
    }

    setIsSavingStoryform(true);

    try {
      const parsed = parseJsonObject(storyformText, 'Storyform');
      await saveStoryform(parsed);
      const formatted = formatJson(parsed);
      setStoryformText(formatted);
      setLastSavedStoryformText(formatted);
      setStoryformStatus('Saved');

      try {
        const contextPayload = await fetchStoryformContext();
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
  }, [isSavingStoryform, storyformText]);

  const handleCreateOMIIdea = useCallback(async (rawIdea) => {
    if (isCreatingOMIIdea) {
      return null;
    }

    setIsCreatingOMIIdea(true);
    setOmiError('');
    setOmiStatus('Creating idea...');

    try {
      const idea = await createOMIIdea(PROJECT_ID, { raw_idea: rawIdea });
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
  }, [isCreatingOMIIdea, refreshOMI]);

  const handleCreateOMICandidate = useCallback(async (payload) => {
    if (isCreatingOMICandidate) {
      return null;
    }

    setIsCreatingOMICandidate(true);
    setOmiError('');
    setOmiStatus('Creating candidate...');

    try {
      const candidate = await createOMICandidate(PROJECT_ID, payload);
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
  }, [isCreatingOMICandidate, refreshOMI]);

  useEffect(() => {
    function handleKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        handleSave();
      }
    }

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleSave]);

  const handleRunStoryCheck = useCallback(async () => {
    if (!selectedSceneId) {
      return;
    }

    setIsAnalyzing(true);
    setAnalysisReport(null);

    try {
      const data = await runStoryCheck(selectedSceneId);
      setAnalysisReport(data);
    } catch (error) {
      setAnalysisReport({
        error: error instanceof Error ? error.message : 'Story check failed.',
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedSceneId]);

  return (
    <div className="app-shell">
      <ProjectNav
        scenes={scenes}
        selectedSceneId={selectedSceneId}
        isLoading={isLoadingScenes}
        error={sceneError}
        onSelectScene={handleSelectScene}
      />
      <main className="editor-column" aria-label="Scene editor">
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
          onCreateIdea={handleCreateOMIIdea}
          onCreateCandidate={handleCreateOMICandidate}
        />

        <Editor
          content={sceneContent}
          disabled={!selectedSceneId || isLoadingScene}
          hasUnsavedChanges={isDirty}
          isLoading={isLoadingScene}
          isSaving={isSaving}
          onChange={handleSceneContentChange}
          onSave={handleSave}
          saveDisabled={!selectedSceneId || isLoadingScene || isSaving}
          saveStatus={saveStatus}
          sceneError={sceneError}
          selectedSceneId={selectedSceneId}
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
