import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Auth store
export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      setAuth: (user, token) =>
        set({ user, token, isAuthenticated: true }),
      
      clearAuth: () =>
        set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)

// Eval data store
export const useEvalStore = create((set) => ({
  evalData: null,
  parsedCourses: [],
  remainingCredits: 0,
  
  setEvalData: (data) =>
    set({
      evalData: data,
      parsedCourses: data.courses || [],
      remainingCredits: data.remainingCredits || 0,
    }),
  
  clearEvalData: () =>
    set({
      evalData: null,
      parsedCourses: [],
      remainingCredits: 0,
    }),
}))

// Preferences store
export const usePreferencesStore = create((set) => ({
  preferences: {
    minCredits: 12,
    maxCredits: 15,
    preferredDays: ['M', 'W', 'F'],
    startTime: '09:00',
    endTime: '17:00',
    campus: 'atlanta',
    modalities: ['in-person'],
  },
  
  setPreferences: (prefs) =>
    set((state) => ({
      preferences: { ...state.preferences, ...prefs },
    })),
  
  resetPreferences: () =>
    set({
      preferences: {
        minCredits: 12,
        maxCredits: 15,
        preferredDays: ['M', 'W', 'F'],
        startTime: '09:00',
        endTime: '17:00',
        campus: 'atlanta',
        modalities: ['in-person'],
      },
    }),
}))

// Schedule results store
export const useScheduleStore = create((set) => ({
  currentSchedule: null,
  schedules: [],
  isLoading: false,
  error: null,
  
  setCurrentSchedule: (schedule) =>
    set({ currentSchedule: schedule }),
  
  addSchedule: (schedule) =>
    set((state) => ({
      schedules: [...state.schedules, schedule],
    })),
  
  updateSchedule: (id, updates) =>
    set((state) => ({
      schedules: state.schedules.map((s) =>
        s.id === id ? { ...s, ...updates } : s
      ),
    })),
  
  deleteSchedule: (id) =>
    set((state) => ({
      schedules: state.schedules.filter((s) => s.id !== id),
    })),
  
  setLoading: (isLoading) =>
    set({ isLoading }),
  
  setError: (error) =>
    set({ error }),
  
  clearError: () =>
    set({ error: null }),
}))

// UI state store
export const useUIStore = create((set) => ({
  sidebarOpen: false,
  modalOpen: false,
  theme: 'light',
  
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  openModal: () =>
    set({ modalOpen: true }),
  
  closeModal: () =>
    set({ modalOpen: false }),
  
  setTheme: (theme) =>
    set({ theme }),
}))
