import React, { useState } from 'react';
import { Crosshair } from 'lucide-react';
import { api } from '../services/api';

interface ScamDrillsViewProps {
  user: any;
  refetchAllBankingData: () => void;
}

export const ScamDrillsView: React.FC<ScamDrillsViewProps> = ({ user, refetchAllBankingData }) => {
  const [drillScenario, setDrillScenario] = useState<any | null>(null);
  const [drillSelectedOption, setDrillSelectedOption] = useState<string>('');
  const [drillResult, setDrillResult] = useState<any | null>(null);
  const [drillLoading, setDrillLoading] = useState<boolean>(false);
  const [drillScore, setDrillScore] = useState<{ correct: number; total: number }>({ correct: 0, total: 0 });

  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">NIRNAY Interactive Scam Drills</h1>
          <p className="page-subtitle">Test your resilience against digital scams, social engineering threats, and identity theft setups</p>
        </div>
      </header>

      <div className="page-content">
        
        {/* Scam Drills Container */}
        {!drillScenario && !drillResult ? (
          <div className="glass-card" style={{padding:'3rem', textAlign:'center', display:'flex', flexDirection:'column', alignItems:'center', gap:'1.5rem'}}>
            <Crosshair style={{width:'64px', height:'64px', color:'var(--primary)', animation:'pulse 2s infinite'}} />
            <div>
              <h2 style={{color:'#fff', marginBottom:'0.5rem'}}>Start Your Scam Resilience Simulation</h2>
              <p style={{color:'var(--text-muted)', maxWidth:'500px', fontSize:'0.88rem', lineHeight:'1.6'}}>
                Scammers use sophisticated scripts mimicking bank managers, police officers, and cash rewards. Run interactive scenarios to learn how to spot scam indicators and secure your assets.
              </p>
            </div>
            
            <button 
              className="action-btn primary"
              onClick={async () => {
                setDrillLoading(true);
                try {
                  const scenario = await api.drills.getScenario();
                  setDrillScenario(scenario);
                  setDrillSelectedOption('');
                } catch (e) {
                  console.error('Failed to load drill scenario:', e);
                }
                setDrillLoading(false);
              }}
              disabled={drillLoading}
              style={{padding:'0.8rem 2rem', fontSize:'1rem'}}
            >
              {drillLoading ? 'Loading Scenario...' : '🎮 Start Drill Simulation'}
            </button>
          </div>
        ) : drillResult ? (
          /* Active Result Output Panel */
          <div className="glass-card" style={{padding:'2.5rem', border: drillResult.is_correct ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(239,68,68,0.3)'}}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.5rem'}}>
              <span className={`status-badge ${drillResult.is_correct ? 'approved' : 'blocked'}`} style={{fontSize:'0.9rem', padding:'0.4rem 1rem'}}>
                {drillResult.is_correct ? '✔️ Drill Passed' : '❌ Drill Failed'}
              </span>
              <span style={{fontSize:'0.85rem', color:'var(--text-muted)'}}>
                Simulation Score: <strong>{drillScore.correct} / {drillScore.total}</strong>
              </span>
            </div>

            <h3 style={{color:'#fff', fontSize:'1.2rem', marginBottom:'1rem'}}>{drillResult.scenario_title}</h3>
            
            <div style={{backgroundColor:'rgba(255,255,255,0.02)', padding:'1.25rem', borderRadius:'8px', marginBottom:'1.5rem', borderLeft: `3px solid ${drillResult.is_correct ? 'var(--success)' : 'var(--danger)'}`}}>
              <p style={{fontSize:'0.88rem', color:'var(--text-secondary)', lineHeight:'1.6', marginBottom:'0.75rem'}}>
                <strong>Explanation:</strong> {drillResult.explanation}
              </p>
              <p style={{fontSize:'0.88rem', color:'var(--text-muted)'}}>
                <strong>Indicator to Watch:</strong> <span style={{color:'var(--warning)'}}>{drillResult.scam_indicators}</span>
              </p>
            </div>

            <div style={{display:'flex', gap:'1rem', alignItems:'center', borderTop:'1px solid rgba(255,255,255,0.06)', paddingTop:'1.5rem'}}>
              <div>
                <span style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>YOUR REWARD</span>
                <p style={{color:'#fff', fontWeight:700, fontSize:'0.95rem'}}>
                  {drillResult.is_correct ? '📈 Security Score Boosted!' : '📉 Security Score Decreased'}
                </p>
              </div>

              <button 
                className="action-btn primary"
                onClick={async () => {
                  setDrillLoading(true);
                  setDrillResult(null);
                  try {
                    const scenario = await api.drills.getScenario();
                    setDrillScenario(scenario);
                    setDrillSelectedOption('');
                    refetchAllBankingData();
                  } catch (e) {
                    console.error('Failed to load next drill:', e);
                  }
                  setDrillLoading(false);
                }}
                disabled={drillLoading}
                style={{marginLeft:'auto', padding:'0.6rem 1.5rem'}}
              >
                {drillLoading ? 'Loading...' : '➡️ Next Drill'}
              </button>
            </div>
          </div>
        ) : drillScenario ? (
          /* Active Scenario Selector Panel */
          <div className="glass-card" style={{padding:'2.5rem'}}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.5rem'}}>
              <div>
                <span style={{fontSize:'0.7rem', padding:'0.2rem 0.5rem', backgroundColor:'rgba(99,102,241,0.15)', border:'1px solid rgba(99,102,241,0.3)', color:'var(--primary)', borderRadius:'4px', marginRight:'0.5rem'}}>
                  {drillScenario.category?.replace(/_/g, ' ')}
                </span>
                <span style={{
                  fontSize:'0.7rem', padding:'0.2rem 0.5rem', 
                  backgroundColor: drillScenario.difficulty === 'HARD' ? 'rgba(239,68,68,0.12)' : drillScenario.difficulty === 'MEDIUM' ? 'rgba(245,158,11,0.12)' : 'rgba(34,197,94,0.12)', 
                  border: `1px solid ${drillScenario.difficulty === 'HARD' ? 'rgba(239,68,68,0.3)' : drillScenario.difficulty === 'MEDIUM' ? 'rgba(245,158,11,0.3)' : 'rgba(34,197,94,0.3)'}`, 
                  color: drillScenario.difficulty === 'HARD' ? 'var(--danger)' : drillScenario.difficulty === 'MEDIUM' ? 'var(--warning)' : 'var(--success)', 
                  borderRadius:'4px'
                }}>
                  {drillScenario.difficulty}
                </span>
              </div>
            </div>

            <h3 style={{color:'#fff', fontSize:'1.15rem', marginBottom:'1.25rem'}}>{drillScenario.title}</h3>
            
            <div style={{backgroundColor:'rgba(255,255,255,0.03)', borderRadius:'8px', padding:'1.25rem', marginBottom:'1.5rem', borderLeft:'3px solid var(--primary)'}}>
              <p style={{color:'var(--text-secondary)', fontSize:'0.9rem', lineHeight:'1.7'}}>{drillScenario.narrative}</p>
            </div>

            <h4 style={{color:'#fff', fontSize:'0.95rem', marginBottom:'1rem'}}>{drillScenario.question}</h4>
            
            <div style={{display:'flex', flexDirection:'column', gap:'0.6rem', marginBottom:'2rem'}}>
              {drillScenario.options?.map((opt: any) => (
                <button
                  key={opt.id}
                  onClick={() => setDrillSelectedOption(opt.id)}
                  style={{
                    display:'flex', alignItems:'center', gap:'0.75rem',
                    padding:'0.9rem 1rem', borderRadius:'8px',
                    border: drillSelectedOption === opt.id ? '2px solid var(--primary)' : '1px solid rgba(255,255,255,0.08)',
                    backgroundColor: drillSelectedOption === opt.id ? 'rgba(99,102,241,0.12)' : 'rgba(255,255,255,0.02)',
                    color: '#fff', cursor:'pointer', textAlign:'left', fontSize:'0.88rem',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <span style={{
                    width:'28px', height:'28px', borderRadius:'50%', 
                    display:'flex', alignItems:'center', justifyContent:'center',
                    backgroundColor: drillSelectedOption === opt.id ? 'var(--primary)' : 'rgba(255,255,255,0.06)',
                    fontSize:'0.75rem', fontWeight:700, flexShrink:0
                  }}>{opt.id}</span>
                  {opt.text}
                </button>
              ))}
            </div>

            <button 
              className="action-btn primary"
              disabled={!drillSelectedOption || drillLoading}
              onClick={async () => {
                if (!drillSelectedOption) return;
                setDrillLoading(true);
                try {
                  const result = await api.drills.submitAnswer({
                    scenario_id: drillScenario.id,
                    selected_option: drillSelectedOption,
                  });
                  setDrillResult(result);
                  setDrillScenario(null);
                  setDrillScore(prev => ({
                    correct: prev.correct + (result.is_correct ? 1 : 0),
                    total: prev.total + 1,
                  }));
                  refetchAllBankingData();
                } catch (e) {
                  console.error('Failed to submit drill answer:', e);
                }
                setDrillLoading(false);
              }}
              style={{width:'100%', padding:'0.8rem', fontSize:'0.95rem'}}
            >
              {drillLoading ? 'Evaluating...' : '🔍 Submit Answer'}
            </button>
          </div>
        ) : null}
      </div>
    </>
  );
};
