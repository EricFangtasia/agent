'use client';

// 模拟 RealtimeClient 类型定义
interface RealtimeClient {
  apiKey?: string;
  dangerouslyAllowAPIKeyInBrowser?: boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  updateSession: (options: any) => Promise<void>;
  on: (event: string, handler: (data: any) => void) => void;
  appendInputAudio: (audio: string) => void;
  createResponse: () => void;
  sendUserMessageContent: (content: any[]) => void;
  cancelResponse: () => void;
}

// 自定义实现
class CustomRealtimeClient implements RealtimeClient {
  apiKey?: string;
  dangerouslyAllowAPIKeyInBrowser?: boolean;
  
  constructor(options?: { apiKey?: string; dangerouslyAllowAPIKeyInBrowser?: boolean }) {
    this.apiKey = options?.apiKey;
    this.dangerouslyAllowAPIKeyInBrowser = options?.dangerouslyAllowAPIKeyInBrowser;
  }
  
  async connect(): Promise<void> {
    // 模拟连接过程
    console.log('Custom Realtime Client connected');
  }
  
  disconnect(): void {
    console.log('Custom Realtime Client disconnected');
  }
  
  async updateSession(options: any): Promise<void> {
    console.log('Session updated:', options);
  }
  
  on(event: string, handler: (data: any) => void): void {
    // 实现事件监听机制
    console.log(`Event listener registered for: ${event}`);
  }
  
  appendInputAudio(audio: string): void {
    console.log('Input audio appended:', audio.substring(0, 20) + '...');
  }
  
  createResponse(): void {
    console.log('Creating response');
  }
  
  sendUserMessageContent(content: any[]): void {
    console.log('Sending user message:', content);
  }
  
  cancelResponse(): void {
    console.log('Response cancelled');
  }
}

import { useDigitalHumanStore, Message } from './store';
import { SimplifiedAIService } from './simplified-ai-service';

export class RealtimeService {
  private client: RealtimeClient | null = null;
  private audioContext: AudioContext | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private recordingStream: MediaStream | null = null;
  private recognition: any = null;
  private simplifiedAIService: SimplifiedAIService;

  constructor() {
    if (typeof window !== 'undefined') {
      this.audioContext = new AudioContext();
      this.simplifiedAIService = SimplifiedAIService.getInstance();
      this.initializeSpeechRecognition();
    }
  }

