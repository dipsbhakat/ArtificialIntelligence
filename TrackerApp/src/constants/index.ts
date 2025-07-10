// App constants and configuration

export const COLORS = {
  primary: '#6366F1',
  secondary: '#8B5CF6',
  accent: '#10B981',
  background: '#F9FAFB',
  surface: '#FFFFFF',
  text: '#111827',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
  error: '#EF4444',
  warning: '#F59E0B',
  success: '#10B981',
  info: '#3B82F6',
} as const;

export const HABIT_CATEGORIES = [
  { value: 'health', label: 'Health', icon: 'medical-outline', color: '#EF4444' },
  { value: 'fitness', label: 'Fitness', icon: 'fitness-outline', color: '#F59E0B' },
  { value: 'productivity', label: 'Productivity', icon: 'briefcase-outline', color: '#3B82F6' },
  { value: 'mindfulness', label: 'Mindfulness', icon: 'leaf-outline', color: '#10B981' },
  { value: 'learning', label: 'Learning', icon: 'book-outline', color: '#8B5CF6' },
  { value: 'social', label: 'Social', icon: 'people-outline', color: '#EC4899' },
  { value: 'creativity', label: 'Creativity', icon: 'color-palette-outline', color: '#F97316' },
  { value: 'lifestyle', label: 'Lifestyle', icon: 'home-outline', color: '#06B6D4' },
  { value: 'other', label: 'Other', icon: 'ellipsis-horizontal-outline', color: '#6B7280' },
] as const;

export const HABIT_FREQUENCIES = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'custom', label: 'Custom' },
] as const;

export const ACHIEVEMENT_TYPES = {
  FIRST_HABIT: {
    title: 'Getting Started',
    description: 'Created your first habit',
    icon: 'trophy-outline',
  },
  WEEK_STREAK: {
    title: 'Week Warrior',
    description: 'Maintained a 7-day streak',
    icon: 'flame-outline',
  },
  MONTH_STREAK: {
    title: 'Month Master',
    description: 'Maintained a 30-day streak',
    icon: 'medal-outline',
  },
  HUNDRED_DAYS: {
    title: 'Century Club',
    description: 'Maintained a 100-day streak',
    icon: 'star-outline',
  },
} as const;

export const SUBSCRIPTION_PLANS = {
  FREE: {
    name: 'Free',
    maxHabits: 3,
    features: [
      'Track up to 3 habits',
      'Basic analytics',
      'Daily reminders',
    ],
  },
  PREMIUM: {
    name: 'Premium',
    maxHabits: -1, // Unlimited
    features: [
      'Unlimited habits',
      'Advanced analytics',
      'Habit stacking',
      'Social features',
      'Custom themes',
      'Export data',
      'Priority support',
    ],
  },
} as const;

export const API_ENDPOINTS = {
  BASE_URL: process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:3000',
  HABITS: '/habits',
  COMPLETIONS: '/completions',
  ACHIEVEMENTS: '/achievements',
  USER: '/user',
} as const;

export const STORAGE_KEYS = {
  USER_TOKEN: '@habit_tracker_user_token',
  USER_PREFERENCES: '@habit_tracker_preferences',
  OFFLINE_DATA: '@habit_tracker_offline_data',
} as const;

export const ANIMATION_DURATION = {
  SHORT: 200,
  MEDIUM: 300,
  LONG: 500,
} as const;

export const SCREEN_NAMES = {
  HOME: 'Home',
  HABIT_DETAIL: 'HabitDetail',
  ADD_HABIT: 'AddHabit',
  EDIT_HABIT: 'EditHabit',
  PROFILE: 'Profile',
  SETTINGS: 'Settings',
  ANALYTICS: 'Analytics',
  PREMIUM: 'Premium',
  AUTH: 'Auth',
  LOGIN: 'Login',
  REGISTER: 'Register',
} as const;
