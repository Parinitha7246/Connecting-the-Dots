import { useAppStore } from "../store/useAppStore";
import { createPodcast } from "../api/podcast";
import { EmptyState } from "./EmptyState";
import { 
  PodcastIcon, 
  BulbIcon, 
  ThemeIcon, 
  LinkIcon, 
  ContradictionIcon,
  ExampleIcon // <-- A new icon for the 'Examples' card
} from "./Icons"; 

// A reusable component for a consistent look and feel for each insight card.
const InsightCard = ({ icon, title, children }: { icon: React.ReactNode, title: string, children: React.ReactNode }) => (
  <div className="bg-surface-inset p-3 rounded-lg">
    <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-content">
      {icon}
      <span>{title}</span>
    </div>
    <div className="text-sm text-content-subtle leading-relaxed">
      {children}
    </div>
  </div>
);

export default function InsightsTab() {
  // We get ALL the different insight types from the global store.
  const { 
    themes, insights, didYouKnow, contradiction, connections, examples, 
    snippets, setAudioUrl, audioUrl 
  } = useAppStore();

  const hasInsights = themes.length > 0 || insights.length > 0 || !!didYouKnow || !!contradiction || connections.length > 0 || (examples && examples.length > 0);

  async function onPodcast() {
    const texts = snippets.map(s => s.text).filter(Boolean);
    if (texts.length === 0) {
      alert("Cannot generate podcast without context from snippets.");
      return;
    }
    try {
      alert("Generating podcast... this may take a moment.");
      const res = await createPodcast({section_texts: texts, persona: 'narrator', task: 'summarize'});
      const url = res?.tts?.url || (res?.tts as any)?.audio_path || "";
      if (url) {
        setAudioUrl(url);
      } else {
        alert("Podcast generated, but no audio URL was returned from the backend.");
      }
    } catch (error) {
      console.error("Failed to generate podcast:", error);
      alert("An error occurred while generating the podcast.");
    }
  }

  if (!hasInsights) {
    return <EmptyState icon={<BulbIcon />} message="Select text to generate AI insights. (Turn on 'Online Mode' for best results)." />;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="scrolly flex-1 -mr-2 pr-2 space-y-4">
        
        {themes.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-content mb-2">Key Themes</h3>
            <div className="flex flex-wrap gap-2">
              {themes.map((theme) =>
                <div key={theme} className="flex items-center gap-2 text-sm bg-gray-100 text-gray-700 rounded-full px-3 py-1">
                  <ThemeIcon />
                  {theme}
                </div>
              )}
            </div>
          </div>
        )}

        {insights.length > 0 && (
          <InsightCard icon={<BulbIcon />} title="Key Takeaways">
            <ul className="list-disc pl-5 space-y-1">
              {insights.map((i, idx) => <li key={idx}>{i}</li>)}
            </ul>
          </InsightCard>
        )}
        
        {didYouKnow && (
          <InsightCard icon={<BulbIcon />} title="Did you know?">
            {didYouKnow}
          </InsightCard>
        )}

        {contradiction && (
          <InsightCard icon={<ContradictionIcon />} title="Contradiction">
            {contradiction}
          </InsightCard>
        )}

        {connections?.length > 0 && (
          <InsightCard icon={<LinkIcon />} title="Cross-Document Connections">
            <ul className="list-disc pl-5 space-y-1">
              {connections.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </InsightCard>
        )}

        {examples?.length > 0 && (
          <InsightCard icon={<ExampleIcon />} title="Examples">
            <ul className="list-disc pl-5 space-y-1">
              {examples.map((ex, i) => <li key={i}>{ex}</li>)}
            </ul>
          </InsightCard>
        )}
      </div>

      <div className="mt-4 pt-4 border-t">
        <button 
          className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary-hover text-white font-semibold rounded-lg px-3 py-2 transition-colors disabled:opacity-50"
          onClick={onPodcast} 
          disabled={!hasInsights}
        >
          <PodcastIcon />
          Generate Podcast
        </button>
        {audioUrl && (
          <div className="mt-3">
            <audio controls src={audioUrl} className="w-full" />
          </div>
        )}
      </div>
    </div>
  );
}