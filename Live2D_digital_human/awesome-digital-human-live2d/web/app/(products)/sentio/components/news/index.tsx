'use client'

import { useEffect, useState, useMemo, useRef, useCallback } from "react";
import { Card, CardBody, Chip } from "@heroui/react";
import { useSentioNewsSettingsStore } from "@/lib/store/sentio";

// ========== 抖音直播防封配置 ==========

// 无弹幕时主动触发话术（包含开场问候、互动引导、热点切入等）
const NO_DANMU_TRIGGERS = [
    // 原有互动话术
    // "有没有朋友想了解今天北向资金加仓了哪些板块？扣'北向'，我马上用数据解读！",
    "今天有一条重要快讯～你觉得这会影响哪些个股？可以在弹幕说说你的判断。",
    "我们来做个小投票：下个开盘日你更看好哪个板块？A.AI算力 B.消费复苏 C.新能源，扣A/B/C告诉我！",
    // "有没有朋友关注的盘面变化？扣'大盘'，我结合数据做实时分析！",
    "看到有朋友在默默观看～有什么想问的尽管打在弹幕，我会挑选回复哦！",
    "最近市场波动比较大，大家觉得是机会还是风险？扣'机会'或'风险'告诉我！",
    // "有朋友想了解今天的资金流向吗？扣'资金'，我用数据解读主力动向！",
    // 开场问候话术
    "大家好，欢迎收看本期新闻资讯，我是数字人主播。",
    "各位观众朋友们，大家好，新闻资讯马上为您呈现。",
    "您好，欢迎来到直播间，最新消息为您同步播报。",
    "大家好，今天的重点新闻已为您整理完毕。",
    "欢迎锁定本频道，我是数字主播，为您带来权威资讯。",
    "大家久等了，今天的热点内容马上开始。",
    "欢迎进入新闻直播间，实时动态一手掌握。",
    "各位网友、观众朋友们，大家好，我是今日新闻主播。",
    "准时相见，今天的重要新闻不容错过。",
    "欢迎收看，我将为您带来最新、最快、最全面的资讯。",
    "新的一天，新的资讯，我已准备就绪。",
    "各位观众，欢迎收看，精彩内容马上开始。",
    "大家好，这里是实时新闻播报，我是数字主播。",
    "欢迎来到新闻现场，全球热点为您速递。",
    "感谢您的守候，现在为您开启今日新闻。",
    "各位朋友，欢迎光临，今天的重点已划好。",
    "欢迎在线观看，我将为您清晰解读今日要闻。",
    "大家好，新闻不中断，信息不迟到。",
    "欢迎收看，我是您的专属数字新闻主播。",
    "各位观众，准备好了吗？今日新闻现在开始。",
    // 互动引导话术
    "欢迎在评论区留言，您关心的就是我们关注的。",
    "有什么想了解的话题，可以打在公屏上。",
    "点赞关注，不错过每一条重要新闻。",
    "欢迎分享转发，让更多人看到权威资讯。",
    "您的疑问，我们将在后续为您解答。",
    "持续锁定，更多深度内容正在路上。",
    "欢迎点亮小红心，支持一下主播。",
    "您最关心哪类新闻？可以告诉我。",
    "关注不迷路，每日资讯准时送达。",
    "评论区说说您的看法，我们一起理性讨论。",
    "有想看的内容，欢迎随时点播。",
    "欢迎预约下一期，重要内容不错过。",
    "感谢您的观看和陪伴，我们继续播报。",
    "欢迎新进来的朋友，这里是实时新闻。",
    "您的每一次互动，都是对我们的支持。",
    "如果有突发消息，我们随时插播。",
    "停留一分钟，了解今天全部重点。",
    "欢迎收藏本频道，资讯随时回看。",
    "看完记得关注，明天同一时间继续相见。",
    "感谢守候，今天的新闻就到这里。",
];

