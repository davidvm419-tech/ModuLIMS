import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
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

describe('AuthContext', () => { // clear storage before each test, shows nice text on the terminal
  beforeEach(() => {
    localStorage.clear();
  });

  it('check if local  storage is actually empty', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.loading).toBe(false);
  });

  it('check if a user exists the data is correctly saved on local storage', () => {
    localStorage.setItem('token', 'valid-token');
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('login() debe almacenar access, refresh y user en localStorage y actualizar el estado', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.login(authData);
    });

    // Verificamos estado del hook
    expect(result.current.user).toEqual(user);
    expect(result.current.isAuthenticated).toBe(true);

    // Verificamos guardado exacto en localStorage
    expect(localStorage.getItem('accessToken')).toBe(authData.access);
    expect(localStorage.getItem('refreshToken')).toBe(authData.refresh);
    expect(JSON.parse(localStorage.getItem('user')!)).toEqual(user);
  });

  it('logout() debe eliminar los tokens del localStorage y resetear el estado', () => {
    // 1. Simular sesión inicial
    localStorage.setItem('accessToken', authData.access);
    localStorage.setItem('refreshToken', authData.refresh);
    localStorage.setItem('user', JSON.stringify(user));

    const { result } = renderHook(() => useAuth(), { wrapper });

    // 2. Hacer logout
    act(() => {
      result.current.logout();
    });

    // 3. Verificaciones
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  it('debe lanzar un error si useAuth se usa fuera de AuthProvider', () => {
    // Para probar el throw error del custom hook
    expect(() => renderHook(() => useAuth())).toThrow(
      'useAuth must be used with an AuthProvider'
    );
  });
});