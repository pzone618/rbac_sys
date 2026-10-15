# TTS Studio 0.2.0

面向 macOS 开发、Linux 部署的网站朗读与音频生成插件。包含跨平台 Python MCP、浏览器朗读模块、15项离线/15项在线选型清单，以及个人 marketplace 安装助手。无需把 artifacts 复制进每个工程。

- [安装、配置与跨项目使用](skills/website-tts/references/runtime.md)
- [引擎选型](skills/website-tts/references/engines.md)
- [验证记录](VERIFICATION.md)
- [浏览器示例](skills/website-tts/assets/reader-example.html)

新增 Edge TTS、有道词典发音、百炼 Qwen-TTS、macOS say。保留 sherpa、Windows、Azure、ElevenLabs 和可配置 Speech API。提供 doctor、catalog、voices、synthesize、synthesize_batch 五个工具。MP3 实际解码验证，长文本分段、播放清单、缓存复用与失败续做；不静默切换供应商。

```bash
python3 -m pip install -r requirements.txt
python3 server/tts_server.py doctor
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/browser.test.mjs
```

发布到账户不代表本机已安装或工具已加载。Mac/Linux 默认 python3，推荐按安装说明绑定自己的虚拟环境；模型与付费云端凭据不随包提供。Mac原生语音、离线神经推理和付费云端请求的验证范围见记录。此版仍不提供实时MCP音频流、逐词高亮、声音克隆工具或单文件长音频拼接。
