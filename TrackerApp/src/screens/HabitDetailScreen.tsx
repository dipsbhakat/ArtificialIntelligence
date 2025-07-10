import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import { RouteProp } from '@react-navigation/native';
import { NavigationParams } from '../types';
import { COLORS } from '../constants';

interface Props {
  route: RouteProp<NavigationParams, 'HabitDetail'>;
}

const HabitDetailScreen: React.FC<Props> = ({ route }) => {
  const { habitId } = route.params;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Habit Details</Text>
        <Text style={styles.subtitle}>Habit ID: {habitId}</Text>
        <Text style={styles.placeholder}>
          This screen will show detailed habit information, progress charts, and completion history.
        </Text>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: COLORS.textSecondary,
    marginBottom: 24,
  },
  placeholder: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
});

export default HabitDetailScreen;
