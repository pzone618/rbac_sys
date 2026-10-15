# TTS 选型清单

核对日期：2026-10-15。适用范围是网站指定文本朗读与音频生成，不声称穷尽全部产品。下面的优先级是工程判断，不是跨引擎音质评测。机器可读完整列表位于 [catalog.json](../../../catalog.json)，每项含官方来源与接入状态。

## 优先选择

| 场景 | 优先试用 | 选择理由与边界 |
|---|---|---|
| 即刻给网站加朗读 | 浏览器 Web Speech API | 无需下载模型；声音由设备决定；没有标准音频导出接口 |
| 本机无模型导出 | Windows SAPI | 已安装系统语音可直接生成 WAV；桌面音色不代表浏览器或云端音色 |
| CPU 离线中英文 | sherpa-onnx + Kokoro/Matcha/VITS | 可固定模型与声音，便于本地部署；先试听具体 checkpoint |
| 浏览器神经 TTS | sherpa WASM 或 kokoro-js | 要下载和缓存模型、WASM、词典；在 Worker 运行；移动端单独测内存 |
| 本地中文表现力 | Qwen3-TTS、CosyVoice | 适合进一步做独立本地推理服务；先评估硬件与部署成本 |
| 多语网站与企业集成 | Azure、Google Cloud TTS、Polly | 按现有云平台、目标地区与音色选择 |
| 表现力与内容配音 | ElevenLabs、MiniMax、OpenAI Speech、Gemini TTS | 用真实业务文本试听；不能由宣传推断中文效果或延迟 |
| 中国大陆用户访问 | 百炼 Qwen/CosyVoice、豆包、腾讯、讯飞 | 从实际服务器到供应商测延迟，核对地域、账号和配额 |
| 交互低延迟 | Cartesia、豆包及其他支持流式的引擎 | 模型支持流式不等于当前适配器已实现流式；首包与持续播放都要测 |
| 固定讲解与教学句子 | 任一合适引擎预生成音频 | 音频随网站发布；断网播放与断网生成是两项能力 |

## 离线：值得保留的 15 项

