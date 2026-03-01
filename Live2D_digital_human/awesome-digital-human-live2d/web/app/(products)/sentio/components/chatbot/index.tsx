'use client'

import { useEffect, memo, useRef, useState } from "react";
import { CHAT_MODE, APP_TYPE, IFER_TYPE } from "@/lib/protocol";
import { ChatRecord } from "./record";
import { ChatInput, ChatVadInput, ChatStreamInput } from "./input";
import { NewsDisplay } from "../news";
import { QuotesDisplay } from "../news/quotes";
import { 
    useSentioChatModeStore, 
    useSentioThemeStore,
    useSentioAsrStore
} from "@/lib/store/sentio";

/**
 * =====================================================
 * 数字人应用 - 三大业务模块架构
 * =====================================================
 * 
 * 【新闻模式 NEWS】
 *   - 从数据库获取新闻展示播放
 *   - 穿插播放新闻话术 + 互动话术
 *   - 文件: components/news/index.tsx
 * 
 * 【名言模式 QUOTES】
 *   - 播报名人名言
 *   - 穿插互动话术
 *   - 文件: components/news/quotes.tsx
 * 
 * 【聊天模式 DIALOGUE/IMMSERSIVE】
 *   - 聊天对话交互
 *   - 不播放互动话术
 *   - 点击数字人时播放互动话术（仅 IMMSERSIVE 模式）
 *   - 文件: components/chatbot/record.tsx + input.tsx
 * 
 * =====================================================
 */

