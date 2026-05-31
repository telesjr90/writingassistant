import { useCallback, useEffect, useState } from 'react';
import ProjectNav from './components/ProjectNav.jsx';
import Editor from './components/Editor.jsx';
import AnalysisSidebar from './components/AnalysisSidebar.jsx';
import {
  fetchScene,
  fetchScenes,
  fetchStoryformContext,
  runStoryCheck,
  saveScene,
} from './api.js';

export default function App() {
  const [scenes, setScenes] = useState([]);
  const [selectedSceneId, setSelectedSceneId] = useState('');
  const [sceneContent, setSceneContent] = useState('');
  const [storyformContext, setStoryformContext] = useState('');
  const [analysisReport, setAnalysisReport] = useState(null);
  const [sceneError, setSceneError] = useState('');
  const [isLoadingScenes, setIsLoadingScenes] = useState(true);
  const [isLoadingScene, setIsLoadingScene] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadInitialData() {
      setIsLoadingScenes(true);
      setSceneError('');

      try {
        const [scenePayload, contextPayload] = await Promise.all([
          fetchScenes(),
          fetchStoryformContext(),
        ]);

        if (!isMounted) {
          return;
        }

        setScenes(Array.isArray(scenePayload) ? scenePayload : scenePayload.scenes ?? []);
        setStoryformContext(contextPayload.context ?? '');
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

  const handleSelectScene = useCallback(async (sceneId) => {
    setSelectedSceneId(sceneId);
    setSceneContent('');
    setAnalysisReport(null);
    setSaveStatus('');
    setSceneError('');
    setIsLoadingScene(true);

    try {
      const data = await fetchScene(sceneId);
      setSceneContent(data.content ?? '');
    } catch (error) {
      setSceneError(error instanceof Error ? error.message : 'Failed to load scene.');
    } finally {
      setIsLoadingScene(false);
    }
  }, []);

  const handleSave = useCallback(async () => {
    if (!selectedSceneId || isSaving) {
      return;
    }

    setIsSaving(true);
    setSaveStatus('');

    try {
      await saveScene(selectedSceneId, sceneContent);
      setSaveStatus('Saved!');
      window.setTimeout(() => setSaveStatus(''), 1800);
    } catch (error) {
      setSaveStatus(error instanceof Error ? error.message : 'Save failed.');
    } finally {
      setIsSaving(false);
    }
  }, [isSaving, sceneContent, selectedSceneId]);

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
        <details className="storyform-context" open>
          <summary>Storyform Context</summary>
          <pre>{storyformContext || 'No storyform context available.'}</pre>
        </details>

        <Editor
          content={sceneContent}
          disabled={!selectedSceneId || isLoadingScene}
          isLoading={isLoadingScene}
          onChange={setSceneContent}
          onSave={handleSave}
          saveDisabled={!selectedSceneId || isLoadingScene || isSaving}
          saveStatus={saveStatus}
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
