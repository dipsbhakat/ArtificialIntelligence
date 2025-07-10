import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { HabitsState, Habit, HabitCompletion } from '../../types';

const initialState: HabitsState = {
  habits: [],
  completions: [],
  isLoading: false,
  error: null,
};

const habitsSlice = createSlice({
  name: 'habits',
  initialState,
  reducers: {
    fetchHabitsStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchHabitsSuccess: (state, action: PayloadAction<Habit[]>) => {
      state.isLoading = false;
      state.habits = action.payload;
      state.error = null;
    },
    fetchHabitsFailure: (state, action: PayloadAction<string>) => {
      state.isLoading = false;
      state.error = action.payload;
    },
    addHabit: (state, action: PayloadAction<Habit>) => {
      state.habits.push(action.payload);
    },
    updateHabit: (state, action: PayloadAction<Habit>) => {
      const index = state.habits.findIndex(h => h.id === action.payload.id);
      if (index !== -1) {
        state.habits[index] = action.payload;
      }
    },
    deleteHabit: (state, action: PayloadAction<string>) => {
      state.habits = state.habits.filter(h => h.id !== action.payload);
      state.completions = state.completions.filter(c => c.habitId !== action.payload);
    },
    fetchCompletionsSuccess: (state, action: PayloadAction<HabitCompletion[]>) => {
      state.completions = action.payload;
    },
    addCompletion: (state, action: PayloadAction<HabitCompletion>) => {
      const existingIndex = state.completions.findIndex(
        c => c.habitId === action.payload.habitId && c.date === action.payload.date
      );
      if (existingIndex !== -1) {
        state.completions[existingIndex] = action.payload;
      } else {
        state.completions.push(action.payload);
      }
      
      // Update habit streak
      const habit = state.habits.find(h => h.id === action.payload.habitId);
      if (habit) {
        // Calculate new streak (simplified logic)
        habit.streak = calculateStreak(state.completions, action.payload.habitId);
        if (habit.streak > habit.bestStreak) {
          habit.bestStreak = habit.streak;
        }
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

// Helper function to calculate streak
function calculateStreak(completions: HabitCompletion[], habitId: string): number {
  const habitCompletions = completions
    .filter(c => c.habitId === habitId)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  
  let streak = 0;
  const today = new Date();
  
  for (let i = 0; i < habitCompletions.length; i++) {
    const completionDate = new Date(habitCompletions[i].date);
    const daysDiff = Math.floor((today.getTime() - completionDate.getTime()) / (1000 * 60 * 60 * 24));
    
    if (daysDiff === i) {
      streak++;
    } else {
      break;
    }
  }
  
  return streak;
}

export const {
  fetchHabitsStart,
  fetchHabitsSuccess,
  fetchHabitsFailure,
  addHabit,
  updateHabit,
  deleteHabit,
  fetchCompletionsSuccess,
  addCompletion,
  clearError,
} = habitsSlice.actions;

export default habitsSlice.reducer;