function FreedomChatBot() {
    // 直接使用 zustand store，与 Header 完全一致
    const chatMode = useSentioChatModeStore((state) => state.chatMode);
    const { infer_type } = useSentioAsrStore();
    
    console.log('[ChatBot] 渲染模式:', chatMode);
    
    // 预合成音频缓存（仅用于聊天模式的触摸互动）
    const audioCacheRef = useRef<Map<string, ArrayBuffer>>(new Map());
    
    // 预合成触摸反馈语音（仅聊天模式使用）
    useEffect(() => {
        // 只在聊天模式下预加载
        if (chatMode === CHAT_MODE.NEWS || chatMode === CHAT_MODE.QUOTES) {
            return;
        }
        
        const preloadTouchVoices = async () => {
            console.log('[ChatBot] 预加载触摸互动语音...');
            
            const reactions = [
                "讨厌~", "不要这样子嘛", "好舒服啊", "哥哥我错了",
                "哈哈哈", "干嘛啦", "你在干什么", "不要碰我",
                "好痒啊", "嘿嘿~", "人家会害羞的啦", "讨厌，别摸了"
            ];
            
            try {
                const { api_tts_infer } = await import('@/lib/api/server');
                const { useSentioTtsStore } = await import('@/lib/store/sentio');
                const { base64ToArrayBuffer } = await import('@/lib/func');
                const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
                
                const store = useSentioTtsStore.getState();
                const ttsEngine = store.engine || 'default';
                const ttsConfig = store.settings || {};
                
                const promises = reactions.map(async (text) => {
                    try {
                        const controller = new AbortController();
                        const audioBase64 = await api_tts_infer(ttsEngine, ttsConfig, text, controller.signal);
                        if (audioBase64) {
                            const audioData = base64ToArrayBuffer(audioBase64);
                            const wavBuffer = await convertMp3ArrayBufferToWavArrayBuffer(audioData);
                            audioCacheRef.current.set(text, wavBuffer);
                        }
                    } catch (error) {
                        console.error(`[ChatBot] 预加载失败: ${text}`, error);
                    }
                });
                
                await Promise.all(promises);
                console.log(`[ChatBot] 预加载完成，共 ${audioCacheRef.current.size} 条`);
            } catch (error) {
                console.error('[ChatBot] 预加载触摸语音失败:', error);
            }
        };
        
        preloadTouchVoices();
    }, [chatMode]);
    
    // Live2D触摸事件 - 仅聊天模式(交互模式)触发互动话术
    useEffect(() => {
        const handleLive2dTouch = async (event: Event) => {
            // 仅在聊天-交互模式下触发互动话术
            if (chatMode !== CHAT_MODE.IMMSERSIVE) {
                console.log('[ChatBot] 非聊天交互模式，跳过触摸互动，当前模式:', chatMode);
                return;
            }
            
            const customEvent = event as CustomEvent;
            const { text } = customEvent.detail;
            console.log('[ChatBot] 触摸互动:', text);
            
            // 从缓存获取或实时合成
            const cachedAudio = audioCacheRef.current.get(text);
            
            try {
                const { Live2dManager } = await import('@/lib/live2d/live2dManager');
                const manager = Live2dManager.getInstance();
                
                if (cachedAudio) {
                    manager.clearAudioQueue();
                    manager.pushAudioQueue(cachedAudio);
                    manager.playAudio();
                } else {
                    // 实时合成
                    const { api_tts_infer } = await import('@/lib/api/server');
                    const { useSentioTtsStore } = await import('@/lib/store/sentio');
                    const { base64ToArrayBuffer } = await import('@/lib/func');
                    const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
                    
                    const store = useSentioTtsStore.getState();
                    const controller = new AbortController();
                    const audioBase64 = await api_tts_infer(store.engine || 'default', store.settings || {}, text, controller.signal);
                    
                    if (audioBase64) {
                        const wavBuffer = await convertMp3ArrayBufferToWavArrayBuffer(base64ToArrayBuffer(audioBase64));
                        manager.clearAudioQueue();
                        manager.pushAudioQueue(wavBuffer);
                        manager.playAudio();
                    }
                }
            } catch (error) {
                console.error('[ChatBot] 播放触摸语音失败:', error);
            }
        };
        
        document.addEventListener('live2d:touch', handleLive2dTouch);
        return () => document.removeEventListener('live2d:touch', handleLive2dTouch);
    }, [chatMode]);
    
    // TTS播报函数（传递给新闻/名言组件使用）
    const speakText = async (text: string) => {
        try {
            const { api_tts_infer } = await import('@/lib/api/server');
            const { useSentioTtsStore } = await import('@/lib/store/sentio');
            const { Live2dManager } = await import('@/lib/live2d/live2dManager');
            const { base64ToArrayBuffer } = await import('@/lib/func');
            const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
            
            const store = useSentioTtsStore.getState();
            const controller = new AbortController();
            const audioBase64 = await api_tts_infer(store.engine || 'default', store.settings || {}, text, controller.signal);
            
            if (audioBase64) {
                const wavBuffer = await convertMp3ArrayBufferToWavArrayBuffer(base64ToArrayBuffer(audioBase64));
                const manager = Live2dManager.getInstance();
                manager.pushAudioQueue(wavBuffer);
                manager.playAudio();
            }
        } catch (error) {
            console.error('[ChatBot] TTS播报失败:', error);
        }
    };
    
    // ================== 三大模块路由 ==================
    return (
        <div className="flex flex-col full-height-minus-64px pb-6 md:px-6 gap-6 justify-between items-center z-10">
            {/* 模块1: 新闻模式 */}
            {chatMode === CHAT_MODE.NEWS && (
                <NewsDisplay onSpeak={speakText} />
            )}
            
            {/* 模块2: 名言模式 */}
            {chatMode === CHAT_MODE.QUOTES && (
                <QuotesDisplay onSpeak={speakText} />
            )}
            
            {/* 模块3: 聊天模式 */}
            {(chatMode === CHAT_MODE.DIALOGUE || chatMode === CHAT_MODE.IMMSERSIVE) && (
                <>
                    <ChatRecord />
                    {chatMode === CHAT_MODE.IMMSERSIVE 
                        ? (infer_type === IFER_TYPE.NORMAL ? <ChatVadInput/> : <ChatStreamInput />) 
                        : <ChatInput />
                    }
                </>
            )}
        </div>
    )
}

function ChatBot() {
    const { theme } = useSentioThemeStore();
    switch (theme) {
        case APP_TYPE.FREEDOM:
            return <FreedomChatBot />
        default:
            return <FreedomChatBot />
    }
}

export default memo(ChatBot);