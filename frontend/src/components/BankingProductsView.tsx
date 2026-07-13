import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CreditCard, ShieldCheck, Gift } from 'lucide-react';
import { api } from '../services/api';

interface BankingProductsViewProps {
  user: any;
  refetchAllBankingData: () => void;
}

export const BankingProductsView: React.FC<BankingProductsViewProps> = ({ user, refetchAllBankingData }) => {
  // Query state hooks self-contained!
  const { data: cardsData, refetch: refetchCards } = useQuery({
    queryKey: ['cards'],
    queryFn: api.bankingProducts.cardsList,
    enabled: !!user,
  });

  const { data: fdData, refetch: refetchFd } = useQuery({
    queryKey: ['fixedDeposits'],
    queryFn: api.bankingProducts.fdList,
    enabled: !!user,
  });

  const { data: offersData, refetch: refetchOffers } = useQuery({
    queryKey: ['offers'],
    queryFn: api.bankingProducts.offersList,
    enabled: !!user,
  });

  // Local card / deposit state hooks
  const [newCardType, setNewCardType] = useState<string>('VISA_DEBIT');
  const [newCardLimit, setNewCardLimit] = useState<string>('50000');
  const [fdPrincipal, setFdPrincipal] = useState<string>('');
  const [fdDuration, setFdDuration] = useState<string>('12');
  const [bankingProductStatus, setBankingProductStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [bankingProductLoading, setBankingProductLoading] = useState<boolean>(false);

  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Cards & Term Deposits</h1>
          <p className="page-subtitle">Configure secure virtual credit cards, open fixed deposits, and claim security-tier rewards</p>
        </div>
      </header>

      <div className="page-content">
        {bankingProductStatus && (
          <div 
            className={bankingProductStatus.type === 'success' ? 'status-badge approved' : 'auth-error-alert'}
            style={{ marginBottom: '1.5rem', width: '100%', padding: '0.8rem', borderRadius: '6px' }}
          >
            {bankingProductStatus.message}
          </div>
        )}

        <div className="grid-row-2">
          
          {/* VIRTUAL CARDS MANAGEMENT */}
          <div className="glass-card">
            <div className="card-header" style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <h2 className="card-title"><CreditCard className="menu-icon" /> Virtual Cards Control</h2>
              <span style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>{cardsData?.length ?? 0} / 3 Active</span>
            </div>

            {/* Create Card Form */}
            <form onSubmit={async (e) => {
              e.preventDefault();
              setBankingProductLoading(true);
              setBankingProductStatus(null);
              try {
                await api.bankingProducts.cardsCreate({
                  card_type: newCardType,
                  spend_limit: Number(newCardLimit)
                });
                refetchCards();
                setBankingProductStatus({ type: 'success', message: 'Secure Virtual Card generated successfully!' });
              } catch (err: any) {
                setBankingProductStatus({ type: 'error', message: err.message || 'Failed to create card.' });
              }
              setBankingProductLoading(false);
            }} style={{marginBottom:'1.5rem', backgroundColor:'rgba(255,255,255,0.02)', padding:'1rem', borderRadius:'8px'}}>
              <div style={{display:'flex', gap:'0.5rem'}}>
                <div className="form-input-group" style={{flex:1, marginBottom:0}}>
                  <select value={newCardType} onChange={(e) => setNewCardType(e.target.value)} style={{width:'100%'}}>
                    <option value="VISA_DEBIT">Visa Secure Debit</option>
                    <option value="MASTERCARD_PREMIUM">Mastercard Premium</option>
                  </select>
                </div>
                <div className="form-input-group" style={{flex:1, marginBottom:0}}>
                  <input
                    type="number"
                    value={newCardLimit}
                    onChange={(e) => setNewCardLimit(e.target.value)}
                    placeholder="Card spend limit ($)"
                    required
                    min="1"
                    style={{width:'100%'}}
                  />
                </div>
                <button type="submit" className="btn-primary" style={{marginTop:0, whiteSpace:'nowrap', padding:'0 1rem'}} disabled={bankingProductLoading}>
                  Generate Card
                </button>
              </div>
            </form>

            {/* Cards Display Row */}
            <div style={{display:'flex', flexDirection:'column', gap:'1rem'}}>
              {(!cardsData || cardsData.length === 0) ? (
                <p style={{fontSize:'0.85rem', color:'var(--text-muted)', textAlign:'center', padding:'2rem'}}>
                  No active virtual cards generated yet.
                </p>
              ) : (
                cardsData.map((card: any) => (
                  <div key={card.id} style={{
                    background: card.status === 'FROZEN'
                      ? 'linear-gradient(135deg, #1f2937 0%, #111827 100%)'
                      : 'linear-gradient(135deg, #1e1b4b 0%, #311042 100%)',
                    border: card.status === 'FROZEN' ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(139, 92, 246, 0.2)',
                    padding: '1.25rem', borderRadius: '12px',
                    display: 'flex', flexDirection: 'column', gap: '1rem',
                    position: 'relative', boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                    opacity: card.status === 'FROZEN' ? 0.75 : 1
                  }}>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
                      <span style={{fontSize:'0.75rem', letterSpacing:'1.5px', color:'rgba(255,255,255,0.6)'}}>
                        {card.card_type.replace('_', ' ')}
                      </span>
                      <span className={`status-badge ${card.status === 'ACTIVE' ? 'approved' : 'blocked'}`}>
                        {card.status}
                      </span>
                    </div>
                    
                    <div style={{fontSize:'1.2rem', letterSpacing:'3px', fontFamily:'monospace', margin:'0.5rem 0', color:'#fff'}}>
                      {card.card_number.replace(/(\d{4})/g, '$1 ')}
                    </div>

                    <div style={{display:'flex', justifyContent:'space-between', fontSize:'0.75rem', color:'rgba(255,255,255,0.7)'}}>
                      <div>
                        <span>CARD HOLDER</span>
                        <p style={{color:'#fff', fontWeight:600, marginTop:'2px'}}>{card.card_holder}</p>
                      </div>
                      <div style={{textAlign:'right'}}>
                        <span>EXP / CVV</span>
                        <p style={{color:'#fff', fontWeight:600, marginTop:'2px'}}>{card.expiry_date} / {card.cvv}</p>
                      </div>
                    </div>

                    <div style={{borderTop:'1px solid rgba(255,255,255,0.06)', paddingTop:'0.75rem', display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                      <span style={{fontSize:'0.75rem', color:'var(--text-muted)'}}>
                        Spend Limit: <strong>${card.spend_limit.toLocaleString()}</strong>
                      </span>
                      
                      <div style={{display:'flex', gap:'0.4rem'}}>
                        <button
                          onClick={async () => {
                            const newLimit = prompt("Enter new spend limit for this card ($):", card.spend_limit.toString());
                            if (!newLimit || isNaN(Number(newLimit))) return;
                            setBankingProductLoading(true);
                            try {
                              await api.bankingProducts.cardsUpdateLimit(card.id, Number(newLimit));
                              refetchCards();
                            } catch (e: any) {
                              alert(e.message || "Failed to update card limit.");
                            }
                            setBankingProductLoading(false);
                          }}
                          className="action-btn"
                          style={{fontSize:'0.75rem', padding:'0.3rem 0.6rem'}}
                        >
                          Edit Limit
                        </button>
                        <button
                          onClick={async () => {
                            setBankingProductLoading(true);
                            try {
                              await api.bankingProducts.cardsToggleStatus(card.id);
                              refetchCards();
                            } catch (e: any) {
                              alert(e.message || "Failed to toggle card status.");
                            }
                            setBankingProductLoading(false);
                          }}
                          className={card.status === 'ACTIVE' ? 'action-btn danger' : 'action-btn primary'}
                          style={{fontSize:'0.75rem', padding:'0.3rem 0.6rem'}}
                        >
                          {card.status === 'ACTIVE' ? 'Freeze' : 'Unfreeze'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* FIXED DEPOSITS (FD) */}
          <div className="glass-card">
            <div className="card-header">
              <h2 className="card-title"><ShieldCheck className="menu-icon" /> Guaranteed Growth Fixed Deposits</h2>
            </div>

            {/* Open FD Form */}
            <form onSubmit={async (e) => {
              e.preventDefault();
              if (!fdPrincipal) return;
              setBankingProductLoading(true);
              setBankingProductStatus(null);
              try {
                await api.bankingProducts.fdCreate({
                  principal_amount: Number(fdPrincipal),
                  duration_months: Number(fdDuration)
                });
                refetchFd();
                refetchAllBankingData();
                setFdPrincipal('');
                setBankingProductStatus({ type: 'success', message: 'Fixed Deposit created and locked successfully!' });
              } catch (err: any) {
                setBankingProductStatus({ type: 'error', message: err.message || 'Failed to create FD.' });
              }
              setBankingProductLoading(false);
            }} style={{backgroundColor:'rgba(255,255,255,0.02)', padding:'1.25rem', borderRadius:'8px', marginBottom:'1.5rem'}}>
              <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.75rem', marginBottom:'1rem'}}>
                <div className="form-input-group" style={{marginBottom:0}}>
                  <label>FD Amount ($)</label>
                  <input
                    type="number"
                    value={fdPrincipal}
                    onChange={(e) => setFdPrincipal(e.target.value)}
                    placeholder="e.g. 10000"
                    required
                    min="1"
                  />
                </div>
                <div className="form-input-group" style={{marginBottom:0}}>
                  <label>Duration & Rate</label>
                  <select value={fdDuration} onChange={(e) => setFdDuration(e.target.value)}>
                    <option value="6">6 Months (5.5% p.a.)</option>
                    <option value="12">12 Months (7.0% p.a.)</option>
                    <option value="24">24 Months (7.5% p.a.)</option>
                    <option value="36">36 Months (8.0% p.a.)</option>
                  </select>
                </div>
              </div>
              
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', backgroundColor:'rgba(255,255,255,0.03)', padding:'0.6rem 0.8rem', borderRadius:'6px', fontSize:'0.8rem', marginBottom:'1rem'}}>
                <span style={{color:'var(--text-muted)'}}>ESTIMATED RETURNS</span>
                <strong style={{color:'var(--success)'}}>
                  {fdPrincipal ? (() => {
                    const amt = Number(fdPrincipal);
                    const rate = Number(fdDuration) < 12 ? 5.5 : Number(fdDuration) < 24 ? 7.0 : Number(fdDuration) < 36 ? 7.5 : 8.0;
                    const interest = amt * (rate / 100) * (Number(fdDuration) / 12);
                    return `Total Payout: $${(amt + interest).toLocaleString(undefined, {maximumFractionDigits:2})}`;
                  })() : 'Enter principal amount'}
                </strong>
              </div>

              <button type="submit" className="btn-primary" style={{width:'100%', marginTop:0}} disabled={bankingProductLoading}>
                Confirm & Book Deposit
              </button>
            </form>

            {/* FDs List */}
            <div style={{display:'flex', flexDirection:'column', gap:'0.75rem'}}>
              {(!fdData || fdData.length === 0) ? (
                <p style={{fontSize:'0.85rem', color:'var(--text-muted)', textAlign:'center', padding:'2rem'}}>
                  No active term deposits found.
                </p>
              ) : (
                fdData.map((fd: any) => (
                  <div key={fd.id} style={{
                    backgroundColor: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: '8px', padding: '1rem',
                    display: 'flex', flexDirection: 'column', gap: '0.6rem'
                  }}>
                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                      <span style={{fontSize:'0.85rem', fontWeight:600, color:'#fff'}}>
                        Fixed Deposit #{fd.id}
                      </span>
                      <span className={`status-badge ${
                        fd.status === 'ACTIVE' ? 'approved' : fd.status === 'MATURED' ? 'approved' : 'blocked'
                      }`}>
                        {fd.status}
                      </span>
                    </div>

                    <div style={{display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'0.5rem', fontSize:'0.78rem', color:'var(--text-muted)'}}>
                      <div>
                        <span>PRINCIPAL</span>
                        <p style={{color:'#fff', fontWeight:600}}>${fd.principal_amount.toLocaleString()}</p>
                      </div>
                      <div>
                        <span>RATE</span>
                        <p style={{color:'#fff', fontWeight:600}}>{fd.interest_rate}%</p>
                      </div>
                      <div>
                        <span>MATURITY</span>
                        <p style={{color:'var(--success)', fontWeight:600}}>${fd.maturity_amount.toLocaleString()}</p>
                      </div>
                    </div>

                    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', borderTop:'1px solid rgba(255,255,255,0.04)', paddingTop:'0.6rem', fontSize:'0.72rem'}}>
                      <span style={{color:'var(--text-muted)'}}>
                        Matures: {new Date(fd.matures_at).toLocaleDateString()}
                      </span>
                      {fd.status === 'ACTIVE' && (
                        <button
                          onClick={async () => {
                            if (!confirm("Are you sure you want to prematurely liquidate this FD? A 1% penalty deduction will be applied on accrued returns.")) return;
                            setBankingProductLoading(true);
                            try {
                              await api.bankingProducts.fdLiquidate(fd.id);
                              refetchFd();
                              refetchAllBankingData();
                              setBankingProductStatus({ type: 'success', message: 'Fixed Deposit liquidated prematurely. Account credited.' });
                            } catch (e: any) {
                              alert(e.message || "Failed to liquidate fixed deposit.");
                            }
                            setBankingProductLoading(false);
                          }}
                          className="action-btn danger"
                          style={{fontSize:'0.7rem', padding:'0.2rem 0.5rem'}}
                        >
                          Liquidate Premature
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

        {/* SECURITY SCORE REWARDS & OFFERS */}
        <div className="glass-card" style={{marginTop:'1.5rem'}}>
          <div className="card-header">
            <h2 className="card-title"><Gift className="menu-icon" /> Personalized Safety Rewards & Cashbacks</h2>
            <p style={{fontSize:'0.8rem', color:'var(--text-muted)', marginTop:'0.25rem'}}>
              Keep your security score high by resolving drills to unlock premium partner voucher offers and card cashbacks.
            </p>
          </div>
          
          <div style={{display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(280px, 1fr))', gap:'1rem', marginTop:'1rem'}}>
            {offersData?.map((offer: any) => (
              <div key={offer.id} style={{
                backgroundColor: offer.unlocked ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255,255,255,0.01)',
                border: offer.unlocked ? '1px solid rgba(16, 185, 129, 0.2)' : '1px solid rgba(255,255,255,0.05)',
                borderRadius:'10px', padding:'1.25rem', display:'flex', flexDirection:'column', gap:'0.75rem',
                opacity: offer.unlocked ? 1 : 0.65, transition:'all 0.2s ease', position:'relative'
              }}>
                <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                  <span style={{fontSize:'0.7rem', padding:'0.2rem 0.5rem', backgroundColor:'rgba(255,255,255,0.05)', borderRadius:'4px', color:'var(--text-secondary)'}}>
                    {offer.category}
                  </span>
                  <span className={`status-badge ${offer.unlocked ? 'approved' : 'blocked'}`}>
                    {offer.unlocked ? 'UNLOCKED' : `LOCKED (Req ${offer.unlock_score}%)`}
                  </span>
                </div>

                <div>
                  <h3 style={{fontSize:'0.95rem', color:'#fff', marginBottom:'0.25rem'}}>{offer.title}</h3>
                  <p style={{fontSize:'0.78rem', color:'var(--text-muted)', lineHeight:'1.4'}}>{offer.description}</p>
                </div>

                <div style={{marginTop:'auto', borderTop:'1px solid rgba(255,255,255,0.04)', paddingTop:'0.75rem', display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                  <span style={{fontSize:'0.82rem', color:'var(--success)', fontWeight:700}}>{offer.reward_rate}</span>
                  {offer.unlocked ? (
                    <span style={{fontSize:'0.72rem', letterSpacing:'1px', color:'var(--primary)', fontWeight:700, padding:'0.2rem 0.5rem', backgroundColor:'rgba(99,102,241,0.15)', borderRadius:'4px'}}>
                      CODE: NIRNAYSECURE
                    </span>
                  ) : (
                    <span style={{fontSize:'0.72rem', color:'var(--text-muted)'}}>Locked</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </>
  );
};
