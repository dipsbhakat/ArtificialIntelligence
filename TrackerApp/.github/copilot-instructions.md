<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Smart Habit Tracker App - Development Guidelines

## Project Overview
This is a React Native Expo TypeScript project for a Smart Habit Tracker app with the following key features:
- Cross-platform mobile app (iOS/Android)
- Firebase/Supabase backend integration
- Premium subscription model with freemium features
- Modern navigation and state management

## Technology Stack
- **Frontend**: React Native with Expo and TypeScript
- **Backend**: Firebase (Authentication, Firestore, Cloud Functions)
- **State Management**: Redux Toolkit with RTK Query
- **Navigation**: React Navigation v6
- **UI Library**: React Native Elements or NativeBase
- **Payments**: RevenueCat for subscription management
- **Analytics**: Firebase Analytics + Mixpanel

## Code Style Guidelines
- Use TypeScript for all new files with strict typing
- Follow React Native and Expo best practices
- Use functional components with hooks
- Implement proper error handling and loading states
- Use descriptive variable and function names
- Follow atomic design principles for components

## Project Structure
```
src/
├── components/         # Reusable UI components
├── screens/           # Screen components
├── navigation/        # Navigation configuration
├── services/          # API services and business logic
├── store/             # Redux store, slices, and RTK Query
├── types/             # TypeScript type definitions
├── utils/             # Utility functions and helpers
├── hooks/             # Custom React hooks
└── constants/         # App constants and configuration
```

## Key Features to Implement
1. **Core Features** (MVP):
   - User authentication (email/social login)
   - Habit creation and management
   - Daily habit tracking with streaks
   - Basic analytics and progress visualization

2. **Premium Features**:
   - Habit stacking suggestions
   - Advanced analytics and insights
   - Social features and accountability
   - Smart reminders and notifications
   - Custom themes and unlimited habits

## Database Schema
- Users: Authentication and profile data
- Habits: Habit definitions and configurations
- Completions: Daily habit completion records
- Achievements: User milestone tracking
- Social: Friend connections and shared achievements

## Development Priorities
1. Start with MVP features for rapid prototyping
2. Implement proper TypeScript interfaces for all data models
3. Set up proper error boundaries and loading states
4. Ensure accessibility compliance (screen readers, contrast)
5. Implement offline-first architecture with data synchronization
6. Focus on performance optimization and smooth animations

## Security & Privacy
- Implement proper data encryption for sensitive information
- Follow GDPR compliance for user data handling
- Use secure authentication flows
- Implement proper input validation and sanitization
