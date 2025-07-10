import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { Provider } from 'react-redux';
import { store } from './src/store';
import AppNavigator from './src/navigation/AppNavigator';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './src/services/firebase';
import { useAppDispatch } from './src/hooks/redux';
import { loginSuccess, logout } from './src/store/slices/authSlice';
import { AuthService } from './src/services/auth';

// Auth listener component
const AuthListener: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const user = await AuthService.getCurrentUser();
          if (user) {
            dispatch(loginSuccess(user));
          }
        } catch (error) {
          console.error('Error getting user profile:', error);
          dispatch(logout());
        }
      } else {
        dispatch(logout());
      }
    });

    return unsubscribe;
  }, [dispatch]);

  return <>{children}</>;
};

export default function App() {
  return (
    <Provider store={store}>
      <AuthListener>
        <StatusBar style="auto" />
        <AppNavigator />
      </AuthListener>
    </Provider>
  );
}
