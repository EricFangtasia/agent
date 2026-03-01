import { LAppDelegate } from '@/lib/live2d/src/lappdelegate';
import { ResourceModel } from '@/lib/protocol';

export class Live2dManager {
    // 单例
    public static getInstance(): Live2dManager {
        if (! this._instance) {
            this._instance = new Live2dManager();
        }

        return this._instance;
    }

    public setReady(ready: boolean) {
      this._ready = ready;
    }

    public isReady(): boolean {
      return this._ready;
    }

    public changeCharacter(character: ResourceModel | null) {
      // _subdelegates中只有一个画布, 所以设置第一个即可
      this._ready = false;
      LAppDelegate.getInstance().changeCharacter(character)
    }

    public setLipFactor(weight: number): void {
      this._lipFactor = weight;
    }

    public getLipFactor(): number {
      return this._lipFactor;
    }

    public pushAudioQueue(audioData: ArrayBuffer): void {
      this._ttsQueue.push(audioData);
    }
    
    /**
     * 触发情绪动作
     * @param emotion 情绪类型：'happy', 'sad', 'angry', 'surprised' 等
     */
    public triggerEmotionMotion(emotion: string): void {
      const delegate = LAppDelegate.getInstance();
      const subdelegates = delegate.getSubdelegate();
      
      if (!subdelegates || subdelegates.getSize() === 0) return;
      
      const live2dManager = subdelegates.at(0).getLive2DManager();
      const model = live2dManager.getCurrentModel();
      if (!model) return;
      
      const modelSetting = (model as any)._modelSetting;
      if (!modelSetting) return;
      
      console.log(`[Live2D] Triggering emotion motion: ${emotion}`);
      
      // 根据情绪选择动作组
      let motionGroups: string[] = [];
      let shouldJump = false;  // 是否需要真实跳跃动画
      
      switch(emotion.toLowerCase()) {
        case 'happy':
        case 'joy':
        case 'excited':
          // 开心时的动作：跳跃、欢呼等
          motionGroups = ['jump', 'Jump', 'happy', 'Happy', 'cheer', 'Cheer', 'celebrate', 'Celebrate'];
          shouldJump = true;  // 开心时触发跳跃
          break;
        case 'sad':
          motionGroups = ['sad', 'Sad', 'cry', 'Cry'];
          break;
        case 'angry':
          motionGroups = ['angry', 'Angry', 'shake', 'Shake'];
          break;
        case 'surprised':
          motionGroups = ['surprised', 'Surprised', 'shock', 'Shock'];
          break;
        default:
          motionGroups = [];
      }
      
      // 尝试播放指定的情绪动作
      for (const group of motionGroups) {
        const motionCount = modelSetting.getMotionCount(group);
        if (motionCount && motionCount > 0) {
          const motionNo = Math.floor(Math.random() * motionCount);
          model.startMotion(group, motionNo, 3); // 优先级3：高优先级
          console.log(`[Live2D] Playing emotion motion: ${group}_${motionNo}`);
          
          // 如果是开心情绪，添加真实的跳跃动画
          if (shouldJump) {
            this.playJumpAnimation(model);
          }
          return;
        }
      }
      
      // 如果没有找到对应情绪动作，播放任意活跃动作
      const fallbackGroups = ['TapBody', 'tap_body', 'Pinch', 'pinch', 'Shake', 'shake'];
      for (const group of fallbackGroups) {
        const motionCount = modelSetting.getMotionCount(group);
        if (motionCount && motionCount > 0) {
          const motionNo = Math.floor(Math.random() * motionCount);
          model.startMotion(group, motionNo, 3);
          console.log(`[Live2D] Using fallback motion for emotion: ${group}_${motionNo}`);
          
          // 如果是开心情绪，即使用回退动作也添加跳跃
          if (shouldJump) {
            this.playJumpAnimation(model);
          }
          return;
        }
      }
      
      console.log(`[Live2D] No suitable motion found for emotion: ${emotion}`);
    }

    /**
     * 播放跳跃动画（Y轴位移）
     * @param model 要跳跃的模型
     */
    private playJumpAnimation(model: any): void {
      const modelMatrix = (model as any)._modelMatrix;
      if (!modelMatrix) return;

      console.log('[Live2D] Playing jump animation with Y-axis translation');

      // 保存原始Y位置
      const originalY = modelMatrix.getTranslateY();
      
      // 跳跃参数
      const jumpHeight = 0.3;      // 跳跃高度（屏幕空间，0.3约为屏幕的15%）
      const jumpDuration = 600;    // 跳跃总时长（毫秒）
      const startTime = Date.now();

      // 使用requestAnimationFrame实现平滑的跳跃动画
      const animateJump = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / jumpDuration, 1.0);

