import React from 'react';
import { Download, BookOpen } from 'lucide-react';

interface PassbookViewProps {
  passbookData: any[] | undefined;
  username: string;
}

export const PassbookView: React.FC<PassbookViewProps> = ({ passbookData, username }) => {
  return (
    <>
      <header className="page-header">
        <div>
          <h1 className="page-title">Digital Bank Passbook</h1>
          <p className="page-subtitle">Real-time ledger audit trail showing all transaction credits and debits</p>
        </div>
        <button
          className="action-btn primary"
          onClick={() => {
            if (!passbookData) return;
            const headers = ['ID', 'Type', 'Category', 'Counterparty', 'Amount ($)', 'Balance After ($)', 'Date & Time', 'Reference ID'];
            const rows = passbookData.map((e: any) => [
              e.id,
              e.type,
              e.category,
              e.counterparty || 'N/A',
              e.amount,
              e.balance_after,
              new Date(e.timestamp).toLocaleString().replace(/,/g, ''),
              e.reference_id || 'N/A'
            ]);
            const csvContent = "data:text/csv;charset=utf-8," 
              + [headers.join(','), ...rows.map((r: any) => r.join(','))].join('\n');
            const encodedUri = encodeURI(csvContent);
            const a = document.createElement('a');
            a.href = encodedUri;
            a.download = `nirnay_passbook_${username}.csv`;
            a.click();
          }}
          style={{display:'flex', alignItems:'center', gap:'0.4rem', padding:'0.6rem 1.2rem'}}
        >
          <Download style={{width:'16px', height:'16px'}} /> Export Statement
        </button>
      </header>

      <div className="page-content">
        <div className="glass-card">
          <div className="card-header" style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h2 className="card-title"><BookOpen className="menu-icon" /> Statement Log Book</h2>
          </div>
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Type</th>
                  <th>Category</th>
                  <th>Counterparty</th>
                  <th>Amount</th>
                  <th>Running Balance</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {(!passbookData || passbookData.length === 0) ? (
                  <tr>
                    <td colSpan={7} style={{textAlign: 'center', padding: '3rem', color: 'var(--text-muted)'}}>
                      No transaction ledger records found.
                    </td>
                  </tr>
                ) : (
                  passbookData.map((entry: any) => (
                    <tr key={entry.id}>
                      <td><strong>#{entry.id}</strong></td>
                      <td>
                        <span className={`status-badge ${entry.type === 'CREDIT' ? 'approved' : 'blocked'}`}>
                          {entry.type === 'CREDIT' ? '↓ CREDIT' : '↑ DEBIT'}
                        </span>
                      </td>
                      <td><span style={{fontSize:'0.8rem', textTransform:'uppercase'}}>{entry.category.replace(/_/g, ' ')}</span></td>
                      <td>{entry.counterparty || 'N/A'}</td>
                      <td>
                        <strong style={{color: entry.type === 'CREDIT' ? 'var(--success)' : 'var(--danger)'}}>
                          {entry.type === 'CREDIT' ? '+' : '-'}${entry.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}
                        </strong>
                      </td>
                      <td><strong>${entry.balance_after.toLocaleString(undefined, {minimumFractionDigits: 2})}</strong></td>
                      <td>{new Date(entry.timestamp).toLocaleString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
};
