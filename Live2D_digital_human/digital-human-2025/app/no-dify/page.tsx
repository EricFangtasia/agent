'use client';

import { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import Head from 'next/head';
import { useDigitalHumanStore, Message } from '@/lib/store';

// 动态导入Live2D组件，禁用SSR
const Live2DCharacter = dynamic(() => import('@/components/Live2DCharacter'), {
  ssr: false,
  loading: () => <div className="w-full h-full flex items-center justify-center bg-gray-900">
    <div className="text-white text-lg">正在加载数字人...</div>
  </div>
});

// 定义接口
interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export default function DigitalHumanNoDify() {
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');
  
  const { 
    messages, 
    isRecording, 
    isSpeaking, 
    isConnected, 
    addMessage, 
    setConnected,
    clearMessages 
  } = useDigitalHumanStore();
  
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // 初始化API密钥
  useEffect(() => {
    const savedKey = localStorage.getItem('volcengine-api-key');
    if (savedKey) {
      setApiKey(savedKey);
    }
  }, []);

  // 保存API密钥到本地存储
  const saveApiKey = (key: string) => {
    localStorage.setItem('volcengine-api-key', key);
  };

  // 模拟连接API
  const connectToApi = async () => {
    if (!apiKey) {
      setError('请输入API密钥');
      return;
    }

    setIsLoading(true);
    setError(null);
    setConnectionStatus('connecting');

    try {
      // 模拟API连接过程
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // 这里应该实际连接到你的AI服务
      // 目前使用模拟连接
      saveApiKey(apiKey);
      setConnected(true);
      setConnectionStatus('connected');
      
      // 添加欢迎消息
      addMessage({
        role: 'assistant',
        content: '你好！我是你的数字人助手，现在已经连接成功了。你可以和我聊天或提问问题。',
      });
    } catch (err) {
      setError('连接失败，请检查API密钥是否正确');
      setConnectionStatus('disconnected');
    } finally {
      setIsLoading(false);
    }
  };

  // 模拟断开连接
  const disconnectFromApi = () => {
    setConnected(false);
    setConnectionStatus('disconnected');
    clearMessages();
  };

  // 模拟发送文本消息
  const handleSendText = async () => {
    if (!inputText.trim()) return;
    
    if (!isConnected) {
      setError('请先连接到服务');
      return;
    }

    // 添加用户消息
    addMessage({
      role: 'user',
      content: inputText,
    });

    // 清空输入框
    setInputText('');

    try {
      // 模拟调用AI服务
      setIsLoading(true);
      
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟AI回复 - 实际应用中应调用真实API
      const simulatedResponse = getSimulatedResponse(inputText);
      
      addMessage({
        role: 'assistant',
        content: simulatedResponse,
      });
    } catch (err) {
      setError('发送消息失败，请重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 模拟开始录音
  const handleStartRecording = async () => {
    if (!isConnected) {
      setError('请先连接到服务');
      return;
    }

    try {
      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());

      // 模拟录音开始
      addMessage({
        role: 'user',
        content: '（语音消息）你好，你能听到我说话吗？',
      });

      // 模拟AI回复
      setTimeout(() => {
        addMessage({
          role: 'assistant',
          content: '我能清楚地听到您的声音，有什么我可以帮您的吗？',
        });
      }, 1500);
    } catch (err) {
      setError('无法访问麦克风，请检查权限设置');
    }
  };

  // 获取模拟响应
  const getSimulatedResponse = (input: string): string => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('你好') || lowerInput.includes('您好')) {
      return '你好！很高兴见到你，今天过得怎么样？';
    } else if (lowerInput.includes('名字') || lowerInput.includes('叫什么')) {
      return '我是你的数字助手小艾，随时为您服务！';
    } else if (lowerInput.includes('天气')) {
      return '我目前无法获取实时天气信息，建议您查看天气应用。';
    } else if (lowerInput.includes('帮助')) {
      return '我可以陪您聊天、解答问题，或者只是倾听您的想法。有什么想和我分享的吗？';
    } else {
      const responses = [
        '这是个有趣的问题，我认为...',
        '我理解您的意思，我的看法是...',
        '根据我的知识，我可以告诉您...',
        '这个问题让我思考了一下，我觉得...',
        '很高兴您问这个问题，让我来解释...',
        '我明白您的关注点，实际情况是...'
      ];
      return responses[Math.floor(Math.random() * responses.length)] + '（这是一个模拟回复，实际应用中应由AI服务提供）';
    }
  };

  // 处理按键事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  return (
    <>
      <Head>
        <title>实时互动数字人 - 无Dify版</title>
        <meta name="description" content="基于AI的实时互动数字人系统，无需Dify和Docker" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white p-4">
        <div className="max-w-6xl mx-auto">
          {/* 顶部导航 */}
          <header className="flex justify-between items-center py-4 mb-6 border-b border-gray-700">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-500 to-cyan-400 bg-clip-text text-transparent">
              实时互动数字人 - 无Dify版
            </h1>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm ${
                connectionStatus === 'connected' 
                  ? 'bg-green-500/20 text-green-400' 
                  : connectionStatus === 'connecting'
                  ? 'bg-yellow-500/20 text-yellow-400'
                  : 'bg-red-500/20 text-red-400'
              }`}>
                {connectionStatus === 'connected' ? '已连接' : 
                 connectionStatus === 'connecting' ? '连接中...' : '未连接'}
              </div>
              {isConnected && (
                <button
                  onClick={disconnectFromApi}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
                >
                  断开连接
                </button>
              )}
            </div>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左侧：连接设置和聊天界面 */}
            <div className="lg:col-span-1 space-y-6">
              {/* 连接设置 */}
              {!isConnected && (
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
                  <h2 className="text-xl font-semibold mb-4 text-cyan-300">连接设置</h2>
                  
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="apiKey" className="block text-sm font-medium mb-2">
                        API密钥
                      </label>
                      <input
                        type="password"
                        id="apiKey"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="输入您的API密钥"
                        className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                      />
                      <p className="mt-2 text-sm text-gray-400">
                        支持火山引擎、阿里云百炼等平台的API密钥
                      </p>
                    </div>
                    
                    {error && (
                      <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
                        {error}
                      </div>
                    )}
                    
                    <button
                      onClick={connectToApi}
                      disabled={isLoading || !apiKey}
                      className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                        isLoading || !apiKey
                          ? 'bg-gray-700 cursor-not-allowed'
                          : 'bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700'
                      }`}
                    >
                      {isLoading ? '连接中...' : '连接服务'}
                    </button>
                  </div>
                </div>
              )}

              {/* 聊天界面 */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 h-[500px] flex flex-col">
                <div className="p-4 border-b border-gray-700">
                  <h2 className="text-lg font-semibold">对话</h2>
                </div>
                
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                          message.role === 'user'
                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none'
                            : 'bg-gray-700 text-gray-100 rounded-tl-none'
                        }`}
                      >
                        {message.content}
                      </div>
                    </div>
                  ))}
                  
                  {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500">
                      <p className="mb-4">还没有对话记录</p>
                      <p className="text-sm">连接服务后开始聊天</p>
                    </div>
                  )}
                </div>
                
                <div className="p-4 border-t border-gray-700">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="输入消息..."
                      disabled={!isConnected}
                      className="flex-1 px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50"
                    />
                    <button
                      onClick={handleSendText}
                      disabled={!isConnected || !inputText.trim() || isLoading}
                      className={`px-4 py-2 rounded-lg font-medium ${
                        !isConnected || !inputText.trim() || isLoading
                          ? 'bg-gray-700 cursor-not-allowed'
                          : 'bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700'
                      }`}
                    >
                      发送
                    </button>
                  </div>
                  
                  <div className="mt-3 flex justify-center">
                    <button
                      onClick={handleStartRecording}
                      disabled={!isConnected || isLoading}
                      className={`flex items-center px-4 py-2 rounded-lg font-medium ${
                        !isConnected || isLoading
                          ? 'bg-gray-700 cursor-not-allowed'
                          : isRecording
                          ? 'bg-red-600 hover:bg-red-700'
                          : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700'
                      }`}
                    >
                      <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        className="h-5 w-5 mr-2" 
                        viewBox="0 0 20 20" 
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                          clipRule="evenodd"
                        />
                      </svg>
                      {isRecording ? '录音中...' : '语音输入'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* 右侧：数字人展示 */}
            <div className="lg:col-span-2">
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 h-[calc(100vh-150px)] min-h-[500px] overflow-hidden">
                <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                  <h2 className="text-lg font-semibold">数字人形象</h2>
                  <div className="flex items-center space-x-4">
                    {isSpeaking && (
                      <div className="flex items-center text-green-400">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                        AI正在说话
                      </div>
                    )}
                    {isRecording && (
                      <div className="flex items-center text-red-400">
                        <div className="w-2 h-2 bg-red-400 rounded-full mr-2 animate-pulse"></div>
                        录音中...
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="w-full h-[calc(100%-60px)]">
                  <Live2DCharacter />
                </div>
              </div>
            </div>
          </div>

          {/* 底部信息 */}
          <footer className="mt-8 text-center text-gray-500 text-sm">
            <p>实时互动数字人系统 · 无需Dify和Docker · 基于Next.js 15 + Live2D</p>
          </footer>
        </div>
      </div>
    </>
  );
}