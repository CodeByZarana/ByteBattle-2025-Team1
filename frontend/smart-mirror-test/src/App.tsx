import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// Enhanced types for full widget system
interface Gesture {
  name: string;
  confidence: number;
  type: 'static' | 'swipe';
  timestamp: number;
  frame_count: number;
}

interface WidgetState {
  current: string;
  menu_open: boolean;
}

interface GestureData {
  type: string;
  gesture: Gesture;
  widget_state: WidgetState;
  action_result?: string;
}

interface Widget {
  id: string;
  name: string;
  icon: string;
  summary: React.ReactNode;
  menu: MenuItem[];
  isExpanded: boolean;
  selectedIndex: number;
}

interface MenuItem {
  id: string;
  name: string;
  icon: string;
  action: string;
}

// Widget definitions with real structure
const WIDGET_DATA: Record<string, Widget> = {
  time: {
    id: 'time',
    name: 'Time & Alarms',
    icon: '🕐',
    summary: (
      <div>
        <div className="main-time">{new Date().toLocaleTimeString()}</div>
        <div className="time-details">
          <div>⏰ Next alarm: 7:00 AM</div>
          <div>🌍 Toronto, Canada</div>
        </div>
      </div>
    ),
    menu: [
      { id: 'set-alarm', name: 'Set New Alarm', icon: '⏰', action: 'set_alarm' },
      { id: 'world-clocks', name: 'World Clocks', icon: '🌍', action: 'world_clocks' },
      { id: 'timer', name: 'Start Timer', icon: '⏱️', action: 'timer' },
      { id: 'stopwatch', name: 'Stopwatch', icon: '⏲️', action: 'stopwatch' }
    ],
    isExpanded: false,
    selectedIndex: 0
  },
  weather: {
    id: 'weather',
    name: 'Weather',
    icon: '🌤️',
    summary: (
      <div>
        <div className="weather-main">22°C Sunny</div>
        <div className="weather-details">
          <div>🌡️ Feels like 25°C</div>
          <div>💨 Wind: 5 mph</div>
          <div>🌧️ Rain: 10% chance</div>
        </div>
      </div>
    ),
    menu: [
      { id: 'current', name: 'Current Conditions', icon: '🌡️', action: 'current_weather' },
      { id: 'hourly', name: 'Hourly Forecast', icon: '📊', action: 'hourly_forecast' },
      { id: 'weekly', name: '7-Day Forecast', icon: '📅', action: 'weekly_forecast' },
      { id: 'alerts', name: 'Weather Alerts', icon: '⚠️', action: 'weather_alerts' }
    ],
    isExpanded: false,
    selectedIndex: 0
  },
  news: {
    id: 'news',
    name: 'News',
    icon: '📰',
    summary: (
      <div>
        <div className="news-main">Latest Headlines</div>
        <div className="news-items">
          <div>📈 Tech stocks continue rising</div>
          <div>🌦️ Weather system approaching</div>
          <div>🎉 Local events this weekend</div>
        </div>
      </div>
    ),
    menu: [
      { id: 'headlines', name: 'Top Headlines', icon: '📰', action: 'top_news' },
      { id: 'tech', name: 'Technology', icon: '💻', action: 'tech_news' },
      { id: 'local', name: 'Local News', icon: '🏠', action: 'local_news' },
      { id: 'sports', name: 'Sports', icon: '⚽', action: 'sports_news' }
    ],
    isExpanded: false,
    selectedIndex: 0
  },
  calendar: {
    id: 'calendar',
    name: 'Calendar',
    icon: '📅',
    summary: (
      <div>
        <div className="calendar-main">Today's Schedule</div>
        <div className="calendar-items">
          <div>• 9:00 AM - Team Meeting</div>
          <div>• 12:00 PM - Lunch</div>
          <div>• 2:00 PM - Project Review</div>
        </div>
      </div>
    ),
    menu: [
      { id: 'today', name: "Today's Schedule", icon: '📋', action: 'today_schedule' },
      { id: 'upcoming', name: 'Upcoming Events', icon: '📅', action: 'upcoming_events' },
      { id: 'add-event', name: 'Add New Event', icon: '➕', action: 'add_event' },
      { id: 'join-meeting', name: 'Join Next Meeting', icon: '📹', action: 'join_meeting' }
    ],
    isExpanded: false,
    selectedIndex: 0
  }
};

