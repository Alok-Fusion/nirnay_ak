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
      // JSON parsing failed, use status text
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
  },

  // Dashboard / User Details
  dashboard: {
    summary: () => request<any>('/dashboard/summary'),
    digitalTwin: () => request<any>('/dashboard/digital-twin'),
  },

  // Admin API
  admin: {
    escalations: () => request<any[]>('/admin/escalations'),
    override: (data: { transaction_id: number; action: string }) =>
      request<any>('/admin/override', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  }
};
