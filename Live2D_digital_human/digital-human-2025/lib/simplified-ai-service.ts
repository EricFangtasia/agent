/**
 * 简化版AI服务实现
 * 用于无Dify版本的数字人，不依赖外部API
 */

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export class SimplifiedAIService {
  private static instance: SimplifiedAIService;
  private apiKey: string | null = null;
  private isConnected: boolean = false;

  private constructor() {}

  public static getInstance(): SimplifiedAIService {
    if (!SimplifiedAIService.instance) {
      SimplifiedAIService.instance = new SimplifiedAIService();
    }
    return SimplifiedAIService.instance;
  }

  /**
   * 连接到AI服务
   */
  async connect(apiKey?: string): Promise<boolean> {
    try {
      // 如果提供了API密钥，验证它
      if (apiKey) {
        this.apiKey = apiKey;
        
        // 验证API密钥格式（简单验证）
        if (!this.isValidApiKey(apiKey)) {
          throw new Error('无效的API密钥格式');
        }
        
        // 模拟API连接验证
        await this.validateConnection(apiKey);
      }
      
      this.isConnected = true;
      return true;
    } catch (error) {
      console.error('连接AI服务失败:', error);
      this.isConnected = false;
      throw error;
    }
  }

  /**
   * 验证API密钥格式
   */
  private isValidApiKey(key: string): boolean {
    // 这里可以根据实际API密钥格式进行验证
    // 例如，对于OpenAI API密钥，通常以"sk-"开头
    // 对于其他服务，需要相应调整验证逻辑
    return key.trim().length > 0;
  }

  /**
   * 验证连接
   */
  private async validateConnection(apiKey: string): Promise<void> {
    // 模拟API调用验证
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        // 模拟API验证成功
        if (Math.random() > 0.1) { // 90%的成功率
          resolve();
        } else {
          reject(new Error('API密钥验证失败'));
        }
      }, 1000);
    });
  }

  /**
   * 发送消息并获取回复
   */
  async sendMessage(messages: Message[]): Promise<string> {
    if (!this.isConnected) {
      throw new Error('尚未连接到AI服务，请先连接');
    }

    // 获取最后一条用户消息
    const lastUserMessage = [...messages].reverse().find(msg => msg.role === 'user');
    
    if (!lastUserMessage) {
      throw new Error('没有找到用户消息');
    }

    // 生成模拟回复
    const response = this.generateResponse(lastUserMessage.content, messages);
    
    return new Promise((resolve) => {
      // 模拟网络延迟
      setTimeout(() => {
        resolve(response);
      }, 800 + Math.random() * 700); // 800ms到1.5s之间的随机延迟
    });
  }

  /**
   * 生成AI回复
   */
  private generateResponse(userInput: string, conversationHistory: Message[]): string {
    const lowerInput = userInput.toLowerCase();
    
    // 根据输入内容生成相应的回复
    if (lowerInput.includes('你好') || lowerInput.includes('您好') || lowerInput.includes('hello')) {
      return '你好！我是你的数字助手，很高兴认识你。今天过得怎么样？';
    } else if (lowerInput.includes('名字') || lowerInput.includes('称呼') || lowerInput.includes('叫什么')) {
      return '我是小艾，你的专属数字助手。你可以问我任何问题，我会尽力帮助你！';
    } else if (lowerInput.includes('天气')) {
      return '我目前无法获取实时天气信息，但建议您可以查看手机上的天气应用，那里有最准确的数据。';
    } else if (lowerInput.includes('帮助')) {
      return '我可以陪你聊天、解答问题、讲笑话，或者只是倾听你的想法。有什么想和我分享的吗？';
    } else if (lowerInput.includes('再见') || lowerInput.includes('拜拜') || lowerInput.includes('bye')) {
      return '再见！很高兴和你聊天，希望很快能再见到你！';
    } else if (lowerInput.includes('谢谢') || lowerInput.includes('感谢')) {
      return '不客气！能帮到你我很开心。还有其他我可以帮忙的吗？';
    } else if (lowerInput.includes('时间')) {
      const now = new Date();
      return `现在是${now.getHours()}点${now.getMinutes()}分。时间过得真快，珍惜每一刻吧！`;
    } else if (lowerInput.includes('心情') || lowerInput.includes('感觉')) {
      return '我一直都很开心能和你聊天！你呢？今天心情怎么样？';
    } else {
      // 根据对话历史生成更个性化的回复
      const assistantMessages = conversationHistory.filter(msg => msg.role === 'assistant');
      
      if (assistantMessages.length === 0) {
        // 第次回复
        return '这很有趣！你能详细说说吗？我对你的想法很感兴趣。';
      } else if (assistantMessages.length < 3) {
        // 中期对话
        return '我明白了，这确实是个值得思考的问题。你对此有什么特别的看法吗？';
      } else {
        // 深入对话
        return '和你聊天真愉快！你总能提出有意思的观点。还有其他想聊的吗？';
      }
    }
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.isConnected = false;
    this.apiKey = null;
  }

  /**
   * 检查是否已连接
   */
  isConnectedToService(): boolean {
    return this.isConnected;
  }

  /**
   * 获取当前API密钥
   */
  getApiKey(): string | null {
    return this.apiKey;
  }
}