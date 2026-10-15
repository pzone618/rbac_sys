# 安装、运行与跨项目复用

TTS Studio 0.2.0 面向 macOS 开发与 Linux 部署，保留 Windows 适配器。Python 3.10+；标准库实现 MCP，Edge 客户端与 MP3 解码器单独安装。插件不是公开网站的后端服务。

## Mac / Linux 一次安装，多个工程使用

把插件 ZIP 解压到固定目录，例如 `~/dev/tts-studio`。只需要这个独立插件包，不需要复制整个 artifacts。创建个人 Python 环境：

```bash
python3 -m venv ~/.local/share/tts-studio-venv
~/.local/share/tts-studio-venv/bin/python -m pip install -r ~/dev/tts-studio/requirements.txt
~/.local/share/tts-studio-venv/bin/python ~/dev/tts-studio/scripts/prepare_local_install.py --python ~/.local/share/tts-studio-venv/bin/python
```

脚本在 `~/.local/share/tts-studio-marketplace` 准备完整插件和 marketplace，将两份 MCP 配置绑定到指定 Python 的绝对路径。不会修改宿主全局配置，也不自动安装依赖。然后在支持的本地 Codex 客户端执行：

```bash
codex plugin marketplace add "$HOME/.local/share/tts-studio-marketplace"
codex plugin add tts-studio@tts-studio-local
```

刷新或重启宿主后检查技能和五个工具是否出现。需要图形安装的宿主，在 Plugins Directory 中选择已注册的本地 marketplace 安装。安装到个人范围后可在多个工程使用；账户中的私有发布与本机安装/执行是不同步骤。目录可以自选，安装脚本支持 `--destination`。现有 marketplace 冲突时脚本停止，不覆盖其他目录的登记。

Portable MCP 默认命令为 `python3`，便于 Mac/Linux；使用安装脚本绑定虚拟环境更可靠。Windows 可用实际 `python.exe` 运行同一安装脚本。宿主不支持本地 stdio 时，技能仍可调用安装目录中的绝对路径 CLI；网页或手机宿主不能直接启动你的本机进程。

## 五个工具与 CLI

`tts_doctor`、`tts_catalog`、`tts_voices`、`tts_synthesize`、`tts_synthesize_batch`。CLI 不默认选择 Windows，合成必须显式指定 provider。

```bash
python3 server/tts_server.py doctor
python3 server/tts_server.py voices --provider youdao
python3 server/tts_server.py synthesize --provider youdao --voice en-US --text 'good morning' --format mp3 --allow-online
python3 server/tts_server.py synthesize --provider edge --voice en-US-AriaNeural --text 'Hello, welcome.' --format mp3 --allow-online
python3 server/tts_server.py voices --provider macos
python3 server/tts_server.py synthesize --provider macos --voice Samantha --text 'Hello, welcome.'
```

示例中的 python3 必须是装有依赖的解释器。Mac 音色从本机列表选择，不假设一定存在 Samantha。Windows 可继续 `--provider windows`，Linux 原生离线使用 sherpa。

## 已实现的适配器

| provider | 能力 | 配置 |
|---|---|---|
| edge | 在线 MP3、音色列表、语速 | `TTS_EDGE_VOICE` 可选；`TTS_EDGE_PROXY` 显式代理；连接10秒、接收60秒、整次120秒 |
| youdao | 英文单词/短语返回 MP3，US/UK | voice 为 `en-US` / `en-GB`；不需密钥；最多8词、100字符；speed=1 |
| dashscope | 百炼 Qwen-TTS 非实时 WAV | `DASHSCOPE_API_KEY`、`TTS_DASHSCOPE_MODEL`、`TTS_DASHSCOPE_VOICE`；`TTS_DASHSCOPE_REGION=beijing` 或 `singapore`；可选 `TTS_DASHSCOPE_LANGUAGE`；speed=1 |
| macos | say 本机语音生成 PCM WAV | macOS 和已安装音色；语速以175词/分钟为基准近似映射 |
| sherpa | VITS/Matcha/Kokoro 本地 WAV | 安装 sherpa-onnx 和模型，设置 `TTS_SHERPA_CONFIG` |
| windows | SAPI 本机 WAV | Windows 桌面语音 |
| azure | REST WAV/MP3、音色列表 | `AZURE_SPEECH_KEY`、`AZURE_SPEECH_REGION`；可选 VOICE、LANGUAGE |
| elevenlabs | MP3、音色列表第一页 | `ELEVENLABS_API_KEY`、`ELEVENLABS_MODEL_ID`、`ELEVENLABS_VOICE_ID`；speed=1 |
| speech-api | Bearer Speech API WAV/MP3 | `TTS_SPEECH_URL`、`TTS_SPEECH_API_KEY`、`TTS_SPEECH_MODEL`、`TTS_SPEECH_VOICE` |

