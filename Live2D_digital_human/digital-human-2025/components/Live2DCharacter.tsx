'use client';

import { useEffect, useRef, useState } from 'react';
import * as PIXI from 'pixi.js';
import { Application, Container, Graphics } from 'pixi.js';
import { useDigitalHumanStore } from '@/lib/store';
import { motion, AnimatePresence } from 'framer-motion';

export default function Live2DCharacter() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const appRef = useRef<Application | null>(null);
  const modelRef = useRef<any>(null);
  const [initStatus, setInitStatus] = useState<'loading-core' | 'initializing-pixi' | 'loading-model' | 'ready' | 'error'>('loading-core');
  const [cubismReady, setCubismReady] = useState(false);
  
  const mouthOpenness = useDigitalHumanStore((state) => state.mouthOpenness);
  const currentEmotion = useDigitalHumanStore((state) => state.currentEmotion);

  // 添加点击处理状态
  const [lastClickTime, setLastClickTime] = useState(0);
  
  // 1. 核心运行时检查 (Cubism Core已在layout.tsx的<head>中同步加载)
  useEffect(() => {
    let isMounted = true;
  
    const checkRuntimes = async () => {
      if (typeof window === 'undefined') return;
        
      try {
        console.log('📦 正在检查 Live2D 运行时...');
          
        // 等待Cubism Core加载完成（最多等待3秒）
        let attempts = 0;
        const maxAttempts = 30;
          
        while (attempts < maxAttempts) {
          const global = window as any;
            
          // 检查Cubism Core是否已加载
          if (global.Live2DCubismCore) {
            console.log('✅ 检测到 Cubism Core');
              
            // 统一变量名
            global.LIVE2DCUBISMCORE = global.Live2DCubismCore;
            global.Live2D = global.Live2DCubismCore;
              
            // 挂载 PIXI
            global.PIXI = PIXI;
              
            console.log('✅ 运行时就绪', {
              hasCubismCore: !!global.Live2DCubismCore,
              hasLIVE2DCUBISMCORE: !!global.LIVE2DCUBISMCORE,
              hasLive2D: !!global.Live2D,
              hasPIXI: !!global.PIXI
            });
              
            if (isMounted) setCubismReady(true);
            return;
          }
            
          // 等待100ms后重试
          await new Promise(resolve => setTimeout(resolve, 100));
          attempts++;
        }
          
        throw new Error('Cubism Core 加载超时，请检查 /libs/live2dcubismcore.min.js 是否存在');
      } catch (err) {
        console.error('❌ 运行时检查失败:', err);
        setInitStatus('error');
      }
    };
  
    checkRuntimes();
    return () => { isMounted = false; };
  }, []);

  // 2. 初始化 PixiJS
  useEffect(() => {
    if (cubismReady && canvasRef.current && !appRef.current) {
      setInitStatus('initializing-pixi');
      initPixiApp();
    }
    
    return () => {
      if (appRef.current) {
        appRef.current.destroy(true, { children: true, texture: true });
        appRef.current = null;
        modelRef.current = null;
      }
    };
  }, [cubismReady]);

  const initPixiApp = async () => {
    if (!canvasRef.current) return;
    try {
      // PIXI v7 API: 使用构造函数而不是 init()
      const app = new Application({
        view: canvasRef.current,
        width: 800,
        height: 600,
        backgroundAlpha: 0,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
      });
      
      appRef.current = app;
      setInitStatus('loading-model');
      await loadLive2DModel(app);
    } catch (error) {
      console.error('❌ PixiJS 初始化失败:', error);
      setInitStatus('error');
    }
  };

  // 等待Cubism Core加载完成(最多等待3秒)
  const waitForCubismCore = async () => {
    const maxAttempts = 30;
    for (let i = 0; i < maxAttempts; i++) {
      if ((window as any).Live2DCubismCore) {
        console.log('✅ Cubism Core 已加载');
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    console.error('❌ Cubism Core 加载超时');
    return false;
  };

  // 3. 加载模型 (在原有基础上增加点击事件)
  const loadLive2DModel = async (app: Application) => {
    try {
      const global = window as any;
      
      // 验证Cubism Core已加载(最多等待3秒)
      const isCoreReady = await waitForCubismCore();
      if (!isCoreReady) {
        throw new Error('Cubism Core 运行时加载失败');
      }
      
      // 确保PIXI可用
      global.PIXI = PIXI;
      
      console.log('🔧 准备导入 pixi-live2d-display...', {
        hasCubismCore: !!global.Live2DCubismCore,
        hasLive2DMotion: !!global.Live2DMotion,
      });
      
      // 导入pixi-live2d-display
      const module = await import('pixi-live2d-display');
      const Live2DModel = module.Live2DModel;
      
      console.log('✅ 模块导入成功');

      // 加载模型
      const modelPath = '/haru_greeter_pro_jp/runtime/haru_greeter_t05.model3.json';
      console.log('🎨 开始加载模型:', modelPath);
      
      const model = await Live2DModel.from(modelPath);

      if (model) {
        // 布局调整
        model.anchor.set(0.5, 0.5);
        const scale = (app.screen.height * 0.8) / model.height;
        model.scale.set(scale);
        model.position.set(app.screen.width / 2, app.screen.height / 2);

        modelRef.current = model;
        app.stage.addChild(model);

        console.log('✨ 互动数字人已上线！');
        setInitStatus('ready');
        
        // === 新增：启动Idle动画 ===
        try {
          // 使用正确的motion方法启动Idle动作
          model.motion('Idle', 0, module.MotionPriority.IDLE);
        } catch (e) {
          console.warn('无法启动Idle动作:', e);
        }
        
        // === 新增：添加点击事件处理器 ===
        const handleModelClick = () => {
          const now = Date.now();
          // 防抖：避免连续快速点击(1秒内只响应一次)
          if (now - lastClickTime < 1000) return;
          setLastClickTime(now);
          
          try {
            // 随机选择TapBody动作组中的一个动作
            const tapMotions = model.internalModel?.motionManager.definitions['TapBody'];
            if (tapMotions && tapMotions.length > 0) {
              const randomIndex = Math.floor(Math.random() * tapMotions.length);
              // 使用motion方法播放TapBody动作
              model.motion('TapBody', randomIndex, module.MotionPriority.NORMAL);
            }
          } catch (e) {
            console.warn('播放TapBody动作失败:', e);
          }
        };
        
        // 为模型添加点击事件监听器
        model.on('click', handleModelClick);
        // 兼容touch事件
        model.on('tap', handleModelClick);
        
        // 清理函数中移除事件监听器
        return () => {
          model.off('click', handleModelClick);
          model.off('tap', handleModelClick);
          // 销毁模型（如果库提供了销毁方法）
          if (typeof model.destroy === 'function') {
            model.destroy();
          }
        };
      } else {
        throw new Error('模型加载失败');
      }
    } catch (error) {
        console.error('❌ 加载失败:', error);
        createPlaceholder(app);
        setInitStatus('ready');
    }
  };

  // 4. 口型与表情逻辑
  useEffect(() => {
    if (modelRef.current?.internalModel?.coreModel) {
      // 使用兼容的方式更新参数
      const coreModel = modelRef.current.internalModel.coreModel;
      if (coreModel && typeof coreModel.setParameterValueById === 'function') {
        coreModel.setParameterValueById('ParamMouthOpenY', mouthOpenness);
      }
    } else if (modelRef.current?.isPlaceholder) {
      updatePlaceholderMouth(mouthOpenness);
    }
  }, [mouthOpenness]);

  useEffect(() => {
    if (modelRef.current?.expression && typeof modelRef.current.expression === 'function') {
      modelRef.current.expression(currentEmotion);
    }
  }, [currentEmotion]);

  const updatePlaceholderMouth = (openness: number) => {
    const mouth = modelRef.current?.mouth as any;
    if (!mouth || mouth.destroyed) return;
    
    try {
      mouth.clear();
      if (openness > 0.1) {
        // PIXI v7 API
        mouth.beginFill(0x1F2937);
        mouth.drawEllipse(0, 0, 30, 5 + openness * 25);
        mouth.endFill();
      } else {
        mouth.lineStyle(3, 0x1F2937);
        mouth.moveTo(-30, 0);
        mouth.lineTo(30, 0);
      }
    } catch (e) {
      console.error('更新占位符嘴部动画时出错:', e);
    }
  };

  const createPlaceholder = (app: Application) => {
    try {
      const container = new PIXI.Container();
      container.position.set(app.screen.width / 2, app.screen.height / 2);
      
      const head = new PIXI.Graphics();
      head.beginFill(0x6366F1);
      head.drawCircle(0, 0, 100);
      head.endFill();
      
      const mouth = new PIXI.Graphics();
      mouth.y = 40;
      mouth.lineStyle(3, 0x1F2937);
      mouth.moveTo(-30, 0);
      mouth.lineTo(30, 0);
      
      container.addChild(head, mouth);
      app.stage.addChild(container);
      modelRef.current = { mouth, isPlaceholder: true };
    } catch (e) {
      console.error('创建占位符时出错:', e);
    }
  };

  const getStatusText = () => {
    switch (initStatus) {
      case 'loading-core': return '加载 Cubism 引擎...';
      case 'initializing-pixi': return '初始化渲染器...';
      case 'loading-model': return '唤醒数字人...';
      case 'error': return '启动失败，请检查资源';
      default: return '';
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative w-full h-full flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full touch-none" style={{ background: 'transparent' }} />
      <AnimatePresence>
        {initStatus !== 'ready' && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className={`absolute px-6 py-3 rounded-xl backdrop-blur-md border flex items-center gap-3 ${initStatus === 'error' ? 'bg-red-500/20 border-red-500/50' : 'bg-indigo-900/40 border-indigo-500/30'}`}
          >
            {initStatus !== 'error' && <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />}
            <span className="text-white text-sm font-medium">{getStatusText()}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}