# UI Easy 配置指南

## 概述

UI Easy 配置页面允许您管理AI模型、分析模块和应用设置。首次运行应用时，会自动创建默认配置文件 `config.json`。

## 配置页面功能

### 1. 模型配置 (Model Configuration)

在此区域您可以：

- **添加新模型**：点击"添加模型"按钮创建新的AI模型配置
- **选择模型**：从下拉列表中选择要编辑的模型
- **编辑配置**：修改模型的详细参数
- **删除模型**：删除不再需要的模型配置

#### 模型参数说明：

- **模型名称**：用于标识模型的友好名称
- **提供商**：AI服务提供商（openai, deepseek, anthropic）
- **API 密钥**：您的API密钥（必填）
- **基础 URL**：API的基础URL（某些提供商需要）
- **模型 ID**：具体的模型标识符（如：gpt-4-turbo-preview）
- **最大令牌数**：单次请求的最大令牌数
- **温度**：控制输出随机性（0.0-2.0）
- **超时**：请求超时时间（秒）

### 2. 模块配置 (Module Configuration)

配置各个分析模块：

- **图像分析器 (image_analyzer)**：用于分析设计图像
- **需求分析器 (requirement_analyzer)**：用于处理需求文档

#### 模块设置：

- **启用模块**：开启/关闭模块功能
- **使用模型**：选择该模块使用的AI模型
- **自定义提示词**：为模块定制特殊的提示词（可选）

### 3. 应用设置 (Application Settings)

- **界面语言**：选择界面显示语言
- **默认分析类型**：设置图像分析的默认类型
- **自动保存结果**：是否自动保存分析结果
- **默认导出格式**：选择默认的导出文件格式

## 快速开始

### 第一次使用

1. **启动应用**：运行 `python main.py`
2. **进入设置页面**：点击"Settings"标签页
3. **配置API密钥**：
   - 选择一个预设模型（如 gpt4 或 deepseek）
   - 填入您的API密钥
   - 点击"更新模型配置"
4. **测试配置**：点击"测试配置"按钮验证设置
5. **保存设置**：点击"保存设置"保存您的配置

### 常见配置示例

#### OpenAI GPT-4 配置：
```
模型名称: GPT-4
提供商: openai
API 密钥: sk-your-openai-key-here
模型 ID: gpt-4-turbo-preview
```

#### DeepSeek 配置：
```
模型名称: DeepSeek Chat
提供商: deepseek
API 密钥: your-deepseek-key-here
基础 URL: https://api.deepseek.com/v1
模型 ID: deepseek-chat
```

## 故障排除

### 常见问题

1. **"缺少 API 密钥" 错误**
   - 确保您已填入正确的API密钥
   - 检查密钥是否有效且有足够额度

2. **"模型配置无效" 错误**
   - 检查模型 ID 是否正确
   - 对于DeepSeek等服务，确保填入了基础 URL

3. **"测试配置失败"**
   - 检查网络连接
   - 验证API密钥和端点设置
   - 确认所选模型服务可用

### 配置文件位置

- **主配置文件**：`config.json`（应用根目录）
- **模板文件**：`config_template.json`（参考用）

### 手动编辑配置

您也可以直接编辑 `config.json` 文件：

```json
{
  "models": {
    "my_model": {
      "name": "My Custom Model",
      "provider": "openai",
      "api_key": "your-key-here",
      "model_id": "gpt-4"
    }
  }
}
```

## 安全提示

- **保护API密钥**：不要将包含真实API密钥的配置文件提交到版本控制
- **定期更新**：定期检查和更新您的API密钥
- **备份配置**：在重要配置完成后备份 `config.json` 文件

## 获取帮助

如果您遇到配置问题：

1. 查看控制台输出的错误信息
2. 使用"测试配置"功能诊断问题
3. 参考 API 服务商的官方文档
4. 检查 `config_template.json` 作为配置参考 