function App() {
  // State management
  const [gestureData, setGestureData] = useState<GestureData | null>(null);
  const [connected, setConnected] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());
  const [widgets, setWidgets] = useState(WIDGET_DATA);
  const [currentWidgetId, setCurrentWidgetId] = useState('time');
  const [lastAction, setLastAction] = useState<string | null>(null);
  
  // Current widget reference
  const currentWidget = widgets[currentWidgetId];
  const widgetOrder = ['time', 'weather', 'news', 'calendar'];

  // Update time every second
  useEffect(() => {
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timeInterval);
  }, []);

  // Handle gesture actions
  const handleGestureAction = useCallback((gesture: Gesture) => {
    const gestureName = gesture.name;
    
    setWidgets(prevWidgets => {
      const newWidgets = { ...prevWidgets };
      const current = newWidgets[currentWidgetId];
      
      if (current.isExpanded) {
        // In menu mode
        switch (gestureName) {
          case 'SWIPE_UP':
            current.selectedIndex = Math.max(0, current.selectedIndex - 1);
            setLastAction(`Selected: ${current.menu[current.selectedIndex].name}`);
            break;
          case 'SWIPE_DOWN':
            current.selectedIndex = Math.min(current.menu.length - 1, current.selectedIndex + 1);
            setLastAction(`Selected: ${current.menu[current.selectedIndex].name}`);
            break;
          case 'FIST':
            const selectedItem = current.menu[current.selectedIndex];
            setLastAction(`Activated: ${selectedItem.name}`);
            // Here you'd trigger the actual action
            break;
          case 'PEACE':
            current.isExpanded = false;
            current.selectedIndex = 0;
            setLastAction('Menu closed');
            break;
        }
      } else {
        // In navigation mode
        switch (gestureName) {
          case 'SWIPE_RIGHT':
            const nextIndex = (widgetOrder.indexOf(currentWidgetId) + 1) % widgetOrder.length;
            setCurrentWidgetId(widgetOrder[nextIndex]);
            setLastAction(`Switched to ${WIDGET_DATA[widgetOrder[nextIndex]].name}`);
            break;
          case 'SWIPE_LEFT':
            const prevIndex = (widgetOrder.indexOf(currentWidgetId) - 1 + widgetOrder.length) % widgetOrder.length;
            setCurrentWidgetId(widgetOrder[prevIndex]);
            setLastAction(`Switched to ${WIDGET_DATA[widgetOrder[prevIndex]].name}`);
            break;
          case 'FIST':
            current.isExpanded = true;
            setLastAction(`Opened ${current.name} menu`);
            break;
          case 'THUMBS_UP':
            setLastAction(`Liked ${current.name}`);
            break;
          case 'POINTING':
            setLastAction(`Info for ${current.name}`);
            break;
        }
      }
      
      return newWidgets;
    });
  }, [currentWidgetId, widgetOrder]);

  // WebSocket connection for real gesture data
  useEffect(() => {
    console.log('🔌 Connecting to real gesture stream...');
    const ws = new WebSocket('ws://localhost:8000/ws/gestures');
    
    ws.onopen = () => {
      console.log('✅ Connected to real gesture recognition!');
      setConnected(true);
    };
    
    ws.onclose = () => {
      console.log('🔌 Disconnected from gesture stream');
      setConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setConnected(false);
    };
    
    ws.onmessage = (event) => {
      try {
        const data: GestureData = JSON.parse(event.data);
        console.log('📥 Real gesture received:', data.gesture.name);
        setGestureData(data);
        
        // Handle the gesture action
        if (data.gesture.name !== 'OPEN_HAND') {  // Ignore open hand
          handleGestureAction(data.gesture);
        }
      } catch (error) {
        console.error('❌ Failed to parse gesture data:', error);
      }
    };

    return () => {
      console.log('🔌 Cleaning up gesture connection');
      ws.close();
    };
  }, [handleGestureAction]);

  // Clear last action after 3 seconds
  useEffect(() => {
    if (lastAction) {
      const timer = setTimeout(() => setLastAction(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [lastAction]);

  const getGestureEmoji = (gestureName: string) => {
    const emojiMap: { [key: string]: string } = {
      'FIST': '👊',
      'SWIPE_LEFT': '👈',
      'SWIPE_RIGHT': '👉',
      'SWIPE_UP': '👆',
      'SWIPE_DOWN': '👇',
      'PEACE': '✌️',
      'THUMBS_UP': '👍',
      'POINTING': '☝️',
      'OPEN_HAND': '🖐️'
    };
    return emojiMap[gestureName] || '🤚';
  };

  return (
    <div className="mirror-container">
      {/* Header */}
      <header className="mirror-header">
        <div className="time-display">{currentTime}</div>
        <div className="header-status">
          <div className="connection-indicator">
            <div className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></div>
            {connected ? 'Live Gestures' : 'Connecting...'}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mirror-content">
        {/* Widget Navigation */}
        <div className="widget-nav">
          {widgetOrder.map(widgetId => (
            <div 
              key={widgetId}
              className={`widget-nav-item ${widgetId === currentWidgetId ? 'active' : ''}`}
            >
              <span className="widget-icon">{widgets[widgetId].icon}</span>
              <span className="widget-name">{widgets[widgetId].name}</span>
            </div>
          ))}
        </div>

        {/* Current Widget Display */}
        <div className="widget-container">
          <div className="widget-header">
            <h1 className="widget-title">
              {currentWidget.icon} {currentWidget.name}
            </h1>
            <div className="widget-mode">
              {currentWidget.isExpanded ? 'Menu Mode' : 'View Mode'}
            </div>
          </div>

          <div className="widget-content">
            {currentWidget.isExpanded ? (
              /* Menu Mode */
              <div className="widget-menu">
                <div className="menu-title">Select an action:</div>
                <div className="menu-items">
                  {currentWidget.menu.map((item, index) => (
                    <div 
                      key={item.id}
                      className={`menu-item ${index === currentWidget.selectedIndex ? 'selected' : ''}`}
                    >
                      <span className="menu-icon">{item.icon}</span>
                      <span className="menu-name">{item.name}</span>
                      {index === currentWidget.selectedIndex && <span className="selection-arrow">👈</span>}
                    </div>
                  ))}
                </div>
                <div className="menu-instructions">
                  👆👇 Navigate • 👊 Select • ✌️ Back
                </div>
              </div>
            ) : (
              /* Summary Mode */
              <div className="widget-summary">
                {currentWidget.summary}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mirror-footer">
        {/* Gesture Feedback */}
        <div className="gesture-feedback">
          {gestureData && gestureData.gesture.name !== 'OPEN_HAND' ? (
            <div className="current-gesture">
              <span className="gesture-emoji">{getGestureEmoji(gestureData.gesture.name)}</span>
              <span className="gesture-name">{gestureData.gesture.name}</span>
              <span className="gesture-confidence">
                {(gestureData.gesture.confidence * 100).toFixed(0)}%
              </span>
            </div>
          ) : (
            <div className="ready-state">👋 Ready for gestures</div>
          )}
        </div>

        {/* Action Feedback */}
        {lastAction && (
          <div className="action-feedback">
            ✅ {lastAction}
          </div>
        )}

        {/* Instructions */}
        <div className="instructions">
          {currentWidget.isExpanded ? (
            'Menu: 👆👇 Navigate • 👊 Select • ✌️ Close'
          ) : (
            'Navigation: 👈👉 Switch • 👊 Menu • 👍 Like'
          )}
        </div>
      </footer>
    </div>
  );
}

export default App;