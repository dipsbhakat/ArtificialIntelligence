// Core type definitions for Smart Habit Tracker

export interface User {
  id: string;
  email: string;
  displayName?: string;
  photoURL?: string;
  createdAt: Date;
  updatedAt: Date;
  isPremium: boolean;
  subscriptionExpiresAt?: Date;
}

export interface Habit {
  id: string;
  userId: string;
  title: string;
  description?: string;
  category: HabitCategory;
  frequency: HabitFrequency;
  targetCount: number;
  unit: string;
  color: string;
  icon: string;
  reminderTime?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
  streak: number;
  bestStreak: number;
}

export interface HabitCompletion {
  id: string;
  habitId: string;
  userId: string;
  date: string; // YYYY-MM-DD format
  count: number;
  note?: string;
  createdAt: Date;
}

export interface Achievement {
  id: string;
  userId: string;
  type: AchievementType;
  title: string;
  description: string;
  unlockedAt: Date;
  habitId?: string; // If achievement is habit-specific
}

export type HabitCategory = 
  | 'health'
  | 'fitness'
  | 'productivity'
  | 'mindfulness'
  | 'learning'
  | 'social'
  | 'creativity'
  | 'lifestyle'
  | 'other';

export type HabitFrequency = 
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'custom';

export type AchievementType =
  | 'streak'
  | 'completion'
  | 'consistency'
  | 'milestone'
  | 'social';

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export interface HabitsState {
  habits: Habit[];
  completions: HabitCompletion[];
  isLoading: boolean;
  error: string | null;
}

export type NavigationParams = {
  Home: undefined;
  HabitDetail: { habitId: string };
  AddHabit: undefined;
  EditHabit: { habitId: string };
  Profile: undefined;
  Settings: undefined;
  Analytics: undefined;
  Premium: undefined;
  MainTabs: undefined;
  Login: undefined;
  Register: undefined;
}
