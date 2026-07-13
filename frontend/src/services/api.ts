const API_BASE_URL = 'http://localhost:8000/api/v1';

// Get stored JWT token
export const getAuthToken = () => localStorage.getItem('nirnay_token');

// Set JWT token
export const setAuthToken = (token: string) => localStorage.setItem('nirnay_token', token);

// Clear JWT token
export const clearAuthToken = () => localStorage.removeItem('nirnay_token');

// Generic request wrapper with auth headers
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = 'An error occurred';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return response.json() as Promise<T>;
}

export const api = {
  // Auth API
  auth: {
    register: (data: any) => request<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    login: (data: any) => request<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    me: () => request<any>('/auth/me'),
    updateProfile: (data: any) => request<any>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    completeTour: () => request<any>('/auth/tour-complete', {
      method: 'POST',
    }),
  },

  // Recipient API
  recipients: {
    list: () => request<any[]>('/recipients'),
    create: (data: { name: string; account_number: string; bank_name: string }) => 
      request<any>('/recipients', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Transaction API
  transactions: {
    list: () => request<any[]>('/transactions'),
    initiate: (data: { recipient_id: number; amount: number; device: string; location: string }) =>
      request<any>('/transactions/initiate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    authenticate: (data: { transaction_id: number; password?: string; mpin?: string; otp?: string }) =>
      request<any>('/transactions/authenticate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    clarify: (data: { transaction_id: number; response_text: string }) =>
      request<any>('/transactions/clarify', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getAuditLog: (transactionId: number) =>
      request<any>(`/transactions/${transactionId}/audit`),
    getReport: (transactionId: number) =>
      request<any>(`/transactions/${transactionId}/report`),
  },

  // Dashboard / User Details
  dashboard: {
    summary: () => request<any>('/dashboard/summary'),
    digitalTwin: () => request<any>('/dashboard/digital-twin'),
    analytics: () => request<any>('/dashboard/analytics'),
    heatmap: () => request<any>('/dashboard/heatmap'),
  },

  // Admin API
  admin: {
    escalations: () => request<any[]>('/admin/escalations'),
    override: (data: { transaction_id: number; action: string }) =>
      request<any>('/admin/override', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Scam Drills API
  drills: {
    getScenario: () => request<any>('/drills/scenario'),
    submitAnswer: (data: { scenario_id: string; selected_option: string }) =>
      request<any>('/drills/answer', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Neo-Banking API
  banking: {
    deposit: (data: { amount: number; category: string }) => request<any>('/banking/deposit', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    passbook: () => request<any[]>('/banking/passbook'),
    balance: () => request<any>('/banking/balance'),
    lookup: (accountNumber: string) => request<any>(`/banking/lookup?account_number=${accountNumber}`),
    p2pTransfer: (data: { recipient_account_number: string; amount: number; device: string; location: string }) => request<any>('/banking/p2p-transfer', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },

  // Security Operations API
  securityOps: {
    freeze: () => request<any>('/security/freeze', { method: 'POST' }),
    unfreeze: (data: { mpin: string }) => request<any>('/security/unfreeze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    activityLog: () => request<any[]>('/security/activity-log'),
    updateLimit: (data: { limit: number; mpin: string }) => request<any>('/security/update-limit', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    changePassword: (data: any) => request<any>('/security/change-password', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  },

  // Banking Products API
  bankingProducts: {
    cardsList: () => request<any[]>('/banking-products/cards'),
    cardsCreate: (data: { card_type: string; spend_limit: number }) => request<any>('/banking-products/cards', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    cardsToggleStatus: (cardId: number) => request<any>(`/banking-products/cards/${cardId}/toggle-status`, {
      method: 'POST',
    }),
    cardsUpdateLimit: (cardId: number, spendLimit: number) => request<any>(`/banking-products/cards/${cardId}/limit`, {
      method: 'PUT',
      body: JSON.stringify({ spend_limit: spendLimit }),
    }),
    fdList: () => request<any[]>('/banking-products/fd'),
    fdCreate: (data: { principal_amount: number; duration_months: number }) => request<any>('/banking-products/fd', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    fdLiquidate: (fdId: number) => request<any>(`/banking-products/fd/${fdId}/liquidate`, {
      method: 'POST',
    }),
    offersList: () => request<any[]>('/banking-products/offers'),
  }
};