百炼例子可选当前账号支持的 `qwen3-tts-flash` 和 `Cherry`。本适配器只对应 Qwen-TTS 的 multimodal-generation 接口，不包含不同接口的 Qwen-Audio-TTS 或 CosyVoice。单次最多600字符，音频下载 URL 限于供应商返回的 DashScope OSS 域名并升级为 HTTPS，不向下载主机发送 API key。按地域匹配凭据。[官方接口](https://help.aliyun.com/zh/model-studio/qwen-tts-api)

Edge 为在线第三方客户端，固定到本版实测的7.3.1，远端仍可能变化。客户端自身可能做403时钟修正重试；插件不额外自动重试或切换服务，不关闭证书校验或悄悄绕过代理。有道是词典发音接口，不保证所有短语有音频，不应当作无限长文本合成；收到500等错误就报告失败。

## 音频、缓存与长文本

MP3 必须通过 ffmpeg 解码验证。可以安装系统 ffmpeg，或 requirements.txt 中的 imageio-ffmpeg；`TTS_FFMPEG` 可指定可执行文件。无解码器时在付费请求前停止。时长由归一化PCM长度计算；`decodedSampleRate=24000` 是验证解码参数，不冒充源文件采样率。WAV 校验头部及声明帧数与实际数据一致。

输出默认在工作目录的 `tts-output/`，可设 `TTS_OUTPUT_DIR` 到项目资源目录。结果返回 requestedProvider、actualProvider、fallbackReason、路径、时长、哈希与缓存命中。没有自动回退，因此 actualProvider 与请求一致。失效缓存会重新生成。修改模型或默认音色后设置新的 `TTS_CACHE_REVISION`；不自动监测模型权重变化。缓存文件可能含私人音频，按项目数据管理。

`tts_synthesize_batch` / CLI `batch` 接收最多100000字符，百炼按600、其他按2500字符以内分段，返回分段音频和 playlist JSON。尽量按句号等边界划分，极长句会硬切；不保证语言学分词。失败立即停止；重复相同请求复用成功缓存并继续。每个未缓存的云端片段都可能计费，遇到请求已计费但未获得有效输出的情况，人工决定是否重试。有道不接受段落批处理。当前不拼接单一音频、不提供实时流或MCP取消。

## sherpa 本地模型

模型包及 Python 包需另行配置，不自动下载。配置中只能引用已经存在的绝对本地路径；tokens、lexicon、phonemizer 必须来自对应模型包。

```json
{
  "model": {
    "vits": {
      "model": "/Users/me/models/selected/model.onnx",
      "tokens": "/Users/me/models/selected/tokens.txt",
      "lexicon": "/Users/me/models/selected/lexicon.txt"
    },
    "num_threads": 2,
    "provider": "cpu",
    "debug": false
  },
  "max_num_sentences": 1
}
```

这是形状示例，不是直接可运行的配置；Linux 使用相应绝对路径。VITS 可能需要 data_dir；中文模型可能需要 rule_fsts。Matcha 使用 acoustic_model/vocoder；Kokoro 使用 voices 等配置。按 [官方模型示例](https://k2-fsa.github.io/sherpa/onnx/tts/index.html)填写。speaker ID 通过 voice 字符串传入，默认0。每进程只缓存最近一个模型，配置或 TTS_CACHE_REVISION 变化时重载。doctor 检查路径与依赖，不加载模型或测性能。

## 网站集成

浏览器模块在 `skills/website-tts/assets`，通过 HTTP 运行 reader-example.html；客户端初始化、页面卸载 dispose。一个页面一个实例，避免抢占全局朗读队列。固定内容在开发/构建时生成音频并随站发布。动态合成应接入网站自己的后端，复用已有认证、限流和任务管理，不把 stdio MCP 直接公开上网。

密钥留在服务端环境变量，插件不读取 .env，不把密钥写入示例或包。默认 offline_only=true；在线显式开启。在线不等于大陆网络始终可用，目标部署机器仍需实际测网络。音频返回/可解码与主观音质是不同验证；Mac/Linux各目标环境仍需试听与断网测试。
