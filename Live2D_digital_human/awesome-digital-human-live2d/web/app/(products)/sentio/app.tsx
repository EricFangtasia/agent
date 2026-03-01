'use client'

import { useEffect, useState } from "react";
import { Live2d } from './components/live2d';
import ChatBot from './components/chatbot';
import { Header } from './components/header';
import { useAppConfig } from "./hooks/appConfig";
import { Spinner } from "@heroui/react";


export default function App() {
    const { setAppConfig } = useAppConfig();
    const [ isLoading, setIsLoading ] = useState(true);
    
    // 初始化应用
    useEffect(() => {
        setAppConfig(null);
        setIsLoading(false);
    }, [])

    return (
        <>
            <style jsx global>{`
                @keyframes radial-chaos {
                    0% {
                        background-position: 20% 30%, 75% 60%, 50% 15%, 10% 80%, 85% 25%;
                    }
                    16% {
                        background-position: 40% 70%, 15% 40%, 80% 85%, 60% 20%, 25% 50%;
                    }
                    32% {
                        background-position: 70% 50%, 30% 15%, 50% 75%, 90% 60%, 10% 35%;
                    }
                    48% {
                        background-position: 15% 65%, 85% 80%, 40% 25%, 70% 90%, 50% 10%;
                    }
                    64% {
                        background-position: 55% 40%, 20% 85%, 90% 30%, 35% 55%, 75% 70%;
                    }
                    80% {
                        background-position: 80% 20%, 45% 75%, 10% 45%, 65% 10%, 30% 90%;
                    }
                    100% {
                        background-position: 20% 30%, 75% 60%, 50% 15%, 10% 80%, 85% 25%;
                    }
                }
                
                .animated-gradient {
                    background: 
                        radial-gradient(circle at 20% 30%, rgba(120, 150, 255, 0.35) 0%, transparent 40%),
                        radial-gradient(circle at 75% 60%, rgba(100, 255, 200, 0.35) 0%, transparent 40%),
                        radial-gradient(circle at 50% 15%, rgba(255, 150, 255, 0.35) 0%, transparent 40%),
                        radial-gradient(circle at 10% 80%, rgba(100, 200, 255, 0.35) 0%, transparent 40%),
                        radial-gradient(circle at 85% 25%, rgba(150, 220, 255, 0.35) 0%, transparent 40%),
                        linear-gradient(135deg, #e8ecf4 0%, #d5dce8 100%);
                    background-size: 200% 200%, 200% 200%, 200% 200%, 200% 200%, 200% 200%, 100% 100%;
                    animation: radial-chaos 30s ease-in-out infinite;
                }
            `}</style>
            
            <div className='w-full h-full animated-gradient' style={{ position: 'relative' }}>
                {
                    isLoading ?
                    <Spinner className="w-screen h-screen z-10" color="secondary" size="lg" variant="wave" />
                    :
                    <div className='flex flex-col w-full h-full'>
                        <Header />
                        <div className="flex-1 z-10">
                            <ChatBot />
                        </div>
                    </div>
                }
                <Live2d />
            </div>
        </>
    );
}