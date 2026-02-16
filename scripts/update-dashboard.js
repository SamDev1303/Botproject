/**
 * update-dashboard.js
 * The backbone of BELLA OS. 
 * High-performance, low-fluff data generation for Clean Up Bros.
 */

const fs = require('fs');
const path = require('path');

function getIntelligence() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const memoryPath = path.join(__dirname, '..', 'memory', `${today}.md`);
        if (fs.existsSync(memoryPath)) {
            const content = fs.readFileSync(memoryPath, 'utf8');
            return content.split('\n')
                .filter(l => l.trim().startsWith('-'))
                .slice(0, 4)
                .map(l => `
                    <div class="flex gap-4 group cursor-default">
                        <div class="w-1 h-1 rounded-full bg-cyan-500 mt-2 shrink-0 group-hover:scale-150 transition-transform"></div>
                        <p class="text-sm text-slate-400 leading-relaxed font-medium">${l.replace('-', '').trim()}</p>
                    </div>
                `).join('');
        }
    } catch (e) { return "Journal offline."; }
    return "<p class='text-xs text-slate-600 italic font-mono uppercase tracking-widest'>Awaiting daily input...</p>";
}

const data = {
    stats: {
        revenue: "$320.00",
        leads: "14",
        invoices: "3",
        memory: "18%"
    },
    system: {
        model: "OPUS 4.6 • ACTIVE",
        memory: "18%"
    },
    opsHtml: `
        <div class="space-y-3">
            <div class="flex items-center justify-between p-6 rounded-3xl bg-white/[0.01] border border-white/[0.03] hover:border-cyan-500/30 transition-all group">
                <div class="flex items-center gap-6">
                    <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 border border-cyan-500/20">
                        <i class="fas fa-broom"></i>
                    </div>
                    <div>
                        <p class="text-sm font-bold uppercase tracking-widest mb-0.5">Airbnb: Pinnacle</p>
                        <p class="text-[10px] text-slate-500 font-black uppercase">Schedule: 10:00 AM • Herdip Gill</p>
                    </div>
                </div>
                <div class="flex items-center gap-4">
                    <span class="text-[10px] font-black text-cyan-400 bg-cyan-500/10 px-4 py-1.5 rounded-full border border-cyan-500/20 uppercase tracking-widest">Awaiting Start</span>
                    <i class="fas fa-chevron-right text-slate-800 group-hover:text-cyan-500 transition-colors"></i>
                </div>
            </div>
            <div class="flex items-center justify-between p-6 rounded-3xl bg-white/[0.01] border border-white/[0.03] opacity-40 grayscale group">
                <div class="flex items-center gap-6">
                    <div class="w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center text-slate-500">
                        <i class="fas fa-check-double"></i>
                    </div>
                    <div>
                        <p class="text-sm font-bold uppercase tracking-widest mb-0.5">Clinical Notes: Larissa Marks</p>
                        <p class="text-[10px] text-slate-600 font-black uppercase">Logged to documentation/2026-02-17.md</p>
                    </div>
                </div>
                <span class="text-[10px] font-black text-slate-600 bg-white/5 px-4 py-1.5 rounded-full uppercase tracking-widest">Completed</span>
            </div>
        </div>
    `,
    intelHtml: getIntelligence(),
    socialHtml: "" 
};

const dataPath = path.join(__dirname, '..', 'dashboard', 'data.json');
fs.writeFileSync(dataPath, JSON.stringify(data, null, 4));
console.log('BELLA OS Updated.');
