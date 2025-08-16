import { useAppStore } from "../store/useAppStore";
import { createPodcast } from "../api/podcast";
import { EmptyState } from "./EmptyState";
import { PodcastIcon, BulbIcon, ThemeIcon } from "./Icons"; 

export default function InsightsTab() {
  const { themes, insights, snippets, setAudioUrl, audioUrl } = useAppStore();
  const hasInsights = themes.length > 0 || insights.length > 0;

  // --- THIS IS THE CORRECTED onPodcast FUNCTION ---
  // The logic has been restored, so 'createPodcast' is now used.
  async function onPodcast() {
    const texts = snippets.map(s=>s.text).filter(Boolean);
    if (texts.length === 0) return; // Don't run if there's no context

    try {
      const res = await createPodcast(texts);
      const url = res?.tts?.url || "";
      if (url) {
        setAudioUrl(url);
      } else {
        alert("Podcast generated, but no audio URL was returned.");
      }
    } catch (error) {
      console.error("Failed to generate podcast:", error);
      alert("There was an error generating the podcast.");
    }
  }

  if (!hasInsights) {
    // The className prop will now work because we are fixing BulbIcon in the next step.
    return <EmptyState icon={<BulbIcon className="w-8 h-8 text-gray-400" />} message="Select text to generate AI insights." />;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="scrolly flex-1 -mr-2 pr-2 space-y-4">
        {themes.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-content mb-2">Key Themes</h3>
            <div className="flex flex-wrap gap-2">
              {themes.map((theme) =>
                <div key={theme} className="flex items-center gap-2 text-sm bg-surface-inset text-content rounded-full px-3 py-1">
                  <ThemeIcon />
                  {theme}
                </div>
              )}
            </div>
          </div>
        )}
        {insights.length > 0 && (
           <div>
            <h3 className="text-sm font-bold text-content mb-2">Generated Insights</h3>
            <div className="text-sm text-content leading-relaxed bg-surface-inset p-3 rounded-lg">
              {insights.join(' ')}
            </div>
          </div>
        )}
      </div>
      <div className="mt-4 pt-4 border-t">
        <button className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-white font-semibold rounded-lg px-3 py-2 transition-colors disabled:opacity-50"
          onClick={onPodcast} disabled={!hasInsights}>
          <PodcastIcon />
          Generate Podcast
        </button>
        {audioUrl && <div className="mt-3"><audio controls src={audioUrl} className="w-full" /></div>}
      </div>
    </div>
  );
}