import { LogoBar } from "@/components/header/logo";
import { Items } from "../items";
import { Button, ButtonGroup, addToast } from "@heroui/react";
import { NewspaperIcon, ChatBubbleLeftRightIcon, BookOpenIcon } from "@heroicons/react/24/solid";
import { useSentioChatModeStore, useChatRecordStore, useSentioAsrStore, useSentioNewsSettingsStore } from "@/lib/store/sentio";
import { CHAT_MODE } from "@/lib/protocol";
import { useTranslations } from 'next-intl';

// 时间范围选项
const TIME_RANGE_OPTIONS = [
    { key: '2days', label: '2天', days: 2 },
    { key: '3days', label: '3天', days: 3 },
    { key: '1week', label: '一周', days: 7 },
    { key: '2weeks', label: '二周', days: 14 },
    { key: '1month', label: '一个月', days: 30 },
];

function ChatModeSwitch() {
    const t = useTranslations('Products.sentio');
    const { chatMode, setChatMode } = useSentioChatModeStore();
    const { enable } = useSentioAsrStore();
    const { clearChatRecord } = useChatRecordStore();
    const { contentLines, timeRange, readImportantOnly, setContentLines, setTimeRange, setReadImportantOnly } = useSentioNewsSettingsStore();
    
    const handleModeChange = (mode: CHAT_MODE) => {
        if (mode === CHAT_MODE.DIALOGUE && !enable) {
            addToast({
                title: t('asrEnableTip'),
                color: "warning"
            })
            return;
        }
        
        // 如果已经是当前模式，不切换
        if (mode === chatMode) return;
        
        console.log('[Header] 切换模式:', mode, '当前模式:', chatMode);
        setChatMode(mode);
        clearChatRecord();
    }
    
    const isNewsMode = chatMode === CHAT_MODE.NEWS;
    const isQuotesMode = chatMode === CHAT_MODE.QUOTES;
    
    return (
        <div className="flex flex-row gap-2 items-center">
            {/* 新闻模式时显示设置 */}
            {isNewsMode && (
                <>
                    <ButtonGroup size="sm" variant="flat">
                        {[1, 2, 3, 4, 5].map(num => (
                            <Button
                                key={num}
                                isDisabled={contentLines === num}
                                onPress={() => setContentLines(num)}
                                className="min-w-8"
                            >
                                {num}行
                            </Button>
                        ))}
                    </ButtonGroup>
                    <ButtonGroup size="sm" variant="flat" color="secondary">
                        {TIME_RANGE_OPTIONS.map(option => (
                            <Button
                                key={option.key}
                                isDisabled={timeRange === option.key}
                                onPress={() => setTimeRange(option.key as any)}
                            >
                                {option.label}
                            </Button>
                        ))}
                    </ButtonGroup>
                    <Button
                        size="sm"
                        variant={readImportantOnly ? "solid" : "flat"}
                        color={readImportantOnly ? "warning" : "default"}
                        onPress={() => setReadImportantOnly(!readImportantOnly)}
                    >
                        {readImportantOnly ? "重磅" : "全部"}
                    </Button>
                </>
            )}
            <ButtonGroup variant="flat" color="secondary">
                <Button
                    startContent={<NewspaperIcon className="w-4 h-4" />}
                    isDisabled={isNewsMode}
                    onPress={() => handleModeChange(CHAT_MODE.NEWS)}
                >
                    {t('newsMode') || '新闻模式'}
                </Button>
                <Button
                    startContent={<BookOpenIcon className="w-4 h-4" />}
                    isDisabled={isQuotesMode}
                    onPress={() => handleModeChange(CHAT_MODE.QUOTES)}
                >
                    名言模式
                </Button>
                <Button
                    startContent={<ChatBubbleLeftRightIcon className="w-4 h-4" />}
                    isDisabled={!isNewsMode && !isQuotesMode}
                    onPress={() => handleModeChange(CHAT_MODE.DIALOGUE)}
                >
                    {t('chatMode') || '对话模式'}
                </Button>
            </ButtonGroup>
        </div>
    )
}

export function Header() {
    return (
        <div className="flex w-full h-[64px] p-6 justify-between z-10">
            <LogoBar isExternal={true}/>
            <div className="flex flex-row gap-4 items-center">
                <ChatModeSwitch />
                <Items />
            </div>
        </div>
    )
}