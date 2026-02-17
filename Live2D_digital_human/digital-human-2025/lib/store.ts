import { create } from 'zustand';

export type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  audioUrl?: string;
};

export type EmotionType = 'neutral' | 'happy' | 'surprised' | 'thinking' | 'talking';

type DigitalHumanState = {
  // 连接状态
  isConnected: boolean;
  isRecording: boolean;
  isSpeaking: boolean;
  
  // 对话历史
  messages: Message[];
  
  // 数字人状态
  currentEmotion: EmotionType;
  mouthOpenness: number;
  
  // Actions
  setConnected: (connected: boolean) => void;
  setRecording: (recording: boolean) => void;
  setSpeaking: (speaking: boolean) => void;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setEmotion: (emotion: EmotionType) => void;
  setMouthOpenness: (openness: number) => void;
  clearMessages: () => void;
};

export const useDigitalHumanStore = create<DigitalHumanState>((set) => ({
  // 初始状态
  isConnected: false,
  isRecording: false,
  isSpeaking: false,
  messages: [],
  currentEmotion: 'neutral',
  mouthOpenness: 0,
  
  // Actions
  setConnected: (connected) => set({ isConnected: connected }),
  setRecording: (recording) => set({ isRecording: recording }),
  setSpeaking: (speaking) => set({ isSpeaking: speaking }),
  
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: crypto.randomUUID(),
          timestamp: Date.now(),
        },
      ],
    })),
  
  setEmotion: (emotion) => set({ currentEmotion: emotion }),
  setMouthOpenness: (openness) => set({ mouthOpenness: openness }),
  clearMessages: () => set({ messages: [] }),
}));
