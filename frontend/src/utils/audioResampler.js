/**
 * 音频重采样器 - 将浏览器麦克风输入（44.1/48kHz）下采样至 16kHz
 */
export class AudioResampler {
  constructor(targetSampleRate = 16000) {
    this.targetSampleRate = targetSampleRate;
    this.audioContext = null;
    this.mediaStream = null;
    this.scriptProcessor = null;
    this.sourceNode = null;
  }

  async init() {
    try {
      // 获取麦克风权限
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      // 创建音频上下文
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);

      // 创建脚本处理器
      const bufferSize = 4096;
      this.scriptProcessor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);

      return true;
    } catch (error) {
      console.error('初始化音频失败:', error);
      return false;
    }
  }

  start(onAudioData) {
    if (!this.scriptProcessor || !this.sourceNode) {
      console.error('音频未初始化');
      return;
    }

    const sourceSampleRate = this.audioContext.sampleRate;
    const targetSampleRate = this.targetSampleRate;
    const ratio = sourceSampleRate / targetSampleRate;

    this.scriptProcessor.onaudioprocess = (event) => {
      const inputData = event.inputBuffer.getChannelData(0);
      
      // 下采样
      const resampledLength = Math.floor(inputData.length / ratio);
      const resampledData = new Float32Array(resampledLength);

      for (let i = 0; i < resampledLength; i++) {
        const sourceIndex = Math.floor(i * ratio);
        resampledData[i] = inputData[sourceIndex];
      }

      // 转换为 Int16Array (PCM 16-bit)
      const pcmData = new Int16Array(resampledData.length);
      for (let i = 0; i < resampledData.length; i++) {
        const s = Math.max(-1, Math.min(1, resampledData[i]));
        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      // 发送音频数据
      if (onAudioData) {
        onAudioData(pcmData.buffer);
      }
    };

    this.sourceNode.connect(this.scriptProcessor);
    this.scriptProcessor.connect(this.audioContext.destination);
  }

  stop() {
    if (this.scriptProcessor) {
      this.scriptProcessor.disconnect();
      this.scriptProcessor.onaudioprocess = null;
    }

    if (this.sourceNode) {
      this.sourceNode.disconnect();
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
    }

    if (this.audioContext) {
      this.audioContext.close();
    }
  }
}
