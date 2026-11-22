/**
 * Global state store using Zustand.
 * Manages auth state and toast notifications.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,

      setAuth: (user, token) => {
        localStorage.setItem('examvault_token', token)
        set({ user, token })
      },

      logout: () => {
        localStorage.removeItem('examvault_token')
        localStorage.removeItem('examvault_user')
        set({ user: null, token: null })
      },

      isAuthenticated: () => {
        const state = useAuthStore.getState()
        return !!state.token && !!state.user
      },
    }),
    {
      name: 'examvault_auth',
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
)

// Simple toast store
export const useToastStore = create((set) => ({
  toasts: [],
  addToast: (message, type = 'success') => {
    const id = Date.now()
    set((state) => ({ toasts: [...state.toasts, { id, message, type }] }))
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }))
    }, 3500)
  },
  removeToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}))
