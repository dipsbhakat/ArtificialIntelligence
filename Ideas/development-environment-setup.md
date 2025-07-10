# Smart Habit Tracker - Development Environment Setup

## 🛠️ Prerequisites Installation

### 1. Node.js & npm
```powershell
# Download and install Node.js LTS from nodejs.org
# Verify installation
node --version  # Should be 18.x or higher
npm --version   # Should be 9.x or higher
```

### 2. Git
```powershell
# Download Git from git-scm.com
# Verify installation
git --version
```

### 3. React Native CLI
```powershell
npm install -g @react-native-community/cli
```

### 4. Expo CLI (Recommended for faster development)
```powershell
npm install -g @expo/cli
```

## 📱 Platform-Specific Setup

### iOS Development (macOS only)
```bash
# Install Xcode from App Store
# Install Xcode Command Line Tools
xcode-select --install

# Install CocoaPods
sudo gem install cocoapods

# Install iOS Simulator (included with Xcode)
```

### Android Development
```powershell
# 1. Download Android Studio from developer.android.com
# 2. Install Android SDK (API level 33 or higher)
# 3. Set up environment variables in PowerShell profile

# Add to PowerShell profile (~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1)
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\platform-tools"
$env:PATH += ";$env:ANDROID_HOME\tools"

# Verify Android setup
adb --version
```

## 🔥 Firebase Setup

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create a project"
3. Project name: "habit-tracker-app"
4. Enable Google Analytics (recommended)
5. Choose default analytics account

### 2. Configure Firebase Services
```javascript
// Enable these services in Firebase Console:
// - Authentication (Email/Password, Google, Apple)
// - Firestore Database
// - Cloud Storage
// - Cloud Functions
// - Analytics
// - Crashlytics
// - Performance Monitoring
// - Remote Config
```

### 3. Get Firebase Configuration
```javascript
// Go to Project Settings > General > Your apps
// Add iOS app (com.yourcompany.habittracker)
// Add Android app (com.yourcompany.habittracker)
// Download google-services.json (Android) and GoogleService-Info.plist (iOS)
```

## 💳 Payment Setup (RevenueCat)

