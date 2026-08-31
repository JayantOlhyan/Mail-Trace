'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { Target, Users, Globe, Server, Layers } from 'lucide-react';

export function CampaignScene() {
  const { ref, progress } = useScrollReveal(0.4);

  // Unified Cinematic Timing
  const fadeIn = Math.min(1, progress * 3);
  const sceneOpacity = fadeIn;


  const showCard = progress > 0.2;
  const showMetrics = progress > 0.5;
  const showButton = progress > 0.8;

  return (
    <section id="scene-10" className="relative w-full h-full" ref={ref}>
      <div className="sticky top-0 flex h-screen items-center justify-center px-4" style={{ opacity: sceneOpacity }}>
        
        <div className={`w-full max-w-xl bg-slate-100/60 dark:bg-slate-900/40 backdrop-blur-xl border border-slate-300 dark:border-slate-700/50 rounded-2xl p-8 shadow-[0_0_40px_rgba(0,0,0,0.5)] transition-all duration-700 transform ease-[cubic-bezier(0.16,1,0.3,1)] ${showCard ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
          
          <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-300 dark:border-slate-700/50">
            <div className="w-14 h-14 bg-purple-500/20 text-purple-400 rounded-lg flex items-center justify-center border border-purple-500/30">
              <Layers className="w-7 h-7" />
            </div>
            <div>
              <div className="text-xs font-mono text-purple-400 tracking-widest mb-1 drop-shadow-[0_0_5px_rgba(168,85,247,0.5)]">CAMPAIGN CANDIDATE</div>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Financial Phishing Campaign</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 font-mono mt-1">ID-8829</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className={`bg-slate-200 dark:bg-slate-800/30 border border-slate-300 dark:border-slate-700/50 rounded-xl p-4 flex items-center gap-4 transition-all duration-500 delay-100 ${showMetrics ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <Users className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              <div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">7</div>
                <div className="text-xs text-slate-600 dark:text-slate-400 font-mono">RELATED EMAILS</div>
              </div>
            </div>
            <div className={`bg-slate-200 dark:bg-slate-800/30 border border-slate-300 dark:border-slate-700/50 rounded-xl p-4 flex items-center gap-4 transition-all duration-500 delay-200 ${showMetrics ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <Globe className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              <div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">2</div>
                <div className="text-xs text-slate-600 dark:text-slate-400 font-mono">DOMAINS</div>
              </div>
            </div>
            <div className={`bg-slate-200 dark:bg-slate-800/30 border border-slate-300 dark:border-slate-700/50 rounded-xl p-4 flex items-center gap-4 transition-all duration-500 delay-300 ${showMetrics ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <Server className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              <div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">2</div>
                <div className="text-xs text-slate-600 dark:text-slate-400 font-mono">IP ADDRESSES</div>
              </div>
            </div>
            <div className={`bg-slate-200 dark:bg-slate-800/30 border border-slate-300 dark:border-slate-700/50 rounded-xl p-4 flex items-center gap-4 transition-all duration-500 delay-400 ${showMetrics ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              <Target className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              <div>
                <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">1</div>
                <div className="text-xs text-slate-600 dark:text-slate-400 font-mono">INFRA CLUSTER</div>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <div className={`transition-all duration-500 delay-500 ${showMetrics ? 'opacity-100' : 'opacity-0'}`}>
              <span className="text-xs text-slate-600 dark:text-slate-400 font-mono mr-2">CONFIDENCE:</span>
              <span className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 text-purple-300 text-xs font-bold rounded-full shadow-[0_0_10px_rgba(168,85,247,0.2)]">HIGH</span>
            </div>
            
            <button className={`bg-purple-600/90 hover:bg-purple-500 text-slate-900 dark:text-white font-medium px-6 py-2 rounded-full transition-all duration-500 hover:scale-105 shadow-[0_0_15px_rgba(147,51,234,0.4)] ${showButton ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
              INVESTIGATE CAMPAIGN
            </button>
          </div>

        </div>

      </div>
    </section>
  );
}
