import React, { useState } from 'react';

// 👇 Типы для пайплайна
interface PipelineRequest {
  prompt: string;
  pipeline_type: 'text_to_image' | 'full_pipeline' | 'character';
  aspect_ratio: string;
  style_preset?: string;
}

interface GenerationStep {
  step: string;
  status: string;
  model?: string;
  result_url?: string;
}

interface PipelineResult {
  image_url?: string;
  video_url?: string;
  character_url?: string;
  type: string;
  source?: string;
}

interface PipelineStatus {
  pipeline_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  steps: GenerationStep[];
  final_result?: PipelineResult;
  error?: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [pipelineType, setPipelineType] = useState<'text_to_image' | 'full_pipeline' | 'character'>('full_pipeline');
  const [aspectRatio, setAspectRatio] = useState('1:1');
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 👇 ПОЛНЫЙ ПАЙПЛАЙН - главная функция
  const startFullPipeline = async () => {
  setIsGenerating(true);
  setError(null);
  setStatus(null);

  try {
    console.log('🚀 Starting REAL AI generation...');
    
    const response = await fetch('http://localhost:8000/api/v1/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt.trim(),
        pipeline_type: 'full_pipeline'
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Generation started:', data);
    
    // 👇 Отслеживаем реальный прогресс
    pollRealStatus(data.job_id);
    
  } catch (err) {
    console.error('❌ Error:', err);
    setError('Failed to start generation. Make sure backend is running with real API keys.');
    setIsGenerating(false);
  }
};

const pollRealStatus = async (pipelineId: string) => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/status/${pipelineId}`);
    
    if (response.ok) {
      const statusData = await response.json();
      
      // 👇 Обновляем реальный прогресс
      setStatus(statusData);
      
      if (statusData.status === 'completed') {
        console.log('🎉 Real AI generation completed!');
        setIsGenerating(false);
        
        // 👇 Показываем РЕАЛЬНЫЕ результаты от Higgsfield
        if (statusData.final_result) {
          setStatus(statusData.final_result);
        }
      } else if (statusData.status === 'failed') {
        setError(statusData.error || 'Real AI generation failed');
        setIsGenerating(false);
      } else {
        // Продолжаем опрос
        setTimeout(() => pollRealStatus(pipelineId), 3000);
      }
    }
  } catch (err) {
    console.error('Status check error:', err);
    setTimeout(() => pollRealStatus(pipelineId), 3000);
  }
};
//   const startFullPipeline = async () => {
//     setIsGenerating(true);
//     setError(null);
//     setStatus(null);

//     try {
//       console.log('🚀 Запуск полного пайплайна...');
      
//       // 👇 ШАГ 1: Отправляем запрос на бэкенд
//       const response = await fetch('http://localhost:8000/api/v1/generate', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           prompt: prompt.trim(),
//           pipeline_type: pipelineType,
//           aspect_ratio: aspectRatio,
//           style_preset: 'cinematic' // 👈 можно добавить motion effect
//         } as PipelineRequest),
//       });

//       console.log('📨 Ответ от бэкенда:', response.status);
      
//       if (!response.ok) {
//         const errorText = await response.text();
//         throw new Error(`Ошибка бэкенда: ${response.status} - ${errorText}`);
//       }

//       const data = await response.json();
//       console.log('✅ Пайплайн запущен:', data);
      
//       // 👇 ШАГ 2: Начинаем отслеживать статус
//       pollPipelineStatus(data.job_id);
      
//     } catch (err) {
//       console.error('❌ Ошибка запуска пайплайна:', err);
//       setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
//       setIsGenerating(false);
//     }
//   };

//   // 👇 Функция отслеживания статуса пайплайна
//   const pollPipelineStatus = async (pipelineId: string) => {
//     try {
//       console.log(`🔄 Проверка статуса пайплайна: ${pipelineId}`);
      
//       const response = await fetch(`http://localhost:8000/api/v1/status/${pipelineId}`);
      
//       if (!response.ok) {
//         throw new Error('Не удалось проверить статус');
//       }

//       const statusData: PipelineStatus = await response.json();
//       console.log('📊 Статус пайплайна:', statusData.status);
      
//       // Обновляем состояние
//       setStatus(statusData);
      
//       // 👇 Если еще не завершено, продолжаем опрос
//       if (statusData.status === 'processing' || statusData.status === 'queued') {
//         setTimeout(() => pollPipelineStatus(pipelineId), 3000); // Опрос каждые 3 секунды
//       } else if (statusData.status === 'completed') {
//         setIsGenerating(false);
//         console.log('🎉 Пайплайн завершен!');
//       } else if (statusData.status === 'failed') {
//         setIsGenerating(false);
//         setError(statusData.error || 'Пайплайн завершился ошибкой');
//       }
      
//     } catch (err) {
//       console.error('❌ Ошибка проверки статуса:', err);
//       // Продолжаем опрос даже при ошибке
//       setTimeout(() => pollPipelineStatus(pipelineId), 3000);
//     }
//   };

  // 👇 Рендеринг шагов пайплайна
  const renderPipelineSteps = () => {
    if (!status?.steps.length) return null;

    return (
      <div className="mt-6 bg-blue-50 rounded-lg p-4">
        <h3 className="font-semibold text-blue-800 mb-3">📋 Ход выполнения:</h3>
        <div className="space-y-3">
          {status.steps.map((step, index) => (
            <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 ${
                  step.status === 'completed' ? 'bg-green-500' : 
                  step.status === 'processing' ? 'bg-yellow-500 animate-pulse' : 
                  'bg-gray-300'
                }`} />
                <div>
                  <span className="font-medium capitalize">
                    {step.step.replace(/_/g, ' ')}
                  </span>
                  {step.model && (
                    <span className="text-sm text-gray-500 ml-2">({step.model})</span>
                  )}
                </div>
              </div>
              <span className={`text-sm px-2 py-1 rounded ${
                step.status === 'completed' ? 'bg-green-100 text-green-800' :
                step.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {step.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // 👇 Рендеринг результатов
  const renderPipelineResults = () => {
    if (!status?.final_result) return null;

    const { final_result } = status;

    return (
      <div className="mt-6 bg-green-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-green-800 mb-4">
          🎉 Генерация завершена!
        </h3>
        
        {/* Результаты в зависимости от типа пайплайна */}
        {final_result.type === 'image' && final_result.image_url && (
          <div>
            <h4 className="font-medium mb-2">🖼️ Сгенерированное изображение:</h4>
            <img 
              src={final_result.image_url} 
              alt="Generated content" 
              className="max-w-full h-auto rounded-lg shadow-md"
            />
            <p className="text-sm text-gray-600 mt-2">
              Модель: {final_result.source || 'Higgsfield Soul'}
            </p>
          </div>
        )}

        {final_result.type === 'video' && final_result.video_url && (
          <div>
            <h4 className="font-medium mb-2">🎥 Сгенерированное видео:</h4>
            <div className="grid md:grid-cols-2 gap-6">
              {final_result.image_url && (
                <div>
                  <p className="text-sm mb-2">Исходное изображение:</p>
                  <img 
                    src={final_result.image_url} 
                    alt="Source" 
                    className="w-full rounded shadow"
                  />
                </div>
              )}
              <div>
                <p className="text-sm mb-2">Результат:</p>
                <video 
                  src={final_result.video_url} 
                  controls 
                  className="w-full rounded shadow"
                >
                  Ваш браузер не поддерживает видео.
                </video>
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Модели: {final_result.source || 'Higgsfield Soul + DoP'}
            </p>
          </div>
        )}

        {final_result.type === 'character' && final_result.character_url && (
          <div>
            <h4 className="font-medium mb-2">👤 Сгенерированный персонаж:</h4>
            <img 
              src={final_result.character_url} 
              alt="Generated character" 
              className="max-w-full h-auto rounded-lg shadow-md"
            />
            <p className="text-sm text-gray-600 mt-2">
              Модель: {final_result.source || 'Higgsfield Soul ID'}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-2">
          🎨 AI Content Generator
        </h1>
        <p className="text-gray-600 text-center mb-8">
          Полный пайплайн генерации: Текст → Изображение → Видео
        </p>

        {/* 👇 ФОРМА ДЛЯ ПОЛНОГО ПАЙПЛАЙНА */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Левая колонка - настройки */}
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  📝 Описание сцены:
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Опишите что хотите создать... 
Например: 'Красивый закат над горами в кинематографичном стиле'"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  🎯 Тип пайплайна:
                </label>
                <select
                  value={pipelineType}
                  onChange={(e) => setPipelineType(e.target.value as any)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="full_pipeline">🎬 Полный пайплайн (Текст → Изображение → Видео)</option>
                  <option value="text_to_image">🖼️ Только изображение</option>
                  <option value="character">👤 Создание персонажа</option>
                </select>
              </div>
            </div>

            {/* Правая колонка - доп настройки */}
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  📐 Соотношение сторон:
                </label>
                <select
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="1:1">Квадрат (1:1)</option>
                  <option value="16:9">Горизонтальное (16:9)</option>
                  <option value="9:16">Вертикальное (9:16)</option>
                  <option value="4:3">Классическое (4:3)</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ⚡ Дополнительные настройки:
                </label>
                <input
                  type="text"
                  placeholder="Motion effect (опционально)..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => {/* можно добавить обработку motion effects */}}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Например: zoom_in, pan_left, cinematic
                </p>
              </div>
            </div>
          </div>

          {/* Кнопка запуска */}
          <button
            onClick={startFullPipeline}
            disabled={isGenerating || !prompt.trim()}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium text-lg mt-4"
          >
            {isGenerating ? (
              <span className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                Генерируем контент...
              </span>
            ) : (
              '🚀 Запустить полный пайплайн'
            )}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700 font-medium">❌ Ошибка: {error}</p>
            </div>
          )}
        </div>

        {/* 👇 ОТОБРАЖЕНИЕ ПРОГРЕССА ПАЙПЛАЙНА */}
        {isGenerating && renderPipelineSteps()}

        {/* 👇 РЕЗУЛЬТАТЫ ПАЙПЛАЙНА */}
        {status?.status === 'completed' && renderPipelineResults()}

        {/* 👇 ИНФОРМАЦИЯ О ПАЙПЛАЙНЕ */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-6">
          <h3 className="font-semibold text-yellow-800 mb-2">ℹ️ О пайплайне:</h3>
          <ul className="text-yellow-700 text-sm list-disc list-inside space-y-1">
            <li><strong>Полный пайплайн:</strong> Текст → Изображение (Soul) → Видео (DoP)</li>
            <li><strong>Только изображение:</strong> Текст → Изображение (Soul)</li>
            <li><strong>Персонаж:</strong> Текст → Персонаж (Soul ID)</li>
            <li>Время генерации: 2-5 минут</li>
            <li>Используются реальные AI модели Higgsfield</li>
          </ul>
        </div>
      </div>
    </div>
  );
}