        if (progress < 1.0) {
          // 使用抛物线函数模拟真实跳跃
          // y = -4h * (t - 0.5)^2 + h，在t=0.5时达到最高点h
          const t = progress;
          const currentY = originalY + jumpHeight * (-4 * Math.pow(t - 0.5, 2) + 1);
          
          // 更新模型Y坐标
          modelMatrix.translateY(currentY);
          
          // 继续动画
          requestAnimationFrame(animateJump);
        } else {
          // 动画结束，恢复原始位置
          modelMatrix.translateY(originalY);
          console.log('[Live2D] Jump animation completed');
        }
      };

      // 开始动画
      animateJump();
    }

    public popAudioQueue(): ArrayBuffer | null {
      if (this._ttsQueue.length > 0) {
        const audioData = this._ttsQueue.shift();
        return audioData;
      } else {
        return null;
      }
    }

    public clearAudioQueue(): void {
      this._ttsQueue = [];
    }

    public async playAudio(): Promise<ArrayBuffer | null> {
      // 检查并恢复 AudioContext 状态（解决浏览器自动播放策略问题）
      if (this._audioContext.state === 'suspended') {
        console.log('[Live2D] AudioContext is suspended, attempting to resume...');
        try {
          await this._audioContext.resume();
          console.log('[Live2D] AudioContext resumed successfully');
        } catch (e) {
          console.error('[Live2D] Failed to resume AudioContext:', e);
          return null;
        }
      }
      
      if (this._audioIsPlaying) return null; // 如果正在播放则返回
      const audioData = this.popAudioQueue();
      if (audioData == null) return null; // 没有音频数据则返回
      this._audioIsPlaying = true;
      
      // 开始说话时触发说话动作（如果模型有的话）
      this.startTalkingMotion();
      
      // 播放音频
      const playAudioBuffer = (buffer: AudioBuffer) => {
        console.log('[Live2D] Playing audio buffer, creating analyser...');
        var source = this._audioContext.createBufferSource();
        source.buffer = buffer;
        
        // 创建音频分析器用于口型同步
        const analyser = this._audioContext.createAnalyser();
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        console.log(`[Live2D] Analyser created - FFT size: ${analyser.fftSize}, Buffer length: ${bufferLength}`);
        
        // 连接音频节点：source -> analyser -> destination
        source.connect(analyser);
        analyser.connect(this._audioContext.destination);
        console.log('[Live2D] Audio nodes connected: source -> analyser -> destination');
        
        // 开始口型同步分析
        this.startLipSyncAnalysis(analyser, dataArray);
        
        // 监听音频播放完毕事件
        source.onended = () => {
          console.log('[Live2D] Audio ended, stopping lip sync');
          this._audioIsPlaying = false;
          // 停止口型同步
          this.stopLipSyncAnalysis();
          // 说话结束，停止说话动作
          this.stopTalkingMotion();
          
          // 关键修复：自动播放队列中的下一段音频
          console.log('[Live2D] Checking for next audio in queue...');
          setTimeout(() => {
            const nextAudio = this.playAudio();
            if (nextAudio) {
              console.log('[Live2D] Playing next audio from queue');
            } else {
              console.log('[Live2D] No more audio in queue');
            }
          }, 50); // 短暂延迟，确保状态更新完成
        };
        source.start();
        console.log('[Live2D] Audio source started');
        this._audioSource = source;
      }
      // 创建一个新的 ArrayBuffer 并复制数据, 防止原始数据被decodeAudioData释放
      const newAudioData = audioData.slice(0);
      this._audioContext.decodeAudioData(newAudioData).then(
        buffer => {
          playAudioBuffer(buffer);
        }
      );
      return audioData;
    }

    public stopAudio(): void {
      this.clearAudioQueue();
      if (this._audioSource) {
        this._audioSource.stop();
        this._audioSource = null;
      }
      this._audioIsPlaying = false;
    }

    public isAudioPlaying(): boolean {
      return this._audioIsPlaying;
    }

    /**
     * 开始说话动作
     * 尝试播放 'talk' 或 'speak' 组的动作，如果没有则使用任意可用动作
     */
    private startTalkingMotion(): void {
      const delegate = LAppDelegate.getInstance();
      const subdelegates = delegate.getSubdelegate();
      
      if (!subdelegates || subdelegates.getSize() === 0) return;
      
      const live2dManager = subdelegates.at(0).getLive2DManager();
      const model = live2dManager.getCurrentModel();
      if (!model) return;
      
      const modelSetting = (model as any)._modelSetting;
      if (!modelSetting) return;
      
      // 优先尝试播放说话动作组
      const talkGroups = ['talk', 'speak', 'speaking', 'Talk', 'Speak'];
      
      for (const group of talkGroups) {
        const motionCount = modelSetting.getMotionCount(group);
        if (motionCount && motionCount > 0) {
          const motionNo = Math.floor(Math.random() * motionCount);
          model.startMotion(group, motionNo, 2);
          console.log(`[Live2D] Started talking motion: ${group}_${motionNo}`);
          return;
        }
      }
      
      // 如果没有专门的说话动作，尝试使用其他动作组
      const fallbackGroups = ['TapBody', 'tap_body', 'Pinch', 'pinch', 'Shake', 'shake'];
      
      for (const group of fallbackGroups) {
        const motionCount = modelSetting.getMotionCount(group);
        if (motionCount && motionCount > 0) {
          const motionNo = Math.floor(Math.random() * motionCount);
          model.startMotion(group, motionNo, 2);
          console.log(`[Live2D] Using fallback motion for talking: ${group}_${motionNo}`);
          return;
        }
      }
      
      // 最后尝试：获取所有可用的动作组，随机播放一个
      try {
        const motionGroupCount = modelSetting.getMotionGroupCount();
        if (motionGroupCount > 0) {
          // 排除idle组（避免播放待机动作）
          const availableGroups = [];
          for (let i = 0; i < motionGroupCount; i++) {
            const groupName = modelSetting.getMotionGroupName(i);
            if (groupName.toLowerCase() !== 'idle') {
              availableGroups.push(groupName);
            }
          }
          
          if (availableGroups.length > 0) {
            const randomGroup = availableGroups[Math.floor(Math.random() * availableGroups.length)];
            const motionCount = modelSetting.getMotionCount(randomGroup);
            if (motionCount > 0) {
              const motionNo = Math.floor(Math.random() * motionCount);
              model.startMotion(randomGroup, motionNo, 2);
              console.log(`[Live2D] Using random motion for talking: ${randomGroup}_${motionNo}`);
              return;
            }
          }
        }
      } catch (e) {
        console.error('[Live2D] Error trying to get motion groups:', e);
      }
      
      console.log('[Live2D] No suitable motion found for talking');
    }

    /**
     * 停止说话动作
     * 说话结束后会自动切换回待机动作
     */
    private stopTalkingMotion(): void {
      // 不需要做任何事，Live2D会自动切换回待机动作
      console.log('[Live2D] Talking motion finished, returning to idle');
    }

    /**
     * 开始口型同步分析
     */
    private startLipSyncAnalysis(analyser: AnalyserNode, dataArray: Uint8Array): void {
      console.log('[Live2D] Starting lip sync analysis...');
      let animationFrameId: number;
      let frameCount = 0;
      
      const updateLipSync = () => {
        analyser.getByteFrequencyData(dataArray);
        
        // 计算平均音量（0-255）
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const average = sum / dataArray.length;
        
        // 将音量归一化到 0-1 范围，并应用lip factor
        const normalizedVolume = (average / 255) * this.getLipFactor();
        
        // 每30帧打印一次调试信息
        if (frameCount % 30 === 0) {
          console.log(`[Live2D] Lip sync - Volume: ${average.toFixed(2)}, Normalized: ${normalizedVolume.toFixed(3)}`);
        }
        frameCount++;
        
        // 更新模型的嘴部参数
        const delegate = LAppDelegate.getInstance();
        const subdelegates = delegate.getSubdelegate();
        
        if (subdelegates && subdelegates.getSize() > 0) {
          const live2dManager = subdelegates.at(0).getLive2DManager();
          const model = live2dManager.getCurrentModel();
          if (model && (model as any)._model) {
            // 更新嘴部开合参数
            const lipSyncIds = (model as any)._lipSyncIds;
            if (lipSyncIds && lipSyncIds.getSize() > 0) {
              if (frameCount === 1) {
                console.log(`[Live2D] Found ${lipSyncIds.getSize()} lip sync parameters`);
                for (let i = 0; i < lipSyncIds.getSize(); i++) {
                  const paramId = lipSyncIds.at(i);
                  console.log(`[Live2D] Lip sync param ${i}:`, paramId);
                }
              }
              
              // 直接使用CubismModel的方法设置参数
              const cubismModel = (model as any)._model;
              for (let i = 0; i < lipSyncIds.getSize(); i++) {
                const paramId = lipSyncIds.at(i);
                // 获取参数索引
                const paramIndex = cubismModel.getParameterIndex(paramId);
                if (paramIndex >= 0) {
                  // 关键修复：使用setParameterValueByIndex直接设置，而不是add
                  // 这样可以覆盖motion的值
                  cubismModel.setParameterValueByIndex(paramIndex, normalizedVolume);
                } else {
                  if (frameCount === 1) {
                    console.warn(`[Live2D] Parameter index not found for param ${i}`);
                  }
                }
              }
            } else {
              if (frameCount === 1) {
                console.warn('[Live2D] No lip sync IDs found!');
              }
            }
          } else {
            if (frameCount === 1) {
              console.warn('[Live2D] No model or _model found!');
            }
          }
        } else {
          if (frameCount === 1) {
            console.warn('[Live2D] No subdelegates found!');
          }
        }
        
        // 继续下一帧
        animationFrameId = requestAnimationFrame(updateLipSync);
      };
      
      // 保存动画帧ID以便停止
      this._lipSyncAnimationId = animationFrameId;
      
      // 开始分析
      updateLipSync();
    }

    /**
     * 停止口型同步分析
     */
    private stopLipSyncAnalysis(): void {
      if (this._lipSyncAnimationId !== null) {
        cancelAnimationFrame(this._lipSyncAnimationId);
        this._lipSyncAnimationId = null;
      }
      
      // 重置嘴部参数
      const delegate = LAppDelegate.getInstance();
      const subdelegates = delegate.getSubdelegate();
      
      if (subdelegates && subdelegates.getSize() > 0) {
        const live2dManager = subdelegates.at(0).getLive2DManager();
        const model = live2dManager.getCurrentModel();
        if (model && (model as any)._model) {
          const lipSyncIds = (model as any)._lipSyncIds;
          const cubismModel = (model as any)._model;
          if (lipSyncIds && lipSyncIds.getSize() > 0) {
            for (let i = 0; i < lipSyncIds.getSize(); i++) {
              const paramId = lipSyncIds.at(i);
              const paramIndex = cubismModel.getParameterIndex(paramId);
              if (paramIndex >= 0) {
                // 使用setParameterValueByIndex重置参数
                cubismModel.setParameterValueByIndex(paramIndex, 0);
              }
            }
          }
        }
      }
    }

    constructor() {
      this._audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this._audioIsPlaying = false;
      this._audioSource = null;
      this._lipFactor = 1.0;
      this._ready = false;
      this._lipSyncAnimationId = null;
      
      // 添加用户交互监听器，在第一次点击时恢复AudioContext
      this._setupAudioContextResume();
      
      // 监听表情和动作事件
      this._setupLive2DEventListeners();
    }
    
    /**
     * 设置Live2D事件监听器（表情、动作）
     */
    private _setupLive2DEventListeners(): void {
      // 监听表情变化事件
      window.addEventListener('live2d:expression', ((event: CustomEvent) => {
        const { expression } = event.detail;
        console.log(`[Live2D] Expression event: ${expression}`);
        
        const delegate = LAppDelegate.getInstance();
        const subdelegates = delegate.getSubdelegate();
        if (!subdelegates || subdelegates.getSize() === 0) return;
        
        const live2dManager = subdelegates.at(0).getLive2DManager();
        const model = live2dManager.getCurrentModel();
        if (model) {
          try {
            model.setExpression(expression);
          } catch (e) {
            // 如果指定表情不存在，使用随机表情
            model.setRandomExpression();
          }
        }
      }) as EventListener);
      
      // 监听动作触发事件
      window.addEventListener('live2d:emotion', ((event: CustomEvent) => {
        const { emotion } = event.detail;
        console.log(`[Live2D] Emotion event: ${emotion}`);
        this.triggerEmotionMotion(emotion);
      }) as EventListener);
      
      // 监听随机动作事件
      window.addEventListener('live2d:action', (() => {
        console.log('[Live2D] Action event triggered');
        this.triggerRandomAction();
      }) as EventListener);
    }
    
    /**
     * 触发随机动作
     */
    public triggerRandomAction(): void {
      const delegate = LAppDelegate.getInstance();
      const subdelegates = delegate.getSubdelegate();
      if (!subdelegates || subdelegates.getSize() === 0) return;
      
      const live2dManager = subdelegates.at(0).getLive2DManager();
      live2dManager.playRandomAction();
    }
    
    /**
     * 设置AudioContext恢复机制
     * 浏览器安全策略要求AudioContext必须在用户手势后才能启动
     */
    private _setupAudioContextResume(): void {
      const resumeAudio = async () => {
        if (this._audioContext.state === 'suspended') {
          console.log('[Live2D] User interaction detected, resuming AudioContext...');
          try {
            await this._audioContext.resume();
            console.log('[Live2D] AudioContext resumed after user interaction');
          } catch (e) {
            console.error('[Live2D] Failed to resume AudioContext:', e);
          }
        }
      };
      
      // 监听多种用户交互事件
      ['click', 'touchstart', 'keydown'].forEach(event => {
        document.addEventListener(event, resumeAudio, { once: true, passive: true });
      });
    }

    private static _instance: Live2dManager;
    private _ttsQueue: ArrayBuffer[] = [];
    private _audioContext: AudioContext;
    private _audioIsPlaying: boolean;
    private _audioSource: AudioBufferSourceNode | null;
    private _lipFactor: number;
    private _ready: boolean;
    private _lipSyncAnimationId: number | null;
  }