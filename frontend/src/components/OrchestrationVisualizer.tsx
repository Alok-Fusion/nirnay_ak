import React, { useState } from 'react';
import { Users, Cpu, HelpCircle, Fingerprint, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';

interface OrchestrationVisualizerProps {
  visualizerOpen: boolean;
  setVisualizerOpen: (open: boolean) => void;
  visualizerStep: 'gathering' | 'evaluating' | 'reasoning' | 'challenging' | 'completed' | 'blocked';
  setVisualizerStep: (step: 'gathering' | 'evaluating' | 'reasoning' | 'challenging' | 'completed' | 'blocked') => void;
  orchTxId: number | null;
  orchRiskScore: number;
  orchShapValues: any;
  orchAuthStepsRequired: string[];
  orchAuthStepsCompleted: string[];
  setOrchAuthStepsCompleted: (steps: string[]) => void;
  orchRequiresClarify: boolean;
  orchClarifyPrompt: string;
  refetchAllBankingData: () => void;
}

export const OrchestrationVisualizer: React.FC<OrchestrationVisualizerProps> = ({
  visualizerOpen,
  setVisualizerOpen,
  visualizerStep,
  setVisualizerStep,
  orchTxId,
  orchRiskScore,
  orchShapValues,
  orchAuthStepsRequired,
  orchAuthStepsCompleted,
  setOrchAuthStepsCompleted,
  orchRequiresClarify,
  orchClarifyPrompt,
  refetchAllBankingData
}) => {
  const [challengeMpin, setChallengeMpin] = useState<string>('');
  const [challengeOtp, setChallengeOtp] = useState<string>('');
  const [challengeResponse, setChallengeResponse] = useState<string>('');
  const [challengePassword, setChallengePassword] = useState<string>('');
  const [challengeError, setChallengeError] = useState<string>('');
  const [challengeLoading, setChallengeLoading] = useState<boolean>(false);

  if (!visualizerOpen) return null;

  // Handle factor challenges verification (Password + MPIN + OTP)
  const handleVerifyChallenges = async () => {
    if (!orchTxId) return;
    setChallengeError('');
    setChallengeLoading(true);

    try {
      const response = await api.transactions.authenticate({
        transaction_id: orchTxId,
        password: challengePassword || undefined,
        mpin: challengeMpin || undefined,
        otp: challengeOtp || undefined
      });

      setOrchAuthStepsCompleted(response.completed_steps);

      if (response.status === 'APPROVED') {
        setVisualizerStep('completed');
        refetchAllBankingData();
      } else if (response.status === 'AWAITING_CLARIFICATION') {
        setChallengeError('');
      }
    } catch (err: any) {
      setChallengeError(err.message || 'Verification failed');
    } finally {
      setChallengeLoading(false);
    }
  };

  // Handle Clarification submission
  const handleVerifyClarification = async () => {
    if (!orchTxId || !challengeResponse) return;
    setChallengeError('');
    setChallengeLoading(true);

    try {
      const response = await api.transactions.clarify({
        transaction_id: orchTxId,
        response_text: challengeResponse
      });

      if (response.status === 'APPROVED') {
        setVisualizerStep('completed');
        refetchAllBankingData();
      } else if (response.status === 'BLOCKED') {
        setVisualizerStep('blocked');
        refetchAllBankingData();
        setChallengeError(response.message || 'Transaction suspended by AI security policies.');
      }
    } catch (err: any) {
      setChallengeError(err.message || 'Verification failed');
    } finally {
      setChallengeLoading(false);
    }
  };

  return (
    <div className="orchestrator-overlay">
      <div className="orchestrator-modal">
        
        <div className="modal-header-section">
          <div className="logo-spinner" style={{margin:'0 auto', width:'60px', height:'60px'}}>
            <div className="spinner-inner" style={{fontSize:'1.8rem'}}>N</div>
          </div>
          <h2 className="orchestrator-loader-text">NIRNAY Decision Pipeline</h2>
          <p style={{fontSize:'0.85rem'}}>Autonomous Multi-Agent Evaluation Layer</p>
        </div>

        {/* Steps Nodes Graph */}
        <div className="agent-node-graph">
          <div className={`agent-node ${
            visualizerStep === 'gathering' ? 'active' : 'completed'
          }`}>
            <Users className="menu-icon" />
            <span className="agent-node-label">Context Agent</span>
          </div>
          
          <div className={`agent-node ${
            visualizerStep === 'gathering' ? '' : 
            visualizerStep === 'evaluating' ? 'active' : 'completed'
          }`}>
            <Cpu className="menu-icon" />
            <span className="agent-node-label">ML & Policies</span>
          </div>

          <div className={`agent-node ${
            ['gathering', 'evaluating'].includes(visualizerStep) ? '' : 
            visualizerStep === 'reasoning' ? 'active' : 'completed'
          }`}>
            <HelpCircle className="menu-icon" />
            <span className="agent-node-label">Agent Logic</span>
          </div>

          <div className={`agent-node ${
            ['gathering', 'evaluating', 'reasoning'].includes(visualizerStep) ? '' :
            visualizerStep === 'challenging' ? 'active' :
            visualizerStep === 'blocked' ? 'failed' : 'completed'
          }`}>
            <Fingerprint className="menu-icon" />
            <span className="agent-node-label">Decision</span>
          </div>
        </div>

        {/* Visualizer Body based on step */}
        <div style={{display:'flex', flexDirection:'column', gap:'1.5rem', marginTop:'1.5rem'}}>
          
          {/* Gathering Context */}
          {visualizerStep === 'gathering' && (
            <div style={{textAlign:'center', padding:'1rem'}}>
              <p>Assembling digital twins profiles, known logins history, and recipient safety score indices...</p>
            </div>
          )}

          {/* Evaluating Risk */}
          {visualizerStep === 'evaluating' && (
            <div style={{textAlign:'center', padding:'1rem'}}>
              <p>Running explainable XGBoost/LightGBM risk algorithms and deterministic compliance audits...</p>
            </div>
          )}

          {/* Multi-Agent Reasoning */}
          {visualizerStep === 'reasoning' && (
            <div style={{textAlign:'center', padding:'1rem'}}>
              <p>Specialized Context, Policy, and Interpretation agents are debating intent indicators...</p>
            </div>
          )}

          {/* Challenged / Under Verification Factors */}
          {visualizerStep === 'challenging' && (
            <>
              {orchShapValues && (
                <div className="shap-container">
                  <div className="shap-header">
                    <span>Feature Contributions (SHAP Values)</span>
                    <span style={{color:'var(--danger)'}}>Total Risk Vector: {orchRiskScore}%</span>
                  </div>

                  <div className="shap-chart">
                    {Object.entries(orchShapValues).map(([feature, val]: [string, any]) => (
                      <div className="shap-row" key={feature}>
                        <span className="shap-feature">{feature}</span>
                        <div className="shap-bar-wrapper">
                          <div 
                            className={`shap-bar ${val > 0 ? 'positive' : 'negative'}`}
                            style={{
                              width: `${Math.min(100, Math.abs(val) * 1.5)}%`,
                            }}
                          ></div>
                        </div>
                        <span className={`shap-val-text ${val > 0 ? 'positive' : 'negative'}`}>
                          {val > 0 ? `+${val}%` : `${val}%`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="adaptive-challenge-box">
                <h3 style={{fontSize:'1rem', color:'#fff'}}>Adaptive Authentication Challenge</h3>
                
                {/* Show tabs indicating steps */}
                <div className="factor-tabs">
                  {orchAuthStepsRequired.map((step) => {
                    const isCompleted = orchAuthStepsCompleted.includes(step);
                    const isActive = !isCompleted && 
                      (step === 'PASSWORD' || 
                       (step === 'MPIN' && orchAuthStepsCompleted.includes('PASSWORD')) || 
                       (step === 'OTP' && orchAuthStepsCompleted.includes('MPIN') && orchAuthStepsCompleted.includes('PASSWORD')));
                    
                    return (
                      <div className={`factor-tab ${isCompleted ? 'completed' : isActive ? 'active' : ''}`} key={step}>
                        {step === 'PASSWORD' ? '1. PASSWORD' : step === 'MPIN' ? '2. SECURITY MPIN' : '3. SMS OTP'}
                      </div>
                    );
                  })}
                </div>

                {challengeError && <div className="auth-error-alert">{challengeError}</div>}

                {/* Challenge Inputs */}
                {/* Password input */}
                {orchAuthStepsRequired.includes('PASSWORD') && !orchAuthStepsCompleted.includes('PASSWORD') && (
                  <div className="form-input-group">
                    <label>Confirm Account Password</label>
                    <input 
                      type="password" 
                      value={challengePassword} 
                      onChange={(e) => setChallengePassword(e.target.value)} 
                      placeholder="••••••••" 
                    />
                  </div>
                )}

                {/* MPIN input */}
                {orchAuthStepsRequired.includes('MPIN') && !orchAuthStepsCompleted.includes('MPIN') && (
                  <div className="form-input-group">
                    <label>Enter 4-6 Digit Security MPIN</label>
                    <input 
                      type="password" 
                      maxLength={6} 
                      value={challengeMpin} 
                      onChange={(e) => setChallengeMpin(e.target.value.replace(/\D/g, ''))} 
                      placeholder="••••" 
                    />
                  </div>
                )}

                {/* OTP input */}
                {orchAuthStepsRequired.includes('OTP') && !orchAuthStepsCompleted.includes('OTP') && (
                  <div className="form-input-group">
                    <label>Enter SMS OTP (Testing code is '123456')</label>
                    <input 
                      type="text" 
                      maxLength={6} 
                      value={challengeOtp} 
                      onChange={(e) => setChallengeOtp(e.target.value.replace(/\D/g, ''))} 
                      placeholder="123456" 
                    />
                  </div>
                )}

                {/* Factor Verification Button */}
                {!orchAuthStepsRequired.every(s => orchAuthStepsCompleted.includes(s)) && (
                  <button 
                    onClick={handleVerifyChallenges} 
                    disabled={challengeLoading} 
                    className="btn-primary"
                  >
                    {challengeLoading ? 'Verifying...' : 'Submit Verification Factor'}
                  </button>
                )}

                {/* Clarification Intent checking text area */}
                {orchRequiresClarify && !orchClarifyPrompt.startsWith('[CLARIFIED]') && 
                 orchAuthStepsRequired.every(s => orchAuthStepsCompleted.includes(s)) && (
                  <div className="form-input-group" style={{marginTop:'0.5rem'}}>
                    <label style={{color:'var(--warning)', fontWeight:600, display:'flex', gap:'0.25rem', alignItems:'center'}}>
                      <AlertTriangle className="menu-icon" /> Conversation Agent Intent Verification
                    </label>
                    <p style={{fontSize:'0.85rem', color: 'var(--text-secondary)', marginBottom:'0.5rem'}}>{orchClarifyPrompt}</p>
                    <textarea 
                      rows={3} 
                      value={challengeResponse} 
                      onChange={(e) => setChallengeResponse(e.target.value)}
                      placeholder="Provide explanation of who told you to make this transaction..."
                      required
                    />
                    <button 
                      onClick={handleVerifyClarification} 
                      disabled={challengeLoading || !challengeResponse} 
                      className="btn-primary" 
                      style={{marginTop:'0.75rem'}}
                    >
                      Submit Response to AI Agent
                    </button>
                  </div>
                )}

              </div>
            </>
          )}

          {/* Blocked Scammer */}
          {visualizerStep === 'blocked' && (
            <div style={{textAlign:'center', padding:'1rem', display:'flex', flexDirection:'column', alignItems:'center', gap:'0.75rem'}}>
              <AlertTriangle className="menu-icon" style={{color:'var(--danger)', width:'48px', height:'48px'}} />
              <h3 style={{color:'#fff'}}>Transaction Suspended</h3>
              <p>NIRNAY Decision Engine detected a critical policy mismatch or matching global scam blacklist threat matrices. Transaction rejected automatically.</p>
              <button onClick={() => setVisualizerOpen(false)} className="btn-primary" style={{marginTop:'1rem'}}>
                Close Window
              </button>
            </div>
          )}

          {/* Completed Success Check */}
          {visualizerStep === 'completed' && (
            <div style={{textAlign:'center', padding:'1rem', display:'flex', flexDirection:'column', alignItems:'center', gap:'0.75rem'}}>
              <CheckCircle2 className="menu-icon" style={{color:'var(--success)', width:'48px', height:'48px'}} />
              <h3 style={{color:'#fff'}}>Transaction Executed</h3>
              <p>Multi-factor adaptive challenge and natural language intent parameters verified. Funds transferred safely.</p>
              <button onClick={() => setVisualizerOpen(false)} className="btn-primary" style={{marginTop:'1rem'}}>
                Return to dashboard
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
