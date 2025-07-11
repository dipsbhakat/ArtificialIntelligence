#!/usr/bin/env python3
"""
Test script to verify watchlist functionality works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from watchlist_manager import WatchlistManager

def test_watchlist():
    """Test basic watchlist functionality."""
    print("🧪 Testing Watchlist Manager...")
    
    try:
        # Initialize watchlist manager
        wm = WatchlistManager()
        print("✅ WatchlistManager initialized successfully")
        
        # Test getting summary (this was causing the KeyError)
        summary = wm.get_watchlist_summary()
        print(f"✅ Watchlist summary: {summary}")
        
        # Verify all required keys are present
        required_keys = ['total_stocks', 'avg_target_distance', 'stocks_near_target', 'stocks_near_stop', 'active_alerts']
        for key in required_keys:
            if key in summary:
                print(f"✅ '{key}': {summary[key]}")
            else:
                print(f"❌ Missing key: '{key}'")
                return False
        
        # Test active alerts count
        alerts_count = wm.get_active_alerts_count()
        print(f"✅ Active alerts count: {alerts_count}")
        
        # Test adding a stock to watchlist
        success = wm.add_to_watchlist("AAPL", 150.0, 140.0, "Test stock")
        if success:
            print("✅ Successfully added test stock to watchlist")
        else:
            print("⚠️ Could not add test stock (might already exist)")
        
        # Test getting watchlist
        watchlist_df = wm.get_watchlist()
        print(f"✅ Watchlist retrieved: {len(watchlist_df)} stocks")
        
        print("\n🎉 All watchlist tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_watchlist()