// 新闻播报互动话术（每条新闻播完后插入，包含热点切入、政策民生、财经科技等）
const NEWS_INTERACTION_TEMPLATES = [
    // 原有互动话术
    "这条新闻大家怎么看？可以在弹幕聊聊你的看法，我或许会抽取做专业解读～",
    "这个消息挺重要的，大家觉得会影响哪些个股？可以在弹幕说说你的判断！",
    "这条快讯涉及{industry}板块，有朋友关注这个方向吗？可以在弹幕告诉我～",
    "关于这条新闻～有后续解读。有朋友想深入了解吗？",
    // 热点切入话术
    "刚刚传来最新消息，我们马上为您跟进。",
    "突发新闻！第一时间为您同步现场情况。",
    "今天全网都在关注的这件事，为您详细解读。",
    "重要提醒！这条消息关系到每一个人。",
    "最新进展来了，事件有了新变化。",
    "刚刚发布！官方最新通报为您梳理。",
    "热点聚焦，今天最受关注的话题在这里。",
    "不容错过！今天有三大重点新闻。",
    "注意看，这个消息正在刷屏全网。",
    "权威发布，第一时间为您送达。",
    "最新数据出炉，结果有明显变化。",
    "刚刚确认！这件事有了明确结论。",
    "紧急关注！相关部门刚刚作出回应。",
    "今日焦点，我们为您深度拆解。",
    "好消息来了，将影响你的生活。",
    "热点事件完整时间线，为您一次性理清。",
    "刚刚更新！现场画面同步为您呈现。",
    "今天最值得看的新闻，我帮你总结好了。",
    "重磅消息！正式文件已对外公布。",
    "全网热议，我们用事实为您客观呈现。",
    // 政策民生话术
    "新政策出台，这些变化与你息息相关。",
    "民生关注，这些福利即将落地。",
    "关注我，点点赞，每天新鲜事给你看。",
    "好消息，这类人群将迎来利好。",
    "注意！这些规定将于近期开始执行。",
    "民生热点回应，官方给出明确答复。",
    "出行、就医、办事，今天都有新消息。",
    "事关收入与保障，这条请认真看完。",
    "教育、医疗、养老，今日重点解读。",
    "提醒市民，这些事项请提前做好准备。",
    "简化流程！多项业务实现一网通办。",
    "物价、供应、保障情况，为您实时播报。",
    "交通出行有新变化，出行前请留意。",
    "民生实事进展顺利，多项工程即将完工。",
    "针对大家关心的问题，权威回应来了。",
    "假期、周末出行，这些信息很有用。",
    "安全提醒：这些事项要特别注意防范。",
    "生活小贴士，帮您省心省力更省钱。",
    // 国际财经科技话术
    "国际热点追踪，全球动态为您梳理。",
    "最新财经数据发布，市场有新动向。",
    "科技突破！这项技术迎来重要进展。",
    "全球市场动态，一分钟看懂走势。",
    "国际会议传来重要成果。",
    "产业新动向，未来发展趋势清晰。",
    "财经关注：这些领域迎来新机遇。",
    "科技新闻：新产品、新功能正式发布。",
    "国际局势最新进展，持续为您关注。",
    "经济数据解读，看懂宏观趋势。",
    "行业新规实施，影响相关产业发展。",
    "新能源、新基建，最新进展同步。",
    "国际贸易与合作，传来好消息。",
    "数字经济新动态，发展再提速。",
    "全球天气、灾害、突发事件及时播报。",
    "医疗健康新突破，研究取得重要进展。",
    "能源供应、价格动态，为您及时关注。",
    "科技创新应用，正在改变生活方式。",
    "海外重要公告，影响全球市场。",
    "财经日历：今天这些数据值得关注。",
];

// 主动发起投票话术
const VOTE_TEMPLATES = [
    "我们来做个小投票：你最看好的板块是？A.AI算力 B.消费复苏 C.新能源，扣A/B/C告诉我！",
    "大家觉得下一个交易日大盘会怎么走？扣'涨'、'跌'或'震荡'，说说技术面或者基本面！",
    "你更看好哪个方向？A.科技成长 B.价值蓝筹 C.周期反转，扣A/B/C告诉我～",
];

// 已使用话术索引（避免重复）
const usedTemplateIndices = new Set<number>();

// 话术TTS音频缓存（本地内存缓存，避免重复请求）
const templateAudioCache = new Map<string, ArrayBuffer>();
let isCacheLoading = false;
let cacheLoadProgress = 0;

// 生成单个话术的TTS音频（使用现有TTS API，后端已有文件缓存）
async function generateTTSAudio(text: string): Promise<ArrayBuffer | null> {
    try {
        const { api_tts_infer } = await import('@/lib/api/server');
        const { useSentioTtsStore } = await import('@/lib/store/sentio');
        const { base64ToArrayBuffer } = await import('@/lib/func');
        const { convertMp3ArrayBufferToWavArrayBuffer } = await import('@/lib/utils/audio');
        
        const store = useSentioTtsStore.getState();
        const ttsEngine = store.engine || 'default';
        const ttsConfig = store.settings || {};
        
        console.log('[TTS] 生成音频:', text.substring(0, 20) + '...');
        
        const controller = new AbortController();
        const audioBase64 = await api_tts_infer(ttsEngine, ttsConfig, text, controller.signal);
        
        if (audioBase64) {
            const audioData = base64ToArrayBuffer(audioBase64);
            // EdgeTTS返回的是MP3，需要转换为WAV
            return await convertMp3ArrayBufferToWavArrayBuffer(audioData);
        }
        console.warn('[TTS] 未返回音频数据');
        return null;
    } catch (error) {
        console.error('[TTS] 生成音频失败:', error);
        return null;
    }
}

// 预加载所有话术TTS音频到本地内存缓存
// 后端已有文件缓存，这里只是预热本地内存缓存
async function preloadAllTemplateTTS() {
    if (isCacheLoading) return;
    isCacheLoading = true;
    
    // 合并所有话术
    const allTemplates = [
        ...NO_DANMU_TRIGGERS,
        ...NEWS_INTERACTION_TEMPLATES,
        ...VOTE_TEMPLATES
    ];
    
    console.log(`[TTS Cache] 预热本地内存缓存，共 ${allTemplates.length} 条话术...`);
    
    // 后端已经有文件缓存，我们只需要预热前几个常用话术到内存
    const preloadCount = Math.min(10, allTemplates.length);
    
    for (let i = 0; i < preloadCount; i++) {
        const text = allTemplates[i];
        if (!templateAudioCache.has(text)) {
            const audio = await generateTTSAudio(text);
            if (audio) {
                templateAudioCache.set(text, audio);
            }
        }
        cacheLoadProgress = Math.round(((i + 1) / preloadCount) * 100);
    }
    
    cacheLoadProgress = 100;
    isCacheLoading = false;
    console.log(`[TTS Cache] 预热完成，本地缓存 ${templateAudioCache.size} 条`);
}

