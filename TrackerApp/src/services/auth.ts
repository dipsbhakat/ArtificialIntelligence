import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  updateProfile,
  User as FirebaseUser,
  AuthError,
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from './firebase';
import { User } from '../types';

export class AuthService {
  static async signIn(email: string, password: string): Promise<User> {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return await this.createUserProfile(userCredential.user);
    } catch (error) {
      throw this.handleAuthError(error as AuthError);
    }
  }

  static async signUp(email: string, password: string, displayName?: string): Promise<User> {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      if (displayName) {
        await updateProfile(userCredential.user, { displayName });
      }
      
      return await this.createUserProfile(userCredential.user, true);
    } catch (error) {
      throw this.handleAuthError(error as AuthError);
    }
  }

  static async signOut(): Promise<void> {
    try {
      await signOut(auth);
    } catch (error) {
      throw this.handleAuthError(error as AuthError);
    }
  }

  static async getCurrentUser(): Promise<User | null> {
    const firebaseUser = auth.currentUser;
    if (!firebaseUser) return null;
    
    return await this.createUserProfile(firebaseUser);
  }

  private static async createUserProfile(firebaseUser: FirebaseUser, isNewUser = false): Promise<User> {
    const userRef = doc(db, 'users', firebaseUser.uid);
    
    if (isNewUser) {
      const newUser: User = {
        id: firebaseUser.uid,
        email: firebaseUser.email!,
        displayName: firebaseUser.displayName || undefined,
        photoURL: firebaseUser.photoURL || undefined,
        createdAt: new Date(),
        updatedAt: new Date(),
        isPremium: false,
      };
      
      await setDoc(userRef, {
        ...newUser,
        createdAt: newUser.createdAt.toISOString(),
        updatedAt: newUser.updatedAt.toISOString(),
      });
      
      return newUser;
    } else {
      const userDoc = await getDoc(userRef);
      if (userDoc.exists()) {
        const userData = userDoc.data();
        return {
          id: firebaseUser.uid,
          email: firebaseUser.email!,
          displayName: firebaseUser.displayName || undefined,
          photoURL: firebaseUser.photoURL || undefined,
          createdAt: new Date(userData.createdAt),
          updatedAt: new Date(userData.updatedAt),
          isPremium: userData.isPremium || false,
          subscriptionExpiresAt: userData.subscriptionExpiresAt 
            ? new Date(userData.subscriptionExpiresAt) 
            : undefined,
        };
      } else {
        // User document doesn't exist, create it
        return await this.createUserProfile(firebaseUser, true);
      }
    }
  }

  private static handleAuthError(error: AuthError): Error {
    switch (error.code) {
      case 'auth/user-not-found':
        return new Error('No user found with this email address.');
      case 'auth/wrong-password':
        return new Error('Incorrect password.');
      case 'auth/email-already-in-use':
        return new Error('An account with this email already exists.');
      case 'auth/weak-password':
        return new Error('Password should be at least 6 characters.');
      case 'auth/invalid-email':
        return new Error('Invalid email address.');
      case 'auth/too-many-requests':
        return new Error('Too many failed attempts. Please try again later.');
      default:
        return new Error(error.message || 'An authentication error occurred.');
    }
  }
}
