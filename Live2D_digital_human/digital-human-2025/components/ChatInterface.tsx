'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Trash2 } from 'lucide-react';
import { useDigitalHumanStore } from '@/lib/store';
import { getRealtimeService } from '@/lib/realtime-service';

export default function ChatInterface() {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const messages = useDigitalHumanStore((state) => state.messages);
  const isRecording = useDigitalHumanStore((state) => state.isRecording);
  const isSpeaking = useDigitalHumanStore((state) => state.isSpeaking);
  const isConnected = useDigitalHumanStore((state) => state.isConnected);
  const clearMessages = useDigitalHumanStore((state) => state.clearMessages);

  const realtimeService = getRealtimeService();

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (!inputText.trim() || !isConnected) return;
    
    realtimeService.sendText(inputText);
    setInputText('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      realtimeService.stopRecording();
    } else {
      realtimeService.startRecording();
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface/50 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl overflow-hidden">
      {/* 头部 */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{
              scale: isSpeaking ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 0.5,
              repeat: isSpeaking ? Infinity : 0,
            }}
            className="w-3 h-3 bg-green-500 rounded-full"
          />
          <div>
            <h3 className="font-display font-semibold text-lg">小艾</h3>
            <p className="text-xs text-muted">
              {isConnected ? '在线' : '离线'}
            </p>
          </div>
        </div>
        
        <button
          onClick={clearMessages}
          className="p-2 hover:bg-white/5 rounded-lg transition-colors"
          title="清空对话"
        >
          <Trash2 className="w-4 h-4 text-muted" />
        </button>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        <AnimatePresence mode="popLayout">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: [0.34, 1.56, 0.64, 1] }}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-white/10 text-text'
                }`}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
                <span className="text-xs opacity-60 mt-1 block">
                  {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* AI正在说话指示器 */}
        {isSpeaking && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-1 items-center text-muted"
          >
            <span className="text-sm">小艾正在说话</span>
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.6, repeat: Infinity }}
              className="w-2 h-2 bg-primary rounded-full"
            />
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="px-6 py-4 border-t border-white/10">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isConnected ? "输入消息..." : "请先连接..."}
              disabled={!isConnected}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl
                       text-text placeholder:text-muted
                       focus:outline-none focus:ring-2 focus:ring-primary/50
                       resize-none transition-all disabled:opacity-50"
              rows={1}
            />
          </div>

          {/* 录音按钮 */}
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={toggleRecording}
            disabled={!isConnected}
            className={`p-4 rounded-2xl transition-all disabled:opacity-50 ${
              isRecording
                ? 'bg-red-500 text-white shadow-lg shadow-red-500/50'
                : 'bg-white/10 text-text hover:bg-white/20'
            }`}
          >
            {isRecording ? (
              <MicOff className="w-5 h-5" />
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </motion.button>

          {/* 发送按钮 */}
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            disabled={!isConnected || !inputText.trim()}
            className="p-4 bg-primary text-white rounded-2xl
                     hover:bg-primary-hover transition-all
                     disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>

        {/* 录音提示 */}
        <AnimatePresence>
          {isRecording && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-xs text-muted mt-2 text-center"
            >
              🎤 正在录音... 再次点击停止
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