### 1. Create RevenueCat Account
1. Sign up at [RevenueCat](https://app.revenuecat.com)
2. Create new project: "HabitTracker"
3. Configure platforms (iOS, Android)

### 2. App Store Connect Setup (iOS)
1. Create app in App Store Connect
2. Set up in-app purchases:
   - Premium Monthly ($4.99)
   - Premium Yearly ($29.99)
3. Add test users for sandbox testing

### 3. Google Play Console Setup (Android)
1. Create app in Google Play Console
2. Set up in-app products:
   - Premium Monthly ($4.99)
   - Premium Yearly ($29.99)
3. Add test accounts

## 🚀 Project Initialization

### 1. Create Expo Project
```powershell
# Create new Expo project with TypeScript
npx create-expo-app HabitTracker --template

# Navigate to project
cd HabitTracker

# Install additional dependencies
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install @react-native-async-storage/async-storage
npm install react-native-reanimated react-native-gesture-handler
npm install date-fns uuid react-hook-form
npm install @react-native-community/datetimepicker
npm install react-native-vector-icons @expo/vector-icons
npm install expo-notifications expo-calendar expo-contacts
npm install expo-camera expo-image-picker expo-location
```

### 2. Firebase Integration
```powershell
# Install Firebase SDK
npm install firebase
npm install @react-native-firebase/app @react-native-firebase/auth
npm install @react-native-firebase/firestore @react-native-firebase/analytics
npm install @react-native-firebase/crashlytics @react-native-firebase/messaging
```

### 3. State Management & UI
```powershell
# State management
npm install zustand  # Lightweight alternative to Redux

# UI Components & Styling
npm install react-native-paper  # Material Design components
npm install react-native-chart-kit  # Charts for analytics
npm install react-native-svg  # SVG support for charts
npm install react-native-linear-gradient  # Gradient backgrounds
npm install react-native-haptic-feedback  # Haptic feedback
```

### 4. Development Tools
```powershell
# Development dependencies
npm install --save-dev @types/react @types/react-native
npm install --save-dev @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
npm install --save-dev jest @types/jest react-test-renderer
npm install --save-dev detox  # E2E testing
```

## 📁 Project Structure Setup

```
HabitTracker/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── common/         # Generic components
│   │   ├── habits/         # Habit-specific components
│   │   ├── analytics/      # Chart and analytics components
│   │   └── social/         # Social feature components
│   ├── screens/            # Screen components
│   │   ├── auth/          # Authentication screens
│   │   ├── habits/        # Habit management screens
│   │   ├── analytics/     # Analytics and insights
│   │   ├── social/        # Social features
│   │   └── settings/      # Settings and profile
│   ├── navigation/         # Navigation configuration
│   ├── services/          # API and business logic
│   │   ├── api/          # API calls
│   │   ├── auth/         # Authentication service
│   │   ├── database/     # Database operations
│   │   ├── notifications/ # Notification handling
│   │   └── analytics/    # Analytics tracking
│   ├── store/             # State management (Zustand)
│   ├── utils/             # Utility functions
│   ├── types/             # TypeScript type definitions
│   ├── constants/         # App constants
│   └── styles/           # Global styles and themes
├── assets/               # Images, fonts, icons
├── config/              # Configuration files
└── __tests__/           # Test files
```

## ⚙️ Configuration Files

### 1. TypeScript Configuration (tsconfig.json)
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "baseUrl": "./src",
    "paths": {
      "@/*": ["*"],
      "@/components/*": ["components/*"],
      "@/screens/*": ["screens/*"],
      "@/services/*": ["services/*"],
      "@/utils/*": ["utils/*"],
      "@/types/*": ["types/*"],
      "@/store/*": ["store/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

### 2. ESLint Configuration (.eslintrc.js)
```javascript
module.exports = {
  extends: [
    'expo',
    '@react-native-community',
    'plugin:@typescript-eslint/recommended',
    'prettier'
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    'react-native/no-unused-styles': 'error',
    'react-native/split-platform-components': 'error',
    'react-native/no-inline-styles': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    'prefer-const': 'error'
  },
  ignorePatterns: ['node_modules/', 'build/', 'dist/']
}
```

### 3. Prettier Configuration (.prettierrc)
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false
}
```

## 🔐 Environment Variables

### 1. Create .env file
```env
# Firebase Configuration
EXPO_PUBLIC_FIREBASE_API_KEY=your_api_key_here
EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
EXPO_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
EXPO_PUBLIC_FIREBASE_APP_ID=your_app_id

# RevenueCat
EXPO_PUBLIC_REVENUECAT_API_KEY=your_revenuecat_key

# Analytics
EXPO_PUBLIC_MIXPANEL_TOKEN=your_mixpanel_token

# Development
EXPO_PUBLIC_APP_ENVIRONMENT=development
```

### 2. Add to .gitignore
```gitignore
# Environment files
.env
.env.local
.env.development
.env.production

# Firebase
google-services.json
GoogleService-Info.plist

# Dependencies
node_modules/

# Build outputs
dist/
build/
.expo/

# OS generated files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

## 🧪 Testing Setup

### 1. Jest Configuration (jest.config.js)
```javascript
module.exports = {
  preset: 'react-native',
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],
  testPathIgnorePatterns: ['/node_modules/', '/android/', '/ios/'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|expo|@expo|@react-navigation)/)'
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/__tests__/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
}
```

### 2. Test Setup File (src/__tests__/setup.ts)
```typescript
import 'react-native-gesture-handler/jestSetup';

jest.mock('react-native-reanimated', () => {
  const Reanimated = require('react-native-reanimated/mock');
  Reanimated.default.call = () => {};
  return Reanimated;
});

jest.mock('react-native/Libraries/Animated/NativeAnimatedHelper');

jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock')
);

jest.mock('expo-notifications', () => ({
  scheduleNotificationAsync: jest.fn(),
  cancelScheduledNotificationAsync: jest.fn(),
  requestPermissionsAsync: jest.fn(() => Promise.resolve({ status: 'granted' })),
}));
```

## 🚀 Development Scripts

### Package.json Scripts
```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "build:android": "eas build --platform android",
    "build:ios": "eas build --platform ios",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/ --ext .ts,.tsx",
    "lint:fix": "eslint src/ --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "clean": "expo r -c",
    "prebuild": "expo prebuild"
  }
}
```

## 📱 Running the Development Environment

### 1. Start the Development Server
```powershell
# Start Expo development server
npm start

# Or start with specific platform
npm run android  # For Android
npm run ios      # For iOS (macOS only)
```

### 2. Install Expo Go App
- **iOS**: Download from App Store
- **Android**: Download from Google Play Store
- Scan QR code from terminal to run on device

### 3. Development Workflow
```powershell
# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint

# Fix linting issues
npm run lint:fix
```

## 🔧 VS Code Setup

### 1. Recommended Extensions
- ES7+ React/Redux/React-Native snippets
- TypeScript Importer
- Prettier - Code formatter
- ESLint
- React Native Tools
- Auto Rename Tag
- Bracket Pair Colorizer
- GitLens

### 2. VS Code Settings (.vscode/settings.json)
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "emmet.includeLanguages": {
    "typescript": "typescriptreact"
  }
}
```

## 🎯 Next Steps After Setup

1. **Verify Installation**: Run `npm start` and test on device/simulator
2. **Set up Firebase**: Configure authentication and Firestore
3. **Create Basic Components**: Start with authentication screens
4. **Set up Navigation**: Implement bottom tab navigation
5. **Create First Habit Screen**: Build the core habit tracking interface

## 🚨 Troubleshooting Common Issues

### Metro bundler issues
```powershell
# Clear cache and restart
npm run clean
npm start -- --reset-cache
```

### Android build issues
```powershell
# Clean Android build
cd android
./gradlew clean
cd ..
npm run android
```

### iOS build issues (macOS)
```bash
# Clean iOS build
cd ios
rm -rf build
pod install
cd ..
npm run ios
```

---

**Ready to code!** 🚀 Your development environment is now configured for building a production-ready React Native habit tracking app.