// 播放缓存的话术音频
async function playCachedTemplate(text: string): Promise<boolean> {
    try {
        const { Live2dManager } = await import('@/lib/live2d/live2dManager');
        const manager = Live2dManager.getInstance();
        
        // 检查本地内存缓存
        let audio = templateAudioCache.get(text);
        
        if (!audio) {
            // 本地缓存没有，生成新的TTS音频
            console.log('[TTS] 本地未命中，生成新音频:', text.substring(0, 20) + '...');
            audio = await generateTTSAudio(text);
            if (audio) {
                // 保存到本地内存缓存
                templateAudioCache.set(text, audio);
            }
        } else {
            console.log('[TTS] 本地命中:', text.substring(0, 20) + '...');
        }
        
        if (audio) {
            manager.pushAudioQueue(audio);
            manager.playAudio();
            return true;
        }
        return false;
    } catch (error) {
        console.error('[TTS] 播放失败:', error);
        return false;
    }
}

// 随机获取1-3个不重复的话术
function getRandomTemplates(templates: string[], minCount: number = 1, maxCount: number = 3): string[] {
    const count = minCount + Math.floor(Math.random() * (maxCount - minCount + 1));
    const result: string[] = [];
    const availableIndices: number[] = [];
    
    // 收集未使用的索引
    for (let i = 0; i < templates.length; i++) {
        if (!usedTemplateIndices.has(i)) {
            availableIndices.push(i);
        }
    }
    
    // 如果可用索引不足，重置已使用记录
    if (availableIndices.length < count) {
        usedTemplateIndices.clear();
        for (let i = 0; i < templates.length; i++) {
            availableIndices.push(i);
        }
    }
    
    // 随机选择
    for (let i = 0; i < count && availableIndices.length > 0; i++) {
        const randomIdx = Math.floor(Math.random() * availableIndices.length);
        const templateIdx = availableIndices[randomIdx];
        result.push(templates[templateIdx]);
        usedTemplateIndices.add(templateIdx);
        availableIndices.splice(randomIdx, 1);
    }
    
    return result;
}

// 随机获取单个话术（兼容旧逻辑）
function getRandomTemplate(templates: string[]): string {
    return templates[Math.floor(Math.random() * templates.length)];
}