1. **系统语音**：Windows SAPI、macOS/Android 本机语音，适合快速接入。现已实现 Windows SAPI 与 macOS say 文件生成，macOS仍需目标设备验证。[Windows API](https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis.speechsynthesizer)
2. **Web Speech API 本机语音**：设备依赖明显；`localService` 筛选后仍要断网测试。[MDN](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/localService)
3. **sherpa-onnx**：推理运行时，支持多种模型，不是单个音色模型。[官方文档](https://k2-fsa.github.io/sherpa/onnx/tts/index.html)
4. **Kokoro / kokoro-js**：轻量神经语音，可选本地、WASM、WebGPU；Python 和 JS 版本的模型/语言支持不能直接等同。[官方仓库](https://github.com/hexgrad/kokoro)
5. **Piper**：CPU/边缘设备候选。当前 upstream 是 `OHF-Voice/piper1-gpl`；旧版 rhasspy 文档不可直接用于新版本。引擎 GPL，音色模型另查。[当前仓库](https://github.com/OHF-Voice/piper1-gpl)
6. **Qwen3-TTS**：固定音色、声音设计、参考音频等能力取决于具体模型；不要用一个配置代表所有变体。[官方仓库](https://github.com/QwenLM/Qwen3-TTS)
7. **CosyVoice**：中文、多语、参考音频和服务化候选，版本与部署接口决定实际能力。[官方仓库](https://github.com/FunAudioLLM/CosyVoice)
8. **MeloTTS**：传统多语 TTS 与 CPU 基线，适合不需要复杂表现力的场景。[官方仓库](https://github.com/myshell-ai/MeloTTS)
9. **GPT-SoVITS**：适合定制音色及少样本工作流，整合与模型管理比普通朗读复杂。[官方仓库](https://github.com/RVC-Boss/GPT-SoVITS)
10. **Chatterbox**：多语与表现力候选，按实际模型/语言包试用。[官方仓库](https://github.com/resemble-ai/chatterbox)
11. **F5-TTS**：研究及参考音色实验候选；官方预训练模型含非商用限制，不能因代码许可宽松就默认商用可用。[官方说明](https://github.com/SWivid/F5-TTS)
12. **Fish Speech**：表现力和本地服务候选，当前仓库含专门研究许可，需核对具体版本及模型条款。[官方仓库](https://github.com/fishaudio/fish-speech)
13. **OpenVoice**：重点是音色转换/克隆，通常与基础 TTS 联用。[官方仓库](https://github.com/myshell-ai/OpenVoice)
14. **VibeVoice**：长语音、多说话人研究候选；先确认目标 TTS 模型与代码仍可获取，不把 ASR 能力当作 TTS。[官方仓库](https://github.com/microsoft/VibeVoice)
15. **eSpeak NG**：资源占用低，适合故障兜底或音素处理，音色机械。[官方仓库](https://github.com/espeak-ng/espeak-ng)

## 在线：值得保留的 15 项

| 服务 | 适合场景 | 来源 |
|---|---|---|
| Azure AI Speech | 多语、SSML、企业网站；已实现文件生成 | [REST](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech) |
| ElevenLabs | 内容配音、音色选择；已实现 MP3 生成 | [API](https://elevenlabs.io/docs/api-reference/text-to-speech/convert) |
| OpenAI Speech API | 自然语言指令控制与已有 OpenAI 应用；通过可配置 Speech API 接入 | [指南](https://developers.openai.com/api/docs/guides/text-to-speech) |
| Google Cloud TTS | Google Cloud 项目、多语与 Chirp 等音色系列 | [文档](https://docs.cloud.google.com/text-to-speech/docs) |
| Gemini TTS | 指令驱动、单人/多人语音制作；与 Cloud TTS、Live API 区分 | [文档](https://ai.google.dev/gemini-api/docs/speech-generation) |
| Amazon Polly | AWS 项目；按音色匹配标准、神经、生成式或长语音引擎 | [引擎说明](https://docs.aws.amazon.com/polly/latest/dg/voice-engines-polly.html) |
| 阿里云百炼 Qwen TTS / CosyVoice | 中文与阿里云生态；本地 Qwen3 SDK 不是此云端 API | [文档](https://help.aliyun.com/zh/model-studio/speech-synthesis-api-reference/) |
| 火山引擎豆包语音 | 中文交互、流式与异步长文本 | [长文本 API](https://docs.volcengine.com/docs/DoubaoVoice/Tasksubmission?lang=zh) |
| MiniMax Speech | 多语内容配音、流式语音 | [API](https://platform.minimax.io/docs/api-reference/speech-t2a-websocket) |
| 腾讯云 TTS | 中英混读、腾讯云项目 | [API](https://cloud.tencent.com/document/api/1073/37995) |
| 讯飞 TTS | 中文与已有讯飞系统 | [API](https://www.xfyun.cn/doc/tts/online_tts/API.html) |
| Cartesia Sonic | 低延迟语音交互 | [文档](https://docs.cartesia.ai/2025-04-16/get-started/overview) |
| Resemble AI | 托管配音和定制音色 | [产品](https://www.resemble.ai/products/text-to-speech) |

## 接入状态与选择方法

实现代码不代表当前机器已配置：Windows SAPI 已有本机音色；sherpa 需要 Python 包和模型；云端需要账号、凭据和可用模型。除明确实现的适配器外，清单均为候选，接入时查当前官方文档。

用同一批中文、英文、混读、数字日期、长句与短提示语试听；记录模型版本、音色、输出格式、首音频延迟、整段耗时、失败率与实际成本。不要把供应商 benchmark 当成本机测量。价格和模型可用性变化较快，本清单不固定价格或承诺模型生命周期。

Context7 原始查询保存在插件 `research/`，用于追溯；其中 Piper 命中旧仓库，阿里云查询误命中本地 Qwen，Polly/Web Speech 查询未取得有效结果。这些项以随后核对的官方链接为准，不能把搜索命中视为已核实 API。引擎代码、模型权重、音色和生成内容使用条款分别核对。

## 0.2.0 接入更新

- **Edge TTS**：新增MP3、音色查询、代理与超时。使用实测7.3.1；7.2.8在本次网络返回403，升级后成功。网络可用性仍需部署环境验证。[项目](https://github.com/rany2/edge-tts)
- **有道词典发音**：新增免密钥HTTPS英文词/短语MP3，非任意文本TTS。明确US/UK，失败不切换其他引擎。真实 good morning 返回并解码成功。
- **百炼 Qwen-TTS**：北京/新加坡非实时WAV适配器，600字符上限；付费凭据尚未联网验证。CosyVoice/Qwen-Audio-TTS仍是不同接口的候选。
- **macOS say**：新增本机WAV和音色查询；sherpa为Linux/Mac可选离线运行时，模型需自行准备。
- 本版不提供自动回退；需回退时由调用方明确选择并遵守在线/离线策略。
