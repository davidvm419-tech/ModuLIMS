import { renderHook, act } from '@testing-library/react';
import { afterEach, describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import { AuthProvider, useAuth } from '../AuthContext';
import type { UserProfile, UserLogin } from '../../../interfaces/users';

// test data
const user: UserProfile = { 
  id: 1, 
  username: 'analyst_test',
  role: 'analyst' 
};

const authData: UserLogin = {
  access: 'fake-jwt-access-token',
  refresh: 'fake-jwt-refresh-token',
  user: user,
};

// allows react  router to work on the test
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MemoryRouter>
    <AuthProvider>{children}</AuthProvider>
  </MemoryRouter>
);

describe('AuthContext', () => { //shows nice text on the terminal
  beforeEach(() => {
    // clear storage before each test
    localStorage.clear();
    // set faketimers and clear them before each test
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  // clear fake timers afteareach test
  afterEach(() => {
    vi.useRealTimers();
  })

  it('check if local  storage is actually empty', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('check if a user exists the data is correctly saved on local storage', () => {
    localStorage.setItem('accessToken', 'valid-token');
    localStorage.setItem('refreshToken', 'valid-rToken');
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('check if login correctly stores user data', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    // simulates login
    act(() => {
      result.current.login(authData);
    });

    // user correctly saved
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);

    // Check that the data is correctly saved on local storage
    expect(localStorage.getItem('accessToken')).toBe(authData.access);
    expect(localStorage.getItem('refreshToken')).toBe(authData.refresh);
    expect(JSON.parse(localStorage.getItem('user')!)).toEqual(user);
  });

  it('check if logout correctly cleans user data and closethe session', () => {
    localStorage.setItem('accessToken', authData.access);
    localStorage.setItem('refreshToken', authData.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(), { wrapper });

    // simulates logout
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('check that session is closed after 30 minutes of inactivity', () => {
    localStorage.setItem('accessToken', authData.access);
    localStorage.setItem('refreshToken', authData.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(),  { wrapper });

    // simulates 30 minutes have passed
    act(() => {
      vi.advanceTimersByTime(30 * 60 * 1000)
    });

    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('check that timer resets and session is still alive after user interacts', () => {
    localStorage.setItem('accessToken', authData.access);
    localStorage.setItem('refreshToken', authData.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(),  { wrapper });

    // simulate 25 minutes have passed
    act(() => {
      vi.advanceTimersByTime(25 * 60 * 1000);
    });

    // simulate user interaction
    act(() => {
      window.dispatchEvent(new Event('keydown'));
    });

    // simulate another 25 minutes have passed
    act(() => {
      vi.advanceTimersByTime(25 * 60 * 1000);
    });

    // session should still be alive
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('check that session is closed after 30 minutes in other window', () => {
    localStorage.setItem('accessToken', authData.access);
    localStorage.setItem('refreshToken', authData.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(),  { wrapper });

    // simulates user leaves the system tab    
    Object.defineProperty(document, 'visibilityState', {
      configurable: true,
      value:  'hidden',
    });

    act(() => {
      document.dispatchEvent(new Event('visibilitychange'));
    });

    // simulates more than 30 minutes have passed
    act(() => {
      vi.advanceTimersByTime(35 * 60  * 1000);
    });

    // simulates user returns to system tab
    Object.defineProperty(document, 'visibilityState',{
      configurable: true,
      value: 'visible'
    });

    act(() => {
      document.dispatchEvent(new Event('visibilitychange'));
    });
    
    // session should be closed
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('check that useAuth throws an error if is used outside the provider', () => {
  
    expect(() => renderHook(() => useAuth())).toThrow(
      'useAuth must be used with an AuthProvider'
    );
  });
});