// 格式化时间为"刚刚"、"X分钟前"等
function formatTimeAgo(dateStr: string): string {
    if (!dateStr) return '刚刚';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}小时前`;
    return `${Math.floor(diffHours / 24)}天前`;
}

// 新闻类型定义
interface NewsItem {
    id: number;
    title: string;
    content: string;
    origin_title?: string;      // 原始标题（过滤前）
    origin_content?: string;    // 原始内容（过滤前）
    industry: string;
    industry_level: string;
    sector: string;
    investment_rating: string;
    investment_type: string;  // 短期/长期
    analysis: string;  // AI分析内容
    analysis_time?: string;
    publish_time?: string;
    isImportant?: boolean;
    is_viral?: number;
    url?: string;
}

interface NewsDisplayProps {
    onSpeak?: (text: string) => void;
}

// 时间范围选项
const TIME_RANGE_OPTIONS = [
    { key: '2days', label: '2天', days: 2 },
    { key: '3days', label: '3天', days: 3 },
    { key: '1week', label: '一周', days: 7 },
    { key: '2weeks', label: '二周', days: 14 },
    { key: '1month', label: '一个月', days: 30 },
];

// 默认模拟数据 - 包含重磅新闻
const DEFAULT_NEWS: NewsItem[] = [
    {
        id: 1,
        title: "【重磅】央行降准释放万亿流动性",
        content: "央行今日宣布降准0.5个百分点，释放长期流动性约1万亿元。此举旨在加大对实体经济的支持力度，降低金融机构融资成本，促进经济平稳运行。",
        industry: "金融",
        industry_level: "A",
        sector: "银行",
        investment_rating: "★★★★★",
        investment_type: "长期",
        analysis: "央行降准是重大货币政策利好，预计将释放约1万亿元流动性。此举有利于降低银行资金成本，提升信贷投放能力，对A股市场特别是金融板块形成明显提振。建议关注银行、券商等金融股的后续表现。",
        analysis_time: new Date().toISOString(),
        isImportant: true
    },
    {
        id: 2,
        title: "科技板块行情",
        content: "半导体板块今日全线上涨，多只个股涨停。分析师认为AI产业链将持续受益于技术创新、政策支持以及市场需求旺盛等多重利好因素。",
        industry: "科技",
        industry_level: "A",
        sector: "人工智能",
        investment_rating: "★★★★",
        investment_type: "短期",
        analysis: "AI产业链持续受到市场追捧，技术创新和政策支持共振。建议关注具备核心技术竞争力的AI龙头公司，但需注意短期涨幅过大带来的回调风险。",
        analysis_time: new Date().toISOString()
    },
    {
        id: 3,
        title: "【重磅】新能源车购置税减免延续",
        content: "国务院常务会议确定，将延续新能源汽车购置税减免政策至2027年底。这一重磅利好将进一步刺激新能源汽车消费，带动产业链发展。",
        industry: "汽车",
        industry_level: "A",
        sector: "新能源汽车",
        investment_rating: "★★★★★",
        investment_type: "长期",
        analysis: "购置税减免政策延续至2027年，超出市场预期，明确了行业发展长期政策导向。新能源汽车渗透率有望持续提升，建议关注产业链龙头企业的长期投资机会。",
        analysis_time: new Date().toISOString(),
        isImportant: true
    },
    {
        id: 4,
        title: "医药行业动态",
        content: "创新药研发取得重大进展，多款国产新药获批上市。医药板块整体估值处于历史低位，机构投资者开始布局。",
        industry: "医药",
        industry_level: "A",
        sector: "创新药",
        investment_rating: "★★★★",
        investment_type: "长期",
        analysis: "医药板块处于历史估值低位，创新药研发进展催化板块情绪。建议关注具备创新能力和国际化潜力的创新药企，中长期配置价值显现。",
        analysis_time: new Date(Date.now() - 86400000).toISOString()
    },
    {
        id: 5,
        title: "【重磅】房地产政策全面松绑",
        content: "多部门联合出台房地产重磅政策，取消限购限售，首套房首付比例降至20%。业内人士认为，政策底已经确立，市场有望迎来复苏。",
        industry: "房地产",
        industry_level: "A",
        sector: "住宅地产",
        investment_rating: "★★★★★",
        investment_type: "短期",
        analysis: "房地产政策力度超预期，政策底已明确。但行业基本面复苏仍需时间，建议关注优质地产龙头的机会，短线可适度参与政策炒作。",
        analysis_time: new Date(Date.now() - 86400000 * 2).toISOString(),
        isImportant: true
    },
    {
        id: 6,
        title: "房地产政策",
        content: "多地出台房地产优化政策，限购限售进一步放松。业内人士认为，政策底已经出现，市场有望逐步企稳回升。",
        industry: "房地产",
        industry_level: "B",
        sector: "住宅地产",
        investment_rating: "★★",
        investment_type: "长期",
        analysis: "房地产政策持续放松，但行业复苏仍面临挑战。建议关注基本面稳健的优质房企，谨慎对待高负债开发商。",
        analysis_time: new Date(Date.now() - 86400000 * 3).toISOString()
    },
    {
        id: 7,
        title: "【重磅】AI芯片获突破性进展",
        content: "国产AI芯片传来重磅消息，最新一代产品性能提升10倍，打破国外技术垄断。这标志着我国在人工智能领域取得重大突破。",
        industry: "科技",
        industry_level: "A",
        sector: "人工智能",
        investment_rating: "★★★★★",
        investment_type: "长期",
        analysis: "国产AI芯片技术突破具有战略意义，有望打破国外垄断。算力自主可控是AI发展的基础，建议关注国产芯片产业链的长期投资机会。",
        analysis_time: new Date(Date.now() - 86400000 * 5).toISOString(),
        isImportant: true
    },
    {
        id: 8,
        title: "新能源车市场",
        content: "新能源汽车销量再创新高，产业链景气度持续提升。多家车企发布新品布局市场，固态电池技术取得突破，续航里程大幅提升。",
        industry: "汽车",
        industry_level: "B",
        sector: "新能源汽车",
        investment_rating: "★★★",
        investment_type: "短期",
        analysis: "新能源车销量持续增长，但竞争加剧导致价格战风险。建议关注具备技术优势和成本控制能力的龙头企业。",
        analysis_time: new Date(Date.now() - 86400000 * 10).toISOString()
    }
];

export function NewsDisplay({ onSpeak }: NewsDisplayProps) {
    const [newsList, setNewsList] = useState<NewsItem[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(true);
    const [cacheProgress, setCacheProgress] = useState(0); // 缓存进度
    
    // 从 store 获取设置
    const { contentLines, timeRange, readImportantOnly } = useSentioNewsSettingsStore();
    
    // ========== 防封相关状态和逻辑 ==========
    const lastInteractionTime = useRef(Date.now());
    const expressionInterval = useRef<NodeJS.Timeout | null>(null);
    const usedKeywords = useRef<Set<string>>(new Set());
    
    // 组件初始化时预加载所有话术TTS
    useEffect(() => {
        console.log('[News] 开始预加载话术TTS缓存...');
        
        // 更新进度显示
        const progressInterval = setInterval(() => {
            setCacheProgress(cacheLoadProgress);
        }, 500);
        
        // 开始预加载
        preloadAllTemplateTTS().then(() => {
            clearInterval(progressInterval);
            setCacheProgress(100);
        });
        
        return () => clearInterval(progressInterval);
    }, []);
    
    // 触发Live2D表情变化（每8-15秒随机）
    const triggerExpression = useCallback(() => {
        const expressions = ['f01', 'f02', 'f03', 'f04', 'f05'];
        const randomExp = expressions[Math.floor(Math.random() * expressions.length)];
        
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('live2d:expression', { 
                detail: { expression: randomExp } 
            }));
        }
    }, []);
    
    // 触发随机动作
    const triggerRandomAction = useCallback(() => {
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('live2d:action', {}));
        }
    }, []);
    
    // Live2D表情定时切换
    useEffect(() => {
        triggerExpression();
        
        const getRandomInterval = () => 8000 + Math.random() * 7000;
        const scheduleNext = () => {
            expressionInterval.current = setTimeout(() => {
                triggerExpression();
                // 随机触发动作
                if (Math.random() > 0.4) {
                    triggerRandomAction();
                }
                scheduleNext();
            }, getRandomInterval());
        };
        scheduleNext();
        
        return () => {
            if (expressionInterval.current) clearTimeout(expressionInterval.current);
        };
    }, [triggerExpression, triggerRandomAction]);
    
    // 获取新闻数据
    useEffect(() => {
        const fetchNews = async () => {
            try {
                const days = TIME_RANGE_OPTIONS.find(o => o.key === timeRange)?.days || 7;
                console.log('[News] 正在获取新闻，天数:', days);
                const response = await fetch(`http://localhost:8880/adh/news?days=${days}`);
                if (response.ok) {
                    const data = await response.json();
                    console.log('[News] API 原始响应:', data);
                    // 确保提取数组数据
                    let newsData = [];
                    if (Array.isArray(data)) {
                        newsData = data;
                    } else if (data && Array.isArray(data.data)) {
                        newsData = data.data;
                    } else if (data && Array.isArray(data.result)) {
                        newsData = data.result;
                    }
                    console.log('[News] 解析后新闻数量:', newsData.length);
                    setNewsList(newsData);
                } else {
                    console.error('[News] API 响应失败:', response.status);
                    setNewsList([]);
                }
            } catch (error) {
                console.error('[News] 获取新闻失败:', error);
                setNewsList([]);
            } finally {
                setLoading(false);
            }
        };
        
        fetchNews();
        
        // 每30秒轮询一次
        const pollInterval = setInterval(fetchNews, 30000);
        
        return () => clearInterval(pollInterval);
    }, [timeRange]);

    // 过滤新闻（后端已按时间过滤，前端只做重磅筛选）
    // 同时去除标题和内容重复的新闻
    const filteredNews = useMemo(() => {
        // 确保 newsList 是数组
        if (!Array.isArray(newsList)) {
            console.error('[News] newsList 不是数组:', typeof newsList, newsList);
            return [];
        }
        
        console.log('[News] 当前时间范围:', timeRange, '新闻总数:', newsList.length);
        
        // 先进行去重（基于ID或者标题）
        const uniqueMap = new Map<number, NewsItem>();
        for (const news of newsList) {
            // 使用ID去重，如果没有ID则使用标题
            const key = news.id || news.title;
            if (!uniqueMap.has(key as number)) {
                uniqueMap.set(key as number, news);
            }
        }
        const uniqueNews = Array.from(uniqueMap.values());
        console.log('[News] 去重后新闻数量:', uniqueNews.length, '原始:', newsList.length);
        
        // 如果只显示重磅新闻
        if (readImportantOnly) {
            const important = uniqueNews.filter(news => news.isImportant || news.is_viral === 1);
            console.log('[News] 重磅新闻数量:', important.length);
            return important;
        }
            
        return uniqueNews;
    }, [timeRange, readImportantOnly, newsList]);
    
    // 已读新闻ID记录（避免重复）
    const readNewsIds = useRef<Set<number>>(new Set());
    
    // 计算当前显示的新闻数量
    const newsCount = contentLines * 2;
    
    // 获取当前显示的新闻（必须在所有hooks中，不能在条件语句后）
    // 使用已读记录，避免重复播放
    const displayedNews: NewsItem[] = useMemo(() => {
        if (filteredNews.length === 0) return [];
        
        const news: NewsItem[] = [];
        let attempts = 0;
        let startIdx = currentIndex;
        
        // 尝试获取未读新闻
        while (news.length < newsCount && attempts < filteredNews.length * 2) {
            const newsItem = filteredNews[startIdx % filteredNews.length];
            
            // 如果已读记录已满（所有新闻都读过了），清空重新开始
            if (readNewsIds.current.size >= filteredNews.length) {
                console.log('[News] 所有新闻已播放完毕，清空已读记录');
                readNewsIds.current.clear();
            }
            
            // 只添加未读过的新闻
            if (newsItem && !readNewsIds.current.has(newsItem.id)) {
                news.push(newsItem);
                readNewsIds.current.add(newsItem.id);
                console.log(`[News] 添加新闻 ID=${newsItem.id}: ${newsItem.title.substring(0, 30)}...`);
            }
            
            startIdx++;
            attempts++;
        }
        
        console.log(`[News] 本批新闻数量: ${news.length}, 已读总数: ${readNewsIds.current.size}/${filteredNews.length}`);
        return news;
    }, [filteredNews, currentIndex, newsCount]);

    // ========== 简化的播放队列系统 ==========
    // 播放队列项类型
    type PlayQueueItem = {
        type: 'news' | 'interaction' | 'vote';
        text: string;
        newsId?: number;  // 新闻ID（仅新闻类型）
    };
    
    const [playQueue, setPlayQueue] = useState<PlayQueueItem[]>([]);  // 播放队列
    const [queueIndex, setQueueIndex] = useState(0);  // 当前播放索引
    const [isPlaying, setIsPlaying] = useState(false);  // 是否正在播放
    const [highlightedNewsId, setHighlightedNewsId] = useState<number | null>(null);  // 高亮的新闻ID
    const [audioActivated, setAudioActivated] = useState(false);  // AudioContext是否已激活
    
    // 当前互动话术显示
    const [interactionText, setInteractionText] = useState('');
    const [showInteraction, setShowInteraction] = useState(false);
    
    // 构建播放队列（新闻 -> 互动话术 -> 新闻 -> ... -> 投票话术）
    const buildPlayQueue = useCallback(() => {
        if (filteredNews.length === 0) return [];
        
        const queue: PlayQueueItem[] = [];
        const newsToPlay = displayedNews.slice(0, newsCount);
        
        for (let i = 0; i < newsToPlay.length; i++) {
            const news = newsToPlay[i];
            if (!news) continue;
            
            // 添加新闻
            let text = news.title;
            if (news.content && news.content !== news.title) {
                text = `${news.title}。${news.content}`;
            }
            queue.push({ type: 'news', text, newsId: news.id });
            
            // 添加互动话术（新闻之间）
            if (i < newsToPlay.length - 1) {
                const template = getRandomTemplate(NEWS_INTERACTION_TEMPLATES);
                const processed = template.replace('{industry}', news.industry || '相关');
                queue.push({ type: 'interaction', text: processed });
            }
        }
        
        // 添加投票话术（最后）
        queue.push({ type: 'vote', text: getRandomTemplate(VOTE_TEMPLATES) });
        
        console.log(`[Queue] 构建播放队列，共 ${queue.length} 项`);
        return queue;
    }, [filteredNews, displayedNews, newsCount]);
    
    // 播放音频并等待完成
    const playAndWait = useCallback(async (text: string): Promise<void> => {
        return new Promise(async (resolve) => {
            if (!text) {
                console.log(`[Play] 文本为空，跳过`);
                resolve();
                return;
            }
            
            console.log(`[Play] 开始播放: ${text.substring(0, 30)}...`);
            
            // 调用TTS播放
            if (onSpeak) {
                onSpeak(text);
            }
            
            // 等待音频播放完成
            let hasStarted = false;
            let noPlayingCount = 0;
            let waitStartCount = 0;
            let resolved = false;
            
            const doResolve = () => {
                if (resolved) return;
                resolved = true;
                console.log(`[Play] 结束播放: ${text.substring(0, 30)}...`);
                clearInterval(checkInterval);
                clearTimeout(timeoutId);
                resolve();
            };
            
            const checkInterval = setInterval(() => {
                try {
                    const Live2dManager = require('@/lib/live2d/live2dManager').Live2dManager;
                    const manager = Live2dManager.getInstance();
                    const isPlaying = manager.isAudioPlaying();
                    
                    if (isPlaying) {
                        hasStarted = true;
                        noPlayingCount = 0;
                        waitStartCount = 0;
                    } else if (hasStarted) {
                        noPlayingCount++;
                        if (noPlayingCount >= 2) {  // 减少到2次检测，加快切换
                            console.log(`[Play] 播放完成`);
                            doResolve();
                        }
                    } else {
                        waitStartCount++;
                        if (waitStartCount >= 20) {  // 减少到20次，6秒超时
                            console.log(`[Play] 等待超时，强制继续`);
                            doResolve();
                        }
                    }
                } catch (e) {
                    console.error(`[Play] 检测播放状态出错:`, e);
                    doResolve();
                }
            }, 300);
            
            // 总超时时间20秒
            const timeoutId = setTimeout(() => {
                console.log(`[Play] 总超时，强制继续`);
                doResolve();
            }, 20000);
        });
    }, [onSpeak]);
    
    // ========== 队列播放系统（分离UI更新和音频播放）==========
    // 当前播放项的文本（用于触发播放）
    const [currentPlayText, setCurrentPlayText] = useState<string | null>(null);
    
    // 1. 当队列索引变化时，更新UI（不播放音频）
    useEffect(() => {
        if (!audioActivated || playQueue.length === 0) return;
        
        if (queueIndex >= playQueue.length) {
            // 队列播放完毕，构建新队列
            console.log(`[Queue] 队列播放完毕，准备下一批新闻`);
            console.log(`[Queue] 当前索引: ${currentIndex}, 新闻总数: ${filteredNews.length}, 每批数量: ${newsCount}`);
            
            // 重置状态
            setQueueIndex(0);
            setPlayQueue([]);
            setHighlightedNewsId(null);
            setShowInteraction(false);
            setInteractionText('');
            setCurrentPlayText(null);
            
            // 更新新闻索引，跳过已显示的新闻数量
            // displayedNews.length 是实际播放的新闻数量（可能小于newsCount）
            const actualPlayedCount = displayedNews.filter(n => n && n.id).length;
            const nextIndex = currentIndex + actualPlayedCount;
            console.log(`[Queue] 实际播放: ${actualPlayedCount}条, 下一批索引: ${nextIndex}`);
            setCurrentIndex(nextIndex);
            return;
        }
        
        const item = playQueue[queueIndex];
        if (!item) {
            console.error(`[Queue] 队列项为空，索引=${queueIndex}`);
            // 跳过空项
            setQueueIndex(prev => prev + 1);
            return;
        }
        
        // 根据类型更新UI
        if (item.type === 'news') {
            setHighlightedNewsId(item.newsId || null);
            setShowInteraction(false);
            setInteractionText('');
            console.log(`[Queue] UI更新 - 新闻高亮 ID=${item.newsId}, 文本=${item.text.substring(0, 30)}...`);
        } else {
            setHighlightedNewsId(null);
            setInteractionText(item.text);
            setShowInteraction(true);
            console.log(`[Queue] UI更新 - 显示话术: ${item.text.substring(0, 30)}...`);
        }
        
        // 设置当前播放文本，触发播放
        setCurrentPlayText(item.text);
        
    }, [audioActivated, playQueue, queueIndex, newsCount, filteredNews.length, currentIndex]);
    
    // 2. 当播放文本变化时，播放音频（UI已更新）
    useEffect(() => {
        if (!currentPlayText || isPlaying) return;
        
        // 延迟150ms让UI先渲染完成
        const timer = setTimeout(() => {
            console.log(`[Queue] 开始播放音频: ${currentPlayText.substring(0, 30)}...`);
            setIsPlaying(true);
            
            playAndWait(currentPlayText).then(() => {
                console.log(`[Queue] 播放完成，准备下一个`);
                
                // 清理状态
                setShowInteraction(false);
                setIsPlaying(false);
                setCurrentPlayText(null);
                
                // 延迟100ms再切换到下一项，避免状态冲突
                setTimeout(() => {
                    setQueueIndex(prev => {
                        const next = prev + 1;
                        console.log(`[Queue] 队列索引: ${prev} -> ${next}`);
                        return next;
                    });
                }, 100);
            }).catch(err => {
                console.error(`[Queue] 播放出错:`, err);
                // 出错也要继续
                setShowInteraction(false);
                setIsPlaying(false);
                setCurrentPlayText(null);
                setTimeout(() => {
                    setQueueIndex(prev => prev + 1);
                }, 100);
            });
        }, 150);
        
        return () => clearTimeout(timer);
    }, [currentPlayText, isPlaying, playAndWait]);
    
    // 当新闻数据变化时构建队列
    useEffect(() => {
        if (audioActivated && filteredNews.length > 0 && playQueue.length === 0 && !isPlaying) {
            const queue = buildPlayQueue();
            if (queue.length > 0) {
                setPlayQueue(queue);
                setQueueIndex(0);
            }
        }
    }, [audioActivated, filteredNews, buildPlayQueue, playQueue.length, isPlaying]);
    
    // 激活音频
    const activateAudio = useCallback(async () => {
        try {
            const { Live2dManager } = await import('@/lib/live2d/live2dManager');
            const manager = Live2dManager.getInstance();
            setAudioActivated(true);
        } catch (e) {
            setAudioActivated(true);
        }
    }, []);
    
    // 主动触发互动（30秒无互动时）
    useEffect(() => {
        const interval = setInterval(() => {
            if (isPlaying) return;  // 正在播放队列，不触发
            
            const elapsed = Date.now() - lastInteractionTime.current;
            if (elapsed > 28000) {
                const template = Math.random() > 0.5 
                    ? getRandomTemplate(NO_DANMU_TRIGGERS)
                    : getRandomTemplate(VOTE_TEMPLATES);
                playAndWait(template);
                triggerExpression();
            }
        }, 10000);
        
        return () => clearInterval(interval);
    }, [isPlaying, playAndWait, triggerExpression]);
    
    
    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">加载中...</div>
            </div>
        );
    }

    if (newsList.length === 0) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-gray-500">暂无新闻</div>
            </div>
        );
    }

    // 根据行数生成索引数组
    const leftIndices: number[] = [];
    const rightIndices: number[] = [];
    for (let row = 0; row < contentLines; row++) {
        leftIndices.push(row * 2);     // 左侧：0, 2, 4, 6...
        rightIndices.push(row * 2 + 1); // 右侧：1, 3, 5, 7...
    }

    // 判断某条新闻是否正在被朗读（使用新闻ID）
    const isCurrentlyReading = (newsId: number | undefined): boolean => {
        return newsId !== undefined && newsId === highlightedNewsId;
    };

    return (
        <div className="flex flex-col w-full h-full overflow-hidden p-2 relative">
            {/* 音频激活提示 - 页面中央 */}
            {!audioActivated && filteredNews.length > 0 && (
                <div 
                    className="absolute inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm cursor-pointer"
                    onClick={(e) => {
                        e.stopPropagation();  // 阻止事件冒泡
                        e.preventDefault();
                        activateAudio();
                    }}
                >
                    <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl px-8 py-6 shadow-2xl border border-white/20 animate-pulse">
                        <div className="text-2xl text-white font-bold text-center">
                            🔊 点击开始播报
                        </div>
                        <div className="text-sm text-white/80 text-center mt-2">
                            点击任意位置激活音频
                        </div>
                    </div>
                </div>
            )}
            
            {/* 话术缓存进度提示 - 右上角 */}
            {cacheProgress < 100 && (
                <div className="absolute top-2 right-2 z-50">
                    <div className="bg-black/60 backdrop-blur-sm rounded-lg px-3 py-1 text-white text-sm">
                        话术缓存中 {cacheProgress}%
                    </div>
                </div>
            )}
            
            {/* 互动消息弹窗 - 底部居中（往上移，避免挡住名言） */}
            {showInteraction && (
                <div className="absolute bottom-20 left-1/2 transform -translate-x-1/2 z-50">
                    <div className="bg-gradient-to-r from-blue-600/95 to-purple-600/95 backdrop-blur-sm rounded-2xl px-6 py-3 shadow-2xl max-w-2xl border border-white/20">
                        <div className="text-lg text-white text-center leading-relaxed">
                            💬 {interactionText}
                        </div>
                    </div>
                </div>
            )}
            
            {/* 新闻内容 - 3x2网格布局，中间留空给数字人 */}
            <div className="flex flex-row flex-1 gap-2 overflow-hidden">
                {/* 左侦3行 - 靠左，加宽 */}
                <div className="w-2/5 flex flex-col gap-2 h-full overflow-y-auto overflow-x-hidden pl-2 no-scrollbar">
                    {/* 左侧新闻 */}
                    {leftIndices.map(idx => (
                        <Card key={idx} className={`${isCurrentlyReading(displayedNews[idx]?.id) ? 'bg-amber-100 ring-4 ring-amber-400 ring-opacity-75' : 'bg-white/80'} backdrop-blur-sm border-none shadow-none transition-all duration-300`}>
                            <CardBody className="p-3">
                                {/* 朗读指示器 */}
                                {isCurrentlyReading(displayedNews[idx]?.id) && (
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                        </span>
                                        <span className="text-green-600 font-bold text-sm">正在播报...</span>
                                    </div>
                                )}
                                {/* 实时时间戳 + 标签 */}
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    {displayedNews[idx]?.publish_time && (
                                        <Chip size="sm" color="success" variant="solid">
                                            {formatTimeAgo(displayedNews[idx]?.publish_time || '')}
                                        </Chip>
                                    )}
                                    {displayedNews[idx]?.isImportant && (
                                        <Chip size="lg" color="danger" variant="solid">重磅</Chip>
                                    )}
                                    <Chip size="lg" color="primary" variant="flat">{displayedNews[idx]?.industry || '其他'}</Chip>
                                    <Chip size="lg" color="warning" variant="flat">{displayedNews[idx]?.investment_rating || '★★'}</Chip>
                                    {displayedNews[idx]?.investment_type && (
                                        <Chip 
                                            size="lg" 
                                            color={displayedNews[idx].investment_type === '短期' ? 'success' : 'secondary'} 
                                            variant="flat"
                                        >
                                            {displayedNews[idx].investment_type}
                                        </Chip>
                                    )}
                                </div>
                                <h3 className="text-3xl font-bold mb-2 text-gray-900">{displayedNews[idx]?.title || '暂无新闻'}</h3>
                                <p className="text-lg text-gray-700 whitespace-normal break-words mb-3">
                                    {displayedNews[idx]?.content || ''}
                                </p>
                                {/* AI分析内容 */}
                                {displayedNews[idx]?.analysis && (
                                    <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
                                        <div className="text-sm font-semibold text-blue-800 mb-1">AI分析</div>
                                        <p className="text-base text-blue-700 whitespace-normal break-words">
                                            {displayedNews[idx]?.analysis}
                                        </p>
                                    </div>
                                )}
                            </CardBody>
                        </Card>
                    ))}
                </div>

                {/* 中间留空给数字人 - 缩小 */}
                <div className="flex-1"></div>

                {/* 右侧新闻 - 靠右，加宽 */}
                <div className="w-2/5 flex flex-col gap-2 h-full overflow-y-auto overflow-x-hidden pr-2 no-scrollbar">
                    {rightIndices.map(idx => (
                        <Card key={idx} className={`${isCurrentlyReading(displayedNews[idx]?.id) ? 'bg-amber-100 ring-4 ring-amber-400 ring-opacity-75' : 'bg-white/80'} backdrop-blur-sm border-none shadow-none transition-all duration-300`}>
                            <CardBody className="p-3">
                                {/* 朗读指示器 */}
                                {isCurrentlyReading(displayedNews[idx]?.id) && (
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="flex h-3 w-3">
                                            <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
                                            <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                                        </span>
                                        <span className="text-green-600 font-bold text-sm">正在播报...</span>
                                    </div>
                                )}
                                {/* 实时时间戳 + 标签 */}
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    {displayedNews[idx]?.publish_time && (
                                        <Chip size="sm" color="success" variant="solid">
                                            {formatTimeAgo(displayedNews[idx]?.publish_time || '')}
                                        </Chip>
                                    )}
                                    {displayedNews[idx]?.isImportant && (
                                        <Chip size="lg" color="danger" variant="solid">重磅</Chip>
                                    )}
                                    <Chip size="lg" color="primary" variant="flat">{displayedNews[idx]?.industry || '其他'}</Chip>
                                    <Chip size="lg" color="warning" variant="flat">{displayedNews[idx]?.investment_rating || '★★'}</Chip>
                                    {displayedNews[idx]?.investment_type && (
                                        <Chip 
                                            size="lg" 
                                            color={displayedNews[idx].investment_type === '短期' ? 'success' : 'secondary'} 
                                            variant="flat"
                                        >
                                            {displayedNews[idx].investment_type}
                                        </Chip>
                                    )}
                                </div>
                                <h3 className="text-3xl font-bold mb-2 text-gray-900">{displayedNews[idx]?.title || '暂无新闻'}</h3>
                                <p className="text-lg text-gray-700 whitespace-normal break-words mb-3">
                                    {displayedNews[idx]?.content || ''}
                                </p>
                                {/* AI分析内容 */}
                                {displayedNews[idx]?.analysis && (
                                    <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
                                        <div className="text-sm font-semibold text-blue-800 mb-1">AI分析</div>
                                        <p className="text-base text-blue-700 whitespace-normal break-words">
                                            {displayedNews[idx]?.analysis}
                                        </p>
                                    </div>
                                )}
                            </CardBody>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}
