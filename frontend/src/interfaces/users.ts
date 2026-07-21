export interface LoginData {
    username: string;
    password: string;
}

export interface UserProfile {
    id:  number;
    username: string;
    rol: string;
}

export interface UserLogin {
    access: string;
    refresh: string;
    user: UserProfile;
}

export interface AuthContextType{
    user: UserProfile | null;
    isAuthenticated: boolean;
    loading: boolean;
    login: (authData: UserLogin) => void;
    logout: () => void;
}
