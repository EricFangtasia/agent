'use client'

import { useEffect, memo, useRef, useState } from "react";
import { CHAT_MODE, APP_TYPE, IFER_TYPE } from "@/lib/protocol";
import { ChatRecord } from "./record";
import { ChatInput, ChatVadInput, ChatStreamInput } from "./input";
import { 
    useSentioChatModeStore, 
    useSentioThemeStore,
    useSentioAsrStore
} from "@/lib/store/sentio";

function FreedomChatBot() {
    const { chatMode } = useSentioChatModeStore();
    const { infer_type } = useSentioAsrStore();
    
    // 预合成音频缓存
    const audioCacheRef = useRef<Map<string, ArrayBuffer>>(new Map());
    const [isPreloading, setIsPreloading] = useState(true);
    
    // 预合成常用触摸反馈语音
    useEffect(() => {
        const preloadTouchVoices = async () => {
            console.log('[ChatBot] Preloading touch voice audios...');
            
            const reactions = [
                "讨厌~",
                "不要这样子嘛",
                "好舒服啊",
                "哥哥我错了",
                "哈哈哈",
                "干嘛啦",
                "你在干什么",
                "不要碰我",
                "好痒啊",
                "嘿嘿~",
                "人家会害羞的啦",
                "讨厌，别摸了",
                "嗯~好舒服",
                "主人真坏",
                "再这样我要生气了哦",
                "呀~轻一点",
                "好痒好痒",
                "你想干嘛呀",
                "人家不给你摸",
                "哼~坏蛋",
                "诶嘿嘿~",
                "主人好色",
                "别闹了啦",
                "讨厌死了",
                "你好坏哦"
            ];
            
            try {
                const { api_tts_infer } = await import('@/lib/api/server');
                const { useSentioTtsStore } = await import('@/lib/store/sentio');
                const { base64ToArrayBuffer } = await import('@/lib/func');
                const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
                
                const store = useSentioTtsStore.getState();
                const ttsEngine = store.engine || 'default';
                const ttsConfig = store.settings || {};
                
                // 并行预合成所有语音
                const promises = reactions.map(async (text) => {
                    try {
                        const controller = new AbortController();
                        const audioBase64 = await api_tts_infer(ttsEngine, ttsConfig, text, controller.signal);
                        
                        if (audioBase64) {
                            const audioData = base64ToArrayBuffer(audioBase64);
                            const wavBuffer = await convertMp3ArrayBufferToWavArrayBuffer(audioData);
                            audioCacheRef.current.set(text, wavBuffer);
                            console.log(`[ChatBot] Preloaded: ${text}`);
                        }
                    } catch (error) {
                        console.error(`[ChatBot] Failed to preload: ${text}`, error);
                    }
                });
                
                await Promise.all(promises);
                console.log('[ChatBot] ===== PRELOAD COMPLETE =====');
                console.log(`[ChatBot] Cached ${audioCacheRef.current.size} audio files`);
                console.log('[ChatBot] Cached texts:', Array.from(audioCacheRef.current.keys()));
                setIsPreloading(false);
            } catch (error) {
                console.error('[ChatBot] Failed to preload touch voices:', error);
                setIsPreloading(false);
            }
        };
        
        preloadTouchVoices();
    }, []);
    
    // Live2D触摸事件监听器
    useEffect(() => {
        console.log('[ChatBot] Setting up live2d:touch event listener');
        
        const handleLive2dTouch = async (event: Event) => {
            const customEvent = event as CustomEvent;
            const { text } = customEvent.detail;
            console.log('[ChatBot] ===== TOUCH EVENT =====');
            console.log('[ChatBot] Touch text:', text);
            console.log('[ChatBot] Total cached items:', audioCacheRef.current.size);
            console.log('[ChatBot] All cached keys:', Array.from(audioCacheRef.current.keys()));
            
            // 从缓存中获取预合成的音频
            const cachedAudio = audioCacheRef.current.get(text);
            console.log('[ChatBot] Cache lookup result:', cachedAudio ? 'HIT ✓' : 'MISS ✗');
            
            if (cachedAudio) {
                console.log('[ChatBot] Using cached audio, playing immediately!');
                try {
                    const { Live2dManager } = await import('@/lib/live2d/live2dManager');
                    const manager = Live2dManager.getInstance();
                    manager.pushAudioQueue(cachedAudio);
                    const result = manager.playAudio();
                    console.log('[ChatBot] ===== Cached audio playing instantly! =====');
                } catch (error) {
                    console.error('[ChatBot] Failed to play cached audio:', error);
                }
            } else {
                console.log('[ChatBot] Cache miss, synthesizing on-the-fly...');
                // 回退到实时合成
                try {
                    const { api_tts_infer } = await import('@/lib/api/server');
                    const { useSentioTtsStore } = await import('@/lib/store/sentio');
                    const { Live2dManager } = await import('@/lib/live2d/live2dManager');
                    const { base64ToArrayBuffer } = await import('@/lib/func');
                    const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
                    
                    const store = useSentioTtsStore.getState();
                    const ttsEngine = store.engine || 'default';
                    const ttsConfig = store.settings || {};
                    
                    const controller = new AbortController();
                    const audioBase64 = await api_tts_infer(ttsEngine, ttsConfig, text, controller.signal);
                    
                    if (audioBase64) {
                        const audioData = base64ToArrayBuffer(audioBase64);
                        const wavBuffer = await convertMp3ArrayBufferToWavArrayBuffer(audioData);
                        
                        const manager = Live2dManager.getInstance();
                        manager.pushAudioQueue(wavBuffer);
                        manager.playAudio();
                        console.log('[ChatBot] ===== On-the-fly audio playing =====');
                    }
                } catch (error) {
                    console.error('[ChatBot] Failed to synthesize touch voice:', error);
                }
            }
        };
        
        document.addEventListener('live2d:touch', handleLive2dTouch);
        console.log('[ChatBot] Event listener registered');
        
        return () => {
            document.removeEventListener('live2d:touch', handleLive2dTouch);
            console.log('[ChatBot] Event listener removed');
        };
    }, []);
    
    return (
        <div className="flex flex-col full-height-minus-64px pb-6 md:px-6 gap-6 justify-between items-center z-10">
            <ChatRecord />
            {chatMode == CHAT_MODE.IMMSERSIVE ? (infer_type == IFER_TYPE.NORMAL ? <ChatVadInput/> : <ChatStreamInput />) : <ChatInput />}
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