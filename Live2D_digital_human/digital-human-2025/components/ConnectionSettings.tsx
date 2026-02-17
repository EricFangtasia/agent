'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Zap, XCircle } from 'lucide-react';
import { useDigitalHumanStore } from '@/lib/store';
import { getRealtimeService } from '@/lib/realtime-service';

export default function ConnectionSettings() {
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState('');
  
  const isConnected = useDigitalHumanStore((state) => state.isConnected);

  const handleConnect = async () => {
    if (!apiKey.trim()) {
      setError('请输入OpenAI API密钥');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      const service = getRealtimeService();
      await service.connect(apiKey);
      setShowSettings(false);
      
      // 保存到localStorage（仅用于开发测试）
      if (typeof window !== 'undefined') {
        localStorage.setItem('openai_api_key', apiKey);
      }
    } catch (err: any) {
      setError(err.message || '连接失败，请检查API密钥');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    const service = getRealtimeService();
    service.disconnect();
  };

  // 自动加载保存的API密钥
  useState(() => {
    if (typeof window !== 'undefined') {
      const savedKey = localStorage.getItem('openai_api_key');
      if (savedKey) {
        setApiKey(savedKey);
      }
    }
  });

  return (
    <>
      {/* 设置按钮 */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setShowSettings(!showSettings)}
        className="fixed top-6 right-6 p-4 bg-surface/80 backdrop-blur-xl 
                   rounded-2xl shadow-lg border border-white/10
                   hover:bg-surface transition-all z-50"
      >
        <Settings className="w-6 h-6 text-text" />
      </motion.button>

      {/* 设置面板 */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowSettings(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-surface rounded-3xl shadow-2xl max-w-md w-full p-8 border border-white/10"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-display font-bold">连接设置</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              {!isConnected ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      OpenAI API密钥
                    </label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-..."
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl
                               focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                    <p className="text-xs text-muted mt-2">
                      获取API密钥: <a href="https://platform.openai.com/api-keys" 
                        target="_blank" 
                        className="text-primary hover:underline">
                        platform.openai.com
                      </a>
                    </p>
                  </div>

                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-sm"
                    >
                      {error}
                    </motion.div>
                  )}

                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    onClick={handleConnect}
                    disabled={isConnecting}
                    className="w-full py-4 bg-primary text-white rounded-xl font-medium
                             hover:bg-primary-hover transition-all
                             disabled:opacity-50 disabled:cursor-not-allowed
                             flex items-center justify-center gap-2"
                  >
                    {isConnecting ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        连接中...
                      </>
                    ) : (
                      <>
                        <Zap className="w-5 h-5" />
                        连接
                      </>
                    )}
                  </motion.button>

                  <div className="pt-4 border-t border-white/10">
                    <p className="text-xs text-muted">
                      💡 提示: 这个演示在浏览器中使用API密钥。生产环境应使用服务端中继以保护密钥安全。
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                    <div className="flex items-center gap-2 text-green-500">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span className="font-medium">已连接</span>
                    </div>
                    <p className="text-sm text-muted mt-1">
                      Realtime API连接正常
                    </p>
                  </div>

                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    onClick={handleDisconnect}
                    className="w-full py-4 bg-red-500/10 text-red-500 rounded-xl font-medium
                             hover:bg-red-500/20 transition-all
                             flex items-center justify-center gap-2"
                  >
                    <XCircle className="w-5 h-5" />
                    断开连接
                  </motion.button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}