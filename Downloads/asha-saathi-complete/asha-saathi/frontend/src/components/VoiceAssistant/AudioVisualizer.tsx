import React, { useEffect, useRef } from 'react';

interface AudioVisualizerProps {
  isListening: boolean;
  barColor?: string;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  isListening,
  barColor = '#0d9488',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const bars = 24;
      const barWidth = canvas.width / bars - 2;

      for (let i = 0; i < bars; i++) {
        let height = 4;
        if (isListening) {
          // Dynamic simulated sine audio wave with noise oscillation
          const angle = (i / bars) * Math.PI * 4 + phase;
          const noise = Math.sin(phase * 2 + i) * 10;
          height = Math.max(6, Math.sin(angle) * 22 + 26 + noise);
        }

        const x = i * (barWidth + 2);
        const y = (canvas.height - height) / 2;

        ctx.fillStyle = isListening ? barColor : '#cbd5e1';
        ctx.beginPath();
        ctx.roundRect(x, y, barWidth, height, 4);
        ctx.fill();
      }

      phase += 0.12;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isListening, barColor]);

  return (
    <div className="w-full flex justify-center py-2">
      <canvas
        ref={canvasRef}
        width={240}
        height={60}
        className="w-60 h-14"
      />
    </div>
  );
};
