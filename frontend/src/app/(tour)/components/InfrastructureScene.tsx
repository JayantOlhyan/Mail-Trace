'use client';

import { useScrollReveal } from '../hooks/useScrollReveal';
import { tourData } from '../data/tourData';

export function InfrastructureScene() {
  const { ref, progress } = useScrollReveal(0.3);

  const showLevel1 = progress > 0.1;
  const showLevel2 = progress > 0.35;
  const showLevel3 = progress > 0.6;

  return (
    <section id="scene-08" className="relative min-h-[150vh]" ref={ref}>
      <div className="sticky top-0 flex h-screen flex-col items-center justify-center px-4">
        
        <div className="text-center mb-16">
          <h3 className="text-xl font-mono text-slate-500 tracking-widest mb-4">INFRASTRUCTURE INTELLIGENCE</h3>
          <p className="text-slate-400 max-w-xl mx-auto">
            Technical indicators are expanded into an intelligence graph, querying external datasets for context.
          </p>
        </div>

        {/* Tree Visualization */}
        <div className="w-full max-w-4xl flex justify-center font-mono text-sm">
          
          <div className="flex flex-col items-center">
            {/* Level 1: Email */}
            <div className={`px-6 py-2 bg-slate-900 border border-slate-700 rounded transition-all duration-500 ${showLevel1 ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}>
              EMAIL
            </div>
            
            <div className={`w-px h-8 bg-slate-700 transition-all duration-500 ${showLevel2 ? 'opacity-100' : 'opacity-0'}`} />

            {/* Level 2: Domain & IP */}
            <div className="flex gap-16 md:gap-32 relative">
              <div className={`absolute top-0 left-1/2 w-[calc(50%+4rem)] md:w-[calc(50%+8rem)] h-px bg-slate-700 -translate-x-1/2 transition-all duration-500 origin-center ${showLevel2 ? 'scale-x-100 opacity-100' : 'scale-x-0 opacity-0'}`} />
              
              {/* Domain Branch */}
              <div className={`flex flex-col items-center transition-all duration-700 delay-100 transform ${showLevel2 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
                <div className="w-px h-8 bg-slate-700" />
                <div className="px-6 py-2 bg-slate-900 border border-slate-700 rounded text-blue-400">
                  DOMAIN
                </div>

                <div className={`w-px h-8 bg-slate-700 transition-all duration-500 ${showLevel3 ? 'opacity-100' : 'opacity-0'}`} />
                
                <div className={`flex gap-4 relative transition-all duration-700 transform ${showLevel3 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
                  <div className="absolute top-0 left-1/2 w-[calc(100%+1rem)] h-px bg-slate-700 -translate-x-1/2" />
                  
                  <div className="flex flex-col items-center pt-8">
                    <div className="absolute top-0 w-px h-8 bg-slate-700" />
                    <div className="px-3 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 text-xs">DNS</div>
                  </div>
                  <div className="flex flex-col items-center pt-8">
                    <div className="absolute top-0 w-px h-8 bg-slate-700" />
                    <div className="px-3 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 text-xs">MX</div>
                  </div>
                </div>
              </div>

              {/* IP Branch */}
              <div className={`flex flex-col items-center transition-all duration-700 delay-200 transform ${showLevel2 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
                <div className="w-px h-8 bg-slate-700" />
                <div className="px-6 py-2 bg-slate-900 border border-slate-700 rounded text-orange-400">
                  IP
                </div>

                <div className={`w-px h-8 bg-slate-700 transition-all duration-500 ${showLevel3 ? 'opacity-100' : 'opacity-0'}`} />
                
                <div className={`flex gap-4 relative transition-all duration-700 delay-100 transform ${showLevel3 ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
                  <div className="absolute top-0 left-1/2 w-[calc(100%+1rem)] h-px bg-slate-700 -translate-x-1/2" />
                  
                  <div className="flex flex-col items-center pt-8">
                    <div className="absolute top-0 w-px h-8 bg-slate-700" />
                    <div className="px-3 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 text-xs">ASN</div>
                  </div>
                  <div className="flex flex-col items-center pt-8">
                    <div className="absolute top-0 w-px h-8 bg-slate-700" />
                    <div className="px-3 py-1 bg-slate-950 border border-slate-800 rounded text-slate-400 text-xs">GEO</div>
                  </div>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
