import { Message } from './store';

/**
 * 火山引擎API客户端
 */
export class VolcEngineClient {
  private baseURL: string = 'https://ark.cn-beijing.volces.com/api/v3';
  private apiKey: string;
  private model: string;

  constructor(apiKey: string, model?: string) {
    this.apiKey = apiKey;
    // 使用用户提供的模型ID
    this.model = model || 'doubao-seed-1-8-251228';
  }

  /**
   * 发送文本消息到火山引擎LLM
   */
  async sendMessage(messages: Omit<Message, 'id' | 'timestamp' | 'audioUrl'>[]): Promise<string> {
    try {
      // 将消息转换为火山引擎API所需的格式
      const input = messages.map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: [
          {
            type: 'input_text',
            text: msg.content
          }
        ]
      }));

      const response = await fetch(`${this.baseURL}/responses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: JSON.stringify({
          model: this.model,
          input: input,
        }),
      });

      if (!response.ok) {
        throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // 解析响应，根据实际API响应结构调整
      if (data && data.choices && data.choices[0] && data.choices[0].message) {
        return data.choices[0].message.content || '抱歉，我没有理解你说的。';
      } else if (data && data.response) {
        // 如果响应格式不同，尝试另一种解析方式
        return data.response || '抱歉，我没有理解你说的。';
      } else {
        // 尝试从content字段获取响应
        return data.content || JSON.stringify(data) || '抱歉，我没有理解你说的。';
      }
    } catch (error) {
      console.error('火山引擎API调用失败:', error);
      throw new Error(`API调用失败: ${(error as Error).message}`);
    }
  }

  /**
   * 检查API密钥是否有效
   */
  async validateApiKey(): Promise<boolean> {
    try {
      // 发送一个简单的测试请求来验证API密钥
      const testResponse = await fetch(`${this.baseURL}/models`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      });

      return testResponse.ok;
    } catch (error) {
      console.error('API密钥验证失败:', error);
      return false;
    }
  }
}