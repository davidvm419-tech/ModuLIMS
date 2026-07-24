import { afterEach, describe, it, expect, beforeEach, vi } from 'vitest';
import apiFetch from '../apiFetch';


const mockApiBase = 'http://localhost:8000';

describe('apiFetch', () => {

    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();

        // mock environment variable
        vi.stubEnv('VITE_API_URL', mockApiBase);

        // mock window.location.href
        Object.defineProperty(window, 'location', {
        writable: true,
        value: { href: '' },
        });
    });

    afterEach(() => {
        vi.unstubAllEnvs();
        vi.restoreAllMocks();
    });
    
  it('makes a GET request with Authorization header if accessToken exists', async () => {
    localStorage.setItem('accessToken', 'test-access-token');

    const mockResponse = new Response(JSON.stringify({ data: 'samples' }), { status: 200 });
    const fetchSpy = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal('fetch', fetchSpy);

    const response = await apiFetch('samples');

    expect(fetchSpy).toHaveBeenCalledWith(`${mockApiBase}/samples/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer test-access-token',
      },
    });

    expect(response.status).toBe(200);
  });

  it('serializes body data when method is POST', async () => {
    const mockData = { name: 'Cafeína', quantity: '100 tabletas' };
    const mockResponse = new Response(JSON.stringify({ success: true }), { status: 201 });
    const fetchSpy = vi.fn().mockResolvedValue(mockResponse);
    vi.stubGlobal('fetch', fetchSpy);

    await apiFetch('samples', 'POST', mockData);

    expect(fetchSpy).toHaveBeenCalledWith(`${mockApiBase}/samples/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(mockData),
    });
  });

  it('refreshes token on 401 and retries original request when refresh succeeds', async () => {
    localStorage.setItem('accessToken', 'expired-access-token');
    localStorage.setItem('refreshToken', 'valid-refresh-token');

    const first401Response = new Response(null, { status: 401 });
    const refreshOkResponse = new Response(
      JSON.stringify({ access: 'new-access-token', refresh: 'new-refresh-token' }),
      { status: 200 }
    );
    const retried200Response = new Response(JSON.stringify({ data: 'success' }), { status: 200 });

    // mock sequential fetch calls: 1. Original (401), 2. Refresh (200), 3. Retry original (200)
    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(first401Response)
      .mockResolvedValueOnce(refreshOkResponse)
      .mockResolvedValueOnce(retried200Response);

    vi.stubGlobal('fetch', fetchSpy);

    const response = await apiFetch('samples');

    // verify refresh API was called
    expect(fetchSpy).toHaveBeenNthCalledWith(2, `${mockApiBase}/api/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: 'valid-refresh-token' }),
    });

    // verify new tokens saved to localStorage
    expect(localStorage.getItem('accessToken')).toBe('new-access-token');
    expect(localStorage.getItem('refreshToken')).toBe('new-refresh-token');

    // verify original request was retried with new Bearer token
    expect(fetchSpy).toHaveBeenNthCalledWith(3, `${mockApiBase}/samples/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer new-access-token',
      },
    });

    expect(response.status).toBe(200);
  });

  it('clears storage and redirects to /login when 401 occurs and no refreshToken exists', async () => {
    localStorage.setItem('accessToken', 'expired-access-token');

    const response401 = new Response(null, { status: 401 });
    const fetchSpy = vi.fn().mockResolvedValue(response401);
    vi.stubGlobal('fetch', fetchSpy);

    await apiFetch('samples');

    expect(localStorage.length).toBe(0);
    expect(window.location.href).toBe('/login');
  });

  it('clears storage and redirects to /login when token refresh fails', async () => {
    localStorage.setItem('accessToken', 'expired-access-token');
    localStorage.setItem('refreshToken', 'invalid-refresh-token');

    const first401Response = new Response(null, { status: 401 });
    const refreshFailedResponse = new Response(null, { status: 401 });

    const fetchSpy = vi.fn()
      .mockResolvedValueOnce(first401Response)
      .mockResolvedValueOnce(refreshFailedResponse);

    vi.stubGlobal('fetch', fetchSpy);

    await apiFetch('samples');

    expect(localStorage.length).toBe(0);
    expect(window.location.href).toBe('/login');
  });
});
