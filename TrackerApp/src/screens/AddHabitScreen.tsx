import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import { COLORS } from '../constants';

const AddHabitScreen: React.FC = () => {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Add New Habit</Text>
        <Text style={styles.placeholder}>
          This screen will contain a form to create new habits with:
          {'\n'}- Habit name and description
          {'\n'}- Category selection
          {'\n'}- Frequency settings
          {'\n'}- Reminder settings
          {'\n'}- Color and icon picker
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
    marginBottom: 24,
  },
  placeholder: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
});

export default AddHabitScreen;