  /**
   * 初始化语音识别功能
   */
  private initializeSpeechRecognition() {
    // 检查浏览器是否支持 Web Speech API
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'zh-CN'; // 设置为中文识别
      
      this.recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript;
          }
        }
        
        if (transcript) {
          console.log('用户说:', transcript);
          useDigitalHumanStore.getState().addMessage({
            role: 'user',
            content: transcript,
          });
          
          // 通过火山引擎获取AI回复
          this.getVolcEngineResponse(transcript);
        }
      };
      
      this.recognition.onerror = (event: any) => {
        console.error('语音识别错误:', event.error);
      };
    }
  }

  /**
   * 通过简化版AI服务获取AI回复
   */
  private async getSimplifiedAIResponse(userInput: string) {
    try {
      // 获取当前对话历史
      const messages = [...useDigitalHumanStore.getState().messages];
      // 只保留最近的10条消息以避免超出API限制
      const recentMessages = messages.slice(-10);
      
      // 添加用户的新消息
      const allMessages = [...recentMessages, { role: 'user', content: userInput }] as Message[];
      
      // 调用简化版AI服务
      const aiResponse = await this.simplifiedAIService.sendMessage(allMessages);
      
      console.log('AI回复:', aiResponse);
      useDigitalHumanStore.getState().addMessage({
        role: 'assistant',
        content: aiResponse,
      });
      
      // 使用 Web Speech API 播放回复
      this.speak(aiResponse);
    } catch (error) {
      console.error('获取AI回复失败:', error);
      
      // 如果API调用失败，使用模拟回复
      const fallbackResponse = '抱歉，我现在有点忙，稍后再聊吧。';
      useDigitalHumanStore.getState().addMessage({
        role: 'assistant',
        content: fallbackResponse,
      });
      
      this.speak(fallbackResponse);
    }
  }

  /**
   * 使用 Web Speech API 朗读文本
   */
  private speak(text: string) {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      
      utterance.onstart = () => {
        console.log('开始播放语音');
        useDigitalHumanStore.getState().setSpeaking(true);
        useDigitalHumanStore.getState().setMouthOpenness(0.8);
      };
      
      utterance.onend = () => {
        console.log('语音播放结束');
        useDigitalHumanStore.getState().setSpeaking(false);
        useDigitalHumanStore.getState().setMouthOpenness(0);
      };
      
      // 模拟口型同步
      this.simulateLipSync();
      
      speechSynthesis.speak(utterance);
    }
  }

  /**
   * 模拟口型同步
   */
  private simulateLipSync() {
    let frame = 0;
    const totalFrames = 60; // 模拟60帧的动画
    
    const animate = () => {
      if (frame < totalFrames && useDigitalHumanStore.getState().isSpeaking) {
        // 随机动画效果
        const openness = 0.3 + Math.random() * 0.7;
        useDigitalHumanStore.getState().setMouthOpenness(openness);
        
        frame++;
        requestAnimationFrame(animate);
      } else if (frame >= totalFrames) {
        useDigitalHumanStore.getState().setMouthOpenness(0);
      }
    };
    
    animate();
  }

  /**
   * 初始化连接
   */
  async connect(apiKey: string) {
    // 初始化简化版AI服务
    await this.simplifiedAIService.connect(apiKey);

    // 使用自定义实现
    this.client = new CustomRealtimeClient({
      apiKey: apiKey,
      dangerouslyAllowAPIKeyInBrowser: true,
    });

    // 模拟配置会话参数
    await this.client.updateSession({
      instructions: `你是一个友好、活泼的AI助手，名字叫小艾。
      请用简洁、自然的方式回复，就像在和朋友聊天一样。
      回复要简短（1-2句话），不要长篇大论。
      适当使用语气词让对话更生动。`,
      voice: 'alloy',
      input_audio_format: 'pcm16',
      output_audio_format: 'pcm16',
      input_audio_transcription: {
        model: 'whisper-1',
      },
      turn_detection: {
        type: 'server_vad',
        threshold: 0.5,
        prefix_padding_ms: 300,
        silence_duration_ms: 500,
      },
      temperature: 0.8,
      max_response_output_tokens: 4096,
    });

    // 连接
    await this.client.connect();
    
    this.setupEventHandlers();
    useDigitalHumanStore.getState().setConnected(true);
    
    console.log('✅ 简化版 AI 服务已连接');
  }

  /**
   * 设置事件监听器
   */
  private setupEventHandlers() {
    if (!this.client) return;

    // 注册各种事件处理器（模拟）
    (this.client as any).on('conversation.item.input_audio_transcription.completed', (event: any) => {
      console.log('用户说:', event.transcript);
      useDigitalHumanStore.getState().addMessage({
        role: 'user',
        content: event.transcript,
      });
    });

    (this.client as any).on('response.text.delta', (event: any) => {
      console.log('AI回复片段:', event.delta);
    });

    (this.client as any).on('response.text.done', (event: any) => {
      console.log('AI回复完成:', event.text);
      useDigitalHumanStore.getState().addMessage({
        role: 'assistant',
        content: event.text,
      });
    });

    (this.client as any).on('response.audio.delta', (event: any) => {
      this.handleAudioDelta(event.delta);
    });

    (this.client as any).on('response.audio.done', () => {
      console.log('✅ AI语音播放完成');
      useDigitalHumanStore.getState().setSpeaking(false);
      useDigitalHumanStore.getState().setMouthOpenness(0);
    });

    (this.client as any).on('error', (error: any) => {
      console.error('❌ Realtime API错误:', error);
    });
  }

  /**
   * 处理音频数据并进行口型同步
   */
  private async handleAudioDelta(audioData: string) {
    if (!this.audioContext) return;

    useDigitalHumanStore.getState().setSpeaking(true);

    try {
      // 解码base64音频数据
      const binaryString = atob(audioData);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // 转换为AudioBuffer
      const audioBuffer = await this.audioContext.decodeAudioData(bytes.buffer);
      
      // 播放音频
      const source = this.audioContext.createBufferSource();
      source.buffer = audioBuffer;
      
      // 创建分析器用于口型同步
      const analyser = this.audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyser.connect(this.audioContext.destination);
      
      source.start();

      // 实时分析音量控制口型
      this.analyzeAudioForLipSync(analyser);
      
    } catch (error) {
      console.error('音频处理错误:', error);
    }
  }

  /**
   * 分析音频并控制口型
   */
  private analyzeAudioForLipSync(analyser: AnalyserNode) {
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    const analyze = () => {
      analyser.getByteFrequencyData(dataArray);
      
      // 计算平均音量
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      const normalizedVolume = Math.min(average / 128, 1);
      
      // 更新嘴巴开合度
      useDigitalHumanStore.getState().setMouthOpenness(normalizedVolume);
      
      // 如果还在播放，继续分析
      if (useDigitalHumanStore.getState().isSpeaking) {
        requestAnimationFrame(analyze);
      }
    };
    
    analyze();
  }

  /**
   * 开始录音
   */
  async startRecording() {
    try {
      // 如果浏览器支持语音识别，直接启动
      if (this.recognition) {
        this.recognition.start();
        useDigitalHumanStore.getState().setRecording(true);
        console.log('🎤 开始录音（使用Web Speech API）');
      } else {
        // 否则使用传统录音方式
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          } 
        });
        
        this.recordingStream = stream;
        this.mediaRecorder = new MediaRecorder(stream, {
          mimeType: 'audio/webm',
        });

        this.mediaRecorder.ondataavailable = async (event) => {
          if (event.data.size > 0 && this.client) {
            // 将音频发送到模拟API
            const arrayBuffer = await event.data.arrayBuffer();
            const base64 = this.arrayBufferToBase64(arrayBuffer);
            
            (this.client as any).appendInputAudio(base64);
          }
        };

        // 每100ms发送一次音频数据
        this.mediaRecorder.start(100);
        useDigitalHumanStore.getState().setRecording(true);
        
        console.log('🎤 开始录音（使用MediaRecorder）');
      }
    } catch (error) {
      console.error('无法访问麦克风:', error);
    }
  }

  /**
   * 停止录音
   */
  stopRecording() {
    if (this.recognition) {
      this.recognition.stop();
      useDigitalHumanStore.getState().setRecording(false);
      console.log('🛑 停止录音（使用Web Speech API）');
    } else if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
      this.recordingStream?.getTracks().forEach(track => track.stop());
      useDigitalHumanStore.getState().setRecording(false);
      
      // 提交音频，触发AI响应
      (this.client as any)?.createResponse();
      
      console.log('🛑 停止录音（使用MediaRecorder）');
    }
  }

  /**
   * 发送文本消息
   */
  async sendText(text: string) {
    if (!this.simplifiedAIService.isConnectedToService()) {
      console.error('简化版AI服务未初始化');
      return;
    }

    useDigitalHumanStore.getState().addMessage({
      role: 'user',
      content: text,
    });

    // 通过简化版AI服务获取AI回复
    this.getSimplifiedAIResponse(text);
  }

  /**
   * 打断AI说话
   */
  interrupt() {
    if (this.client) {
      (this.client as any).cancelResponse();
      useDigitalHumanStore.getState().setSpeaking(false);
      useDigitalHumanStore.getState().setMouthOpenness(0);
      
      // 如果有正在进行的语音合成，停止它
      if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
      }
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.stopRecording();
    this.client?.disconnect();
    this.simplifiedAIService.disconnect();
    this.audioContext?.close();
    useDigitalHumanStore.getState().setConnected(false);
    console.log('👋 已断开连接');
  }

  /**
   * 工具函数：ArrayBuffer转Base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
}

// 单例实例
let realtimeServiceInstance: RealtimeService | null = null;

export function getRealtimeService(): RealtimeService {
  if (!realtimeServiceInstance) {
    realtimeServiceInstance = new RealtimeService();
  }
  return realtimeServiceInstance;
}