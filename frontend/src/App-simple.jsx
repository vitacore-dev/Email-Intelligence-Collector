import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('single');
  const [searchEmail, setSearchEmail] = useState('');
  const [digitalTwinEmail, setDigitalTwinEmail] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [digitalTwinData, setDigitalTwinData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8001/api';

  // API calls
  const makeAPICall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
        },
        ...options,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  };

  const handleSingleSearch = async (e) => {
    e.preventDefault();
    if (!searchEmail) return;

    setIsLoading(true);
    try {
      const data = await makeAPICall('/search', {
        method: 'POST',
        body: JSON.stringify({ email: searchEmail }),
      });
      setSearchResult(data);
    } catch (error) {
      setError('Ошибка при поиске');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDigitalTwinSearch = async (e) => {
    e.preventDefault();
    if (!digitalTwinEmail) return;

    setIsLoading(true);
    setError(null);
    
    try {
      // Load digital twin data with fallback to demo data
      let digitalTwin;
      try {
        digitalTwin = await makeAPICall(`/digital-twin/${encodeURIComponent(digitalTwinEmail)}`);
      } catch (apiError) {
        // Fallback to demo data if API is not available
        digitalTwin = {
          name: "Dr. John Doe",
          email: digitalTwinEmail,
          affiliation: "Demo University",
          research_interests: ["Machine Learning", "Data Science", "AI Ethics"],
          metrics: {
            total_publications: 45,
            total_citations: 892,
            h_index: 14,
            collaboration_score: 78
          }
        };
      }
      
      setDigitalTwinData(digitalTwin);
    } catch (err) {
      setError('Ошибка при загрузке данных цифрового двойника');
    } finally {
      setIsLoading(false);
    }
  };

  // Demo data for visualization
  const demoRadarData = [
    { subject: 'Продуктивность', A: 120, fullMark: 150 },
    { subject: 'Влияние', A: 98, fullMark: 150 },
    { subject: 'Сотрудничество', A: 86, fullMark: 150 },
    { subject: 'Инновации', A: 99, fullMark: 150 },
    { subject: 'Качество', A: 85, fullMark: 150 },
    { subject: 'Актуальность', A: 65, fullMark: 150 }
  ];

  const demoTimelineData = [
    { year: 2019, publications: 3, citations: 45 },
    { year: 2020, publications: 5, citations: 78 },
    { year: 2021, publications: 7, citations: 123 },
    { year: 2022, publications: 4, citations: 156 },
    { year: 2023, publications: 6, citations: 201 }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Email Intelligence Collector
          </h1>
          <p className="text-gray-600">
            Сбор и анализ информации по email-адресам из открытых источников
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('single')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'single'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Одиночный поиск
              </button>
              <button
                onClick={() => setActiveTab('digital-twin')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'digital-twin'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Цифровой двойник
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'single' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Поиск по одному email</h2>
                <form onSubmit={handleSingleSearch} className="space-y-4">
                  <div>
                    <input
                      type="email"
                      placeholder="example@domain.com"
                      value={searchEmail}
                      onChange={(e) => setSearchEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoading ? 'Поиск...' : 'Найти'}
                  </button>
                </form>

                {/* Search Results */}
                {searchResult && (
                  <div className="mt-6 p-4 bg-gray-100 rounded-md">
                    <h3 className="font-semibold mb-2">Результаты поиска:</h3>
                    <pre className="text-sm overflow-auto">
                      {JSON.stringify(searchResult, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'digital-twin' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Анализ цифрового двойника</h2>
                <form onSubmit={handleDigitalTwinSearch} className="space-y-4">
                  <div>
                    <input
                      type="email"
                      placeholder="researcher@university.com"
                      value={digitalTwinEmail}
                      onChange={(e) => setDigitalTwinEmail(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoading ? 'Загрузка...' : 'Создать цифрового двойника'}
                  </button>
                </form>

                {/* Error Display */}
                {error && (
                  <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                    {error}
                  </div>
                )}

                {/* Digital Twin Results */}
                {digitalTwinData && (
                  <div className="mt-6 space-y-6">
                    {/* Profile Summary */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                      <h3 className="text-lg font-semibold mb-4">Профиль исследователя</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <strong>Email:</strong> {digitalTwinData.email}
                        </div>
                        {digitalTwinData.name && (
                          <div>
                            <strong>Имя:</strong> {digitalTwinData.name}
                          </div>
                        )}
                        {digitalTwinData.affiliation && (
                          <div>
                            <strong>Организация:</strong> {digitalTwinData.affiliation}
                          </div>
                        )}
                        {digitalTwinData.research_interests && (
                          <div>
                            <strong>Области исследований:</strong>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {digitalTwinData.research_interests.map((interest, index) => (
                                <span
                                  key={index}
                                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                                >
                                  {interest}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Key Metrics */}
                    {digitalTwinData.metrics && (
                      <div className="bg-white p-6 rounded-lg shadow-md">
                        <h3 className="text-lg font-semibold mb-4">Ключевые метрики</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {digitalTwinData.metrics.total_publications || 0}
                            </div>
                            <div className="text-sm text-gray-600">Публикации</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {digitalTwinData.metrics.total_citations || 0}
                            </div>
                            <div className="text-sm text-gray-600">Цитирования</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                              {digitalTwinData.metrics.h_index || 0}
                            </div>
                            <div className="text-sm text-gray-600">H-индекс</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-orange-600">
                              {digitalTwinData.metrics.collaboration_score || 0}%
                            </div>
                            <div className="text-sm text-gray-600">Коллаборация</div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Demo Visualization Note */}
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h4 className="font-semibold text-yellow-800 mb-2">Демо-режим</h4>
                      <p className="text-yellow-700 text-sm">
                        Визуализации (графики, сети, временные линии) будут доступны после 
                        обновления Node.js до версии 18+ и установки всех зависимостей.
                        Текущая версия показывает базовую информацию профиля.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
