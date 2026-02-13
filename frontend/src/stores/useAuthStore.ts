import { create } from 'zustand'
import { authApi } from '@/lib/api'

interface User {
    id: string
    name: string
    email: string
}

interface AuthState {
    user: User | null
    isAuthenticated: boolean
    isLoading: boolean
    isInitialized: boolean
    login: (params: any) => Promise<void>
    register: (params: any) => Promise<void>
    logout: () => void
    checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    isInitialized: false,

    login: async (params) => {
        set({ isLoading: true })
        try {
            const response = await authApi.login(params)
            localStorage.setItem('token', response.tokens.access_token)
            set({ user: response.user, isAuthenticated: true, isInitialized: true })
        } catch (error) {
            throw error
        } finally {
            set({ isLoading: false })
        }
    },

    register: async (params) => {
        set({ isLoading: true })
        try {
            const response = await authApi.register(params)
            localStorage.setItem('token', response.tokens.access_token)
            set({ user: response.user, isAuthenticated: true, isInitialized: true })
        } catch (error) {
            throw error
        } finally {
            set({ isLoading: false })
        }
    },

    logout: () => {
        localStorage.removeItem('token')
        set({ user: null, isAuthenticated: false, isInitialized: true, isLoading: false })
    },

    checkAuth: async () => {
        const token = localStorage.getItem('token')
        if (!token) {
            set({ isLoading: false, isAuthenticated: false, user: null, isInitialized: true })
            return
        }

        try {
            const user = await authApi.getMe()
            set({ user, isAuthenticated: true, isInitialized: true })
        } catch (error) {
            localStorage.removeItem('token')
            set({ user: null, isAuthenticated: false, isInitialized: true })
        } finally {
            set({ isLoading: false })
        }
    }
}))
