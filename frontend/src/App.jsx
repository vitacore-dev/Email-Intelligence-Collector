import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('single');
  const [darkMode, setDarkMode] = useState(false);
  
  // Single search state
  const [searchEmail, setSearchEmail] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [forceRefresh, setForceRefresh] = useState(false);
  
  // Bulk search state
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkResult, setBulkResult] = useState(null);
  
  // Stats state
  const [stats, setStats] = useState(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  
  // Digital twin state
  const [digitalTwinEmail, setDigitalTwinEmail] = useState('');
  const [digitalTwinResult, setDigitalTwinResult] = useState(null);
  
  // PDF analysis state
  const [pdfAnalysisEmail, setPdfAnalysisEmail] = useState('');
  const [pdfAnalysisResult, setPdfAnalysisResult] = useState(null);
  const [isPdfLoading, setIsPdfLoading] = useState(false);

  // Load statistics on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Stats loading error:', error);
      setStats({ error: 'Не удалось загрузить статистику' });
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleSingleSearch = async (e) => {
    e.preventDefault();
    if (!searchEmail) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: searchEmail, force_refresh: forceRefresh })
      });
      const data = await response.json();
      setSearchResult(data);
      loadStats();
    } catch (error) {
      console.error('Search error:', error);
      setSearchResult({
        status: 'error',
        message: 'Ошибка при поиске. Проверьте подключение к серверу.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleBulkSearch = async (e) => {
    e.preventDefault();
    if (!bulkFile) return;

    const formData = new FormData();
    formData.append('file', bulkFile);

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/bulk_search', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setBulkResult(data);
      loadStats();
    } catch (error) {
      console.error('Bulk search error:', error);
      setBulkResult({
        status: 'error',
        message: 'Ошибка при массовом поиске.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDigitalTwin = async (e) => {
    e.preventDefault();
    if (!digitalTwinEmail) return;

    setIsLoading(true);
    try {
      // Сначала проверяем есть ли профиль в системе
      const profileResponse = await fetch(`http://localhost:8000/api/profile/${digitalTwinEmail}`);
      
      if (!profileResponse.ok) {
        setDigitalTwinResult({
          status: 'error',
          message: 'Email не найден в системе. Сначала выполните поиск по этому email.'
        });
        return;
      }

      const profileData = await profileResponse.json();
      
      // Формируем агрегированный цифровой двойник из всех собранных данных
      const profile = profileData.data;
      const data = profile.data || {};
      
      const aggregatedTwin = {
        email: digitalTwinEmail,
        summary: {
          total_sources: profile.source_count || 0,
          confidence_score: profile.confidence_score || 0,
          last_updated: profile.updated_at,
          is_verified: profile.is_verified || false
        },
        personal_information: data.person_info || {},
        social_presence: {
          social_profiles: data.social_profiles || [],
          websites: data.websites || [],
          total_social_accounts: (data.social_profiles || []).length
        },
        contact_information: {
          phone_numbers: data.phone_numbers || [],
          addresses: data.addresses || [],
          verified_contacts: (data.phone_numbers || []).filter(p => p).length
        },
        digital_footprint: {
          search_results: data.search_results || [],
          search_engines_coverage: new Set((data.search_results || []).map(r => r.source).filter(s => s)).size,
          web_mentions: (data.search_results || []).length,
          search_statistics: data.search_statistics || {}
        },
        academic_profile: data.academic_profile || {},
        data_sources: {
          sources: data.sources || [],
          reliability_score: profile.confidence_score || 0
        },
        timeline: {
          first_seen: profile.created_at,
          last_updated: profile.updated_at,
          data_age_days: profile.updated_at ? Math.floor((new Date() - new Date(profile.updated_at)) / (1000 * 60 * 60 * 24)) : null
        },
        analysis: {
          completeness_score: 0,
          data_quality: profile.confidence_score > 0.7 ? 'Высокая' : profile.confidence_score > 0.4 ? 'Средняя' : 'Низкая',
          recommendations: []
        }
      };
      
      // Расчет completeness score
      const completenessFactors = [
        Boolean(data.person_info?.name),
        Boolean(data.person_info?.location),
        Boolean(data.social_profiles?.length),
        Boolean(data.phone_numbers?.length),
        Boolean(data.websites?.length),
        Boolean(data.search_results?.length)
      ];
      aggregatedTwin.analysis.completeness_score = completenessFactors.filter(Boolean).length / completenessFactors.length;
      
      // Рекомендации
      const recommendations = [];
      if (!data.person_info?.name) recommendations.push('Имя не найдено - рекомендуется дополнительный поиск');
      if (!data.social_profiles?.length) recommendations.push('Социальные профили не найдены - расширить поиск в соц.сетях');
      if ((profile.confidence_score || 0) < 0.5) recommendations.push('Низкий уровень достоверности - требуется верификация данных');
      aggregatedTwin.analysis.recommendations = recommendations;
      
      setDigitalTwinResult({
        status: 'success',
        data: aggregatedTwin,
        generated_at: new Date().toISOString()
      });
      
    } catch (error) {
      console.error('Digital twin error:', error);
      setDigitalTwinResult({
        status: 'error',
        message: 'Ошибка при формировании цифрового двойника.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handlePdfAnalysis = async (e) => {
    e.preventDefault();
    if (!pdfAnalysisEmail) return;

    setIsPdfLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/pdf-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: pdfAnalysisEmail, force_refresh: false })
      });
      const data = await response.json();
      setPdfAnalysisResult(data);
      loadStats();
    } catch (error) {
      console.error('PDF analysis error:', error);
      setPdfAnalysisResult({
        status: 'error',
        message: 'Ошибка при PDF анализе. Проверьте подключение к серверу.'
      });
    } finally {
      setIsPdfLoading(false);
    }
  };

  const TabButton = ({ id, children, isActive, onClick }) => (
    <button
      onClick={() => onClick(id)}
      style={{
        padding: '10px 20px',
        border: 'none',
        backgroundColor: isActive ? '#007bff' : '#f8f9fa',
        color: isActive ? 'white' : '#333',
        borderRadius: '4px 4px 0 0',
        cursor: 'pointer',
        marginRight: '5px',
        fontWeight: isActive ? 'bold' : 'normal'
      }}
    >
      {children}
    </button>
  );

  const Card = ({ children, title, style = {} }) => (
    <div style={{
      backgroundColor: 'white',
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      ...style
    }}>
      {title && <h3 style={{ marginTop: 0, color: '#333' }}>{title}</h3>}
      {children}
    </div>
  );

  const Input = ({ ...props }) => (
    <input
      style={{
        padding: '10px',
        border: '1px solid #ddd',
        borderRadius: '4px',
        fontSize: '16px',
        width: '100%',
        boxSizing: 'border-box'
      }}
      {...props}
    />
  );

  const Button = ({ children, disabled, ...props }) => (
    <button
      style={{
        padding: '10px 20px',
        backgroundColor: disabled ? '#ccc' : '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: '16px'
      }}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: darkMode ? '#2d3748' : '#f5f5f5',
      color: darkMode ? 'white' : '#333'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        {/* Header */}
        <header style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '10px' }}>
            Email Intelligence Collector
          </h1>
          <p style={{ color: '#666', fontSize: '1.1rem' }}>
            Сбор и анализ информации по email-адресам из открытых источников
          </p>
          <div style={{ marginTop: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
              <span>🌞</span>
              <input
                type="checkbox"
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
              />
              <span>🌙</span>
            </label>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div style={{ marginBottom: '20px' }}>
          <TabButton id="single" isActive={activeTab === 'single'} onClick={setActiveTab}>
            📧 Одиночный поиск
          </TabButton>
          <TabButton id="digital-twin" isActive={activeTab === 'digital-twin'} onClick={setActiveTab}>
            👤 Цифровой двойник
          </TabButton>
          <TabButton id="pdf" isActive={activeTab === 'pdf'} onClick={setActiveTab}>
            📄 PDF Анализ
          </TabButton>
          <TabButton id="bulk" isActive={activeTab === 'bulk'} onClick={setActiveTab}>
            📁 Массовый поиск
          </TabButton>
          <TabButton id="stats" isActive={activeTab === 'stats'} onClick={setActiveTab}>
            📊 Статистика
          </TabButton>
        </div>

        {/* Tab Content */}
        <div style={{ minHeight: '400px' }}>
          {/* Single Search Tab */}
          {activeTab === 'single' && (
            <div>
              <Card title="Поиск по одному email">
                <form onSubmit={handleSingleSearch} style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <Input
                    type="email"
                    placeholder="example@domain.com"
                    value={searchEmail}
                    onChange={(e) => setSearchEmail(e.target.value)}
                    required
                  />
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Поиск...' : 'Найти'}
                  </Button>
                </form>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={forceRefresh}
                    onChange={(e) => setForceRefresh(e.target.checked)}
                  />
                  Принудительное обновление (игнорировать кэш)
                </label>
              </Card>

              {searchResult && (
                <Card title="Результаты поиска">
                  {searchResult.status === 'error' ? (
                    <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
                      ❌ {searchResult.message}
                    </div>
                  ) : (
                    <div style={{ backgroundColor: '#e6ffe6', padding: '15px', borderRadius: '4px' }}>
                      <h4>Профиль: {searchResult.data?.email}</h4>
                      <p><strong>Источник:</strong> {searchResult.source === 'cache' ? 'Кэш' : 'Новые данные'}</p>
                      {searchResult.data?.sources && (
                        <p><strong>Источники данных:</strong> {searchResult.data.sources.join(', ')}</p>
                      )}
                      <pre style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
                        {JSON.stringify(searchResult.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </Card>
              )}
            </div>
          )}

          {/* Digital Twin Tab */}
          {activeTab === 'digital-twin' && (
            <div>
              <Card title="Анализ цифрового двойника">
                <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#e6f3ff', borderRadius: '4px', fontSize: '14px' }}>
                  💡 <strong>Автоматическое формирование:</strong> Цифровой двойник создается из всех данных, которые уже были собраны для email-адреса. 
                  Если email не найден в системе, сначала выполните поиск в разделе "Одиночный поиск".
                </div>
                <form onSubmit={handleDigitalTwin} style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <Input
                    type="email"
                    placeholder="example@domain.com"
                    value={digitalTwinEmail}
                    onChange={(e) => setDigitalTwinEmail(e.target.value)}
                    required
                  />
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Анализ...' : 'Создать цифрового двойника'}
                  </Button>
                </form>
              </Card>

              {digitalTwinResult && (
                <div>
                  {digitalTwinResult.status === 'error' ? (
                    <Card title="Ошибка формирования цифрового двойника">
                      <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
                        ❌ {digitalTwinResult.message}
                      </div>
                    </Card>
                  ) : (
                    <div>
                      {/* Summary Card */}
                      <Card title="📊 Общий анализ цифрового двойника">
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff' }}>
                              {Math.round((digitalTwinResult.data.analysis.completeness_score || 0) * 100)}%
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>Полнота данных</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                              {digitalTwinResult.data.summary.total_sources || 0}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>Источников данных</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ffc107' }}>
                              {digitalTwinResult.data.analysis.data_quality}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>Качество данных</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6f42c1' }}>
                              {digitalTwinResult.data.timeline.data_age_days || 0} дн.
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>Возраст данных</div>
                          </div>
                        </div>
                      </Card>

                      {/* Personal Information */}
                      {Object.keys(digitalTwinResult.data.personal_information).length > 0 && (
                        <Card title="👤 Личная информация">
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
                            {digitalTwinResult.data.personal_information.name && (
                              <div><strong>Имя:</strong> {digitalTwinResult.data.personal_information.name}</div>
                            )}
                            {digitalTwinResult.data.personal_information.location && (
                              <div><strong>Местоположение:</strong> {digitalTwinResult.data.personal_information.location}</div>
                            )}
                            {digitalTwinResult.data.personal_information.occupation && (
                              <div><strong>Профессия:</strong> {digitalTwinResult.data.personal_information.occupation}</div>
                            )}
                            {digitalTwinResult.data.personal_information.company && (
                              <div><strong>Компания:</strong> {digitalTwinResult.data.personal_information.company}</div>
                            )}
                          </div>
                        </Card>
                      )}

                      {/* Social Presence */}
                      <Card title="🌐 Цифровое присутствие">
                        <div style={{ marginBottom: '15px' }}>
                          <strong>Социальные аккаунты:</strong> {digitalTwinResult.data.social_presence.total_social_accounts} найдено
                        </div>
                        {digitalTwinResult.data.social_presence.social_profiles.length > 0 && (
                          <div style={{ marginBottom: '15px' }}>
                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Социальные сети:</div>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {digitalTwinResult.data.social_presence.social_profiles.map((social, index) => (
                                <span key={index} style={{
                                  backgroundColor: '#007bff',
                                  color: 'white',
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '12px'
                                }}>
                                  {social.platform}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {digitalTwinResult.data.social_presence.websites.length > 0 && (
                          <div>
                            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>Веб-сайты:</div>
                            <div style={{ fontSize: '14px', color: '#666' }}>
                              {digitalTwinResult.data.social_presence.websites.slice(0, 3).map((site, index) => (
                                <div key={index} style={{ marginBottom: '4px' }}>{site}</div>
                              ))}
                              {digitalTwinResult.data.social_presence.websites.length > 3 && (
                                <div>...и еще {digitalTwinResult.data.social_presence.websites.length - 3}</div>
                              )}
                            </div>
                          </div>
                        )}
                      </Card>

                      {/* Digital Footprint */}
                      <Card title="🔍 Цифровой след">
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                          <div>
                            <div style={{ fontWeight: 'bold' }}>Упоминания в интернете</div>
                            <div style={{ fontSize: '1.2rem', color: '#007bff' }}>{digitalTwinResult.data.digital_footprint.web_mentions}</div>
                          </div>
                          <div>
                            <div style={{ fontWeight: 'bold' }}>Поисковых систем</div>
                            <div style={{ fontSize: '1.2rem', color: '#28a745' }}>{digitalTwinResult.data.digital_footprint.search_engines_coverage}</div>
                          </div>
                        </div>
                      </Card>

                      {/* Contact Information */}
                      {(digitalTwinResult.data.contact_information.phone_numbers.length > 0 || digitalTwinResult.data.contact_information.addresses.length > 0) && (
                        <Card title="📞 Контактная информация">
                          {digitalTwinResult.data.contact_information.phone_numbers.length > 0 && (
                            <div style={{ marginBottom: '15px' }}>
                              <strong>Телефоны:</strong> {digitalTwinResult.data.contact_information.phone_numbers.length} найдено
                            </div>
                          )}
                          {digitalTwinResult.data.contact_information.addresses.length > 0 && (
                            <div>
                              <strong>Адреса:</strong> {digitalTwinResult.data.contact_information.addresses.length} найдено
                            </div>
                          )}
                        </Card>
                      )}

                      {/* Recommendations */}
                      {digitalTwinResult.data.analysis.recommendations.length > 0 && (
                        <Card title="💡 Рекомендации по улучшению">
                          <div style={{ display: 'grid', gap: '8px' }}>
                            {digitalTwinResult.data.analysis.recommendations.map((rec, index) => (
                              <div key={index} style={{
                                padding: '10px',
                                backgroundColor: '#fff3cd',
                                border: '1px solid #ffeaa7',
                                borderRadius: '4px',
                                fontSize: '14px'
                              }}>
                                💡 {rec}
                              </div>
                            ))}
                          </div>
                        </Card>
                      )}

                      {/* Data Sources */}
                      <Card title="📊 Источники данных">
                        <div style={{ marginBottom: '15px' }}>
                          <strong>Всего источников:</strong> {digitalTwinResult.data.data_sources.sources.length}
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {digitalTwinResult.data.data_sources.sources.map((source, index) => (
                            <span key={index} style={{
                              backgroundColor: '#6c757d',
                              color: 'white',
                              padding: '4px 8px',
                              borderRadius: '4px',
                              fontSize: '12px'
                            }}>
                              {source}
                            </span>
                          ))}
                        </div>
                      </Card>

                      {/* Timeline */}
                      <Card title="⏰ Временная линия">
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                          <div>
                            <div style={{ fontWeight: 'bold', color: '#666' }}>Первое обнаружение</div>
                            <div>{digitalTwinResult.data.timeline.first_seen ? new Date(digitalTwinResult.data.timeline.first_seen).toLocaleString('ru-RU') : 'Неизвестно'}</div>
                          </div>
                          <div>
                            <div style={{ fontWeight: 'bold', color: '#666' }}>Последнее обновление</div>
                            <div>{digitalTwinResult.data.timeline.last_updated ? new Date(digitalTwinResult.data.timeline.last_updated).toLocaleString('ru-RU') : 'Неизвестно'}</div>
                          </div>
                        </div>
                      </Card>

                      {/* Raw Data (for debugging) */}
                      <Card title="🔧 Полные данные (для разработчиков)">
                        <details>
                          <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>Показать все данные JSON</summary>
                          <pre style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', overflow: 'auto', fontSize: '12px' }}>
                            {JSON.stringify(digitalTwinResult.data, null, 2)}
                          </pre>
                        </details>
                      </Card>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* PDF Analysis Tab */}
          {activeTab === 'pdf' && (
            <div>
              <Card title="PDF Анализ - Поиск и анализ академических документов">
                <div style={{ marginBottom: '15px', padding: '10px', backgroundColor: '#e6f3ff', borderRadius: '4px', fontSize: '14px' }}>
                  📄 <strong>Поиск PDF документов:</strong> Система найдет PDF документы, содержащие указанный email, через Google Scholar, 
                  ResearchGate, arXiv и другие академические репозитории. Извлечет авторов, учреждения и контекст.
                </div>
                <form onSubmit={handlePdfAnalysis} style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <Input
                    type="email"
                    placeholder="example@domain.com"
                    value={pdfAnalysisEmail}
                    onChange={(e) => setPdfAnalysisEmail(e.target.value)}
                    required
                  />
                  <Button type="submit" disabled={isPdfLoading}>
                    {isPdfLoading ? 'Анализ...' : 'Анализировать PDF'}
                  </Button>
                </form>
              </Card>

              {pdfAnalysisResult && (
                <div>
                  {pdfAnalysisResult.status === 'error' ? (
                    <Card title="Ошибка PDF анализа">
                      <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
                        ❌ {pdfAnalysisResult.message}
                      </div>
                    </Card>
                  ) : (
                    <div>
                      {/* Summary Card */}
                      <Card title="📊 Результаты PDF анализа">
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff' }}>
                              {pdfAnalysisResult.data?.pdf_summary?.total_documents || 0}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>PDF документов найдено</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#28a745' }}>
                              {pdfAnalysisResult.data?.pdf_summary?.documents_with_email || 0}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>с упоминанием email</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ffc107' }}>
                              {Math.round((pdfAnalysisResult.data?.pdf_summary?.average_confidence || 0) * 100)}%
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>средняя достоверность</div>
                          </div>
                          <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#6f42c1' }}>
                              {pdfAnalysisResult.data?.pdf_summary?.total_authors || 0}
                            </div>
                            <div style={{ fontSize: '0.9rem', color: '#666' }}>авторов найдено</div>
                          </div>
                        </div>
                        {pdfAnalysisResult.data?.pdf_summary?.unique_sources && (
                          <div style={{ marginTop: '15px' }}>
                            <strong>Источники:</strong>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '8px' }}>
                              {pdfAnalysisResult.data.pdf_summary.unique_sources.map((source, index) => (
                                <span key={index} style={{
                                  backgroundColor: '#007bff',
                                  color: 'white',
                                  padding: '4px 8px',
                                  borderRadius: '4px',
                                  fontSize: '12px'
                                }}>
                                  {source}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </Card>

                      {/* PDF Documents */}
                      {pdfAnalysisResult.data?.pdf_documents && pdfAnalysisResult.data.pdf_documents.length > 0 && (
                        <Card title="📄 Найденные PDF документы">
                          <div style={{ display: 'grid', gap: '15px' }}>
                            {pdfAnalysisResult.data.pdf_documents.slice(0, 5).map((doc, index) => (
                              <div key={index} style={{
                                border: '1px solid #ddd',
                                borderRadius: '8px',
                                padding: '15px',
                                backgroundColor: doc.email_found ? '#e6ffe6' : '#f8f9fa'
                              }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                                  <h4 style={{ margin: 0, color: '#333', flex: 1 }}>
                                    {doc.title || 'Без названия'}
                                  </h4>
                                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                    {doc.email_found && (
                                      <span style={{ backgroundColor: '#28a745', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                                        ✅ Email найден
                                      </span>
                                    )}
                                    <span style={{ backgroundColor: '#6c757d', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                                      {doc.source || 'Unknown'}
                                    </span>
                                  </div>
                                </div>
                                
                                {doc.url && (
                                  <div style={{ marginBottom: '10px', fontSize: '14px' }}>
                                    <strong>URL:</strong> <a href={doc.url} target="_blank" rel="noopener noreferrer" style={{ color: '#007bff' }}>
                                      {doc.url.length > 80 ? doc.url.substring(0, 80) + '...' : doc.url}
                                    </a>
                                  </div>
                                )}
                                
                                {doc.authors && doc.authors.length > 0 && (
                                  <div style={{ marginBottom: '10px' }}>
                                    <strong>Авторы:</strong> {doc.authors.slice(0, 3).join(', ')}
                                    {doc.authors.length > 3 && ` (и еще ${doc.authors.length - 3})`}
                                  </div>
                                )}
                                
                                {doc.institutions && doc.institutions.length > 0 && (
                                  <div style={{ marginBottom: '10px' }}>
                                    <strong>Учреждения:</strong> {doc.institutions.slice(0, 2).join(', ')}
                                    {doc.institutions.length > 2 && ` (и еще ${doc.institutions.length - 2})`}
                                  </div>
                                )}
                                
                                {doc.email_contexts && doc.email_contexts.length > 0 && (
                                  <div style={{ marginBottom: '10px' }}>
                                    <strong>Контексты упоминания email ({doc.email_contexts.length}):</strong>
                                    <div style={{ marginTop: '8px', maxHeight: '200px', overflowY: 'auto' }}>
                                      {doc.email_contexts.slice(0, 2).map((context, ctxIndex) => (
                                        <div key={ctxIndex} style={{
                                          backgroundColor: '#fff3cd',
                                          border: '1px solid #ffeaa7',
                                          borderRadius: '4px',
                                          padding: '8px',
                                          marginBottom: '8px',
                                          fontSize: '13px'
                                        }}>
                                          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Строка {context.line_number}:</div>
                                          <div style={{ fontFamily: 'monospace', backgroundColor: '#fff', padding: '4px', borderRadius: '2px' }}>
                                            {context.line}
                                          </div>
                                        </div>
                                      ))}
                                      {doc.email_contexts.length > 2 && (
                                        <div style={{ fontSize: '12px', color: '#666', fontStyle: 'italic' }}>
                                          ...и еще {doc.email_contexts.length - 2} упоминаний
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                                
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px', color: '#666' }}>
                                  <div>Размер текста: {doc.text_length || 0} символов</div>
                                  <div>Достоверность: {Math.round((doc.confidence_score || 0) * 100)}%</div>
                                </div>
                              </div>
                            ))}
                            {pdfAnalysisResult.data.pdf_documents.length > 5 && (
                              <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', fontSize: '14px', color: '#666' }}>
                                ...и еще {pdfAnalysisResult.data.pdf_documents.length - 5} PDF документов
                              </div>
                            )}
                          </div>
                        </Card>
                      )}

                      {/* Raw Data */}
                      <Card title="🔧 Полные данные PDF анализа">
                        <details>
                          <summary style={{ cursor: 'pointer', fontWeight: 'bold', marginBottom: '10px' }}>Показать все данные JSON</summary>
                          <pre style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', overflow: 'auto', fontSize: '12px' }}>
                            {JSON.stringify(pdfAnalysisResult.data, null, 2)}
                          </pre>
                        </details>
                      </Card>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Bulk Search Tab */}
          {activeTab === 'bulk' && (
            <div>
              <Card title="Массовый поиск">
                <form onSubmit={handleBulkSearch} style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <Input
                    type="file"
                    accept=".csv,.txt"
                    onChange={(e) => setBulkFile(e.target.files[0])}
                    required
                  />
                  <Button type="submit" disabled={isLoading || !bulkFile}>
                    {isLoading ? 'Обработка...' : 'Загрузить'}
                  </Button>
                </form>
                <p style={{ color: '#666', fontSize: '14px' }}>
                  Поддерживаются файлы CSV и TXT с email-адресами
                </p>
              </Card>

              {bulkResult && (
                <Card title="Результаты массового поиска">
                  {bulkResult.status === 'error' ? (
                    <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
                      ❌ {bulkResult.message}
                    </div>
                  ) : (
                    <div style={{ backgroundColor: '#e6ffe6', padding: '15px', borderRadius: '4px' }}>
                      <pre style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px', overflow: 'auto' }}>
                        {JSON.stringify(bulkResult, null, 2)}
                      </pre>
                    </div>
                  )}
                </Card>
              )}
            </div>
          )}

          {/* Stats Tab */}
          {activeTab === 'stats' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2>Статистика системы</h2>
                <Button onClick={loadStats} disabled={isLoadingStats}>
                  {isLoadingStats ? 'Обновление...' : 'Обновить'}
                </Button>
              </div>

              {stats && !stats.error ? (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                    <Card title="Всего профилей" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
                        {stats.total_profiles}
                      </div>
                      <p style={{ color: '#666', margin: 0 }}>в базе данных</p>
                    </Card>

                    <Card title="Всего поисков" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
                        {stats.total_searches}
                      </div>
                      <p style={{ color: '#666', margin: 0 }}>выполнено запросов</p>
                    </Card>

                    <Card title="Поисковые результаты" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
                        {stats.search_engine_results || 0}
                      </div>
                      <p style={{ color: '#666', margin: 0 }}>через поисковики</p>
                    </Card>

                    <Card title="Последние поиски" style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#6f42c1' }}>
                        {stats.recent_searches?.length || 0}
                      </div>
                      <p style={{ color: '#666', margin: 0 }}>недавних запросов</p>
                    </Card>
                  </div>

                  {stats.recent_searches && stats.recent_searches.length > 0 && (
                    <Card title="Последние поиски">
                      <div style={{ display: 'grid', gap: '10px' }}>
                        {stats.recent_searches.map((search, index) => (
                          <div key={index} style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '10px',
                            backgroundColor: '#f8f9fa',
                            borderRadius: '4px',
                            border: '1px solid #e9ecef'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <span style={{
                                backgroundColor: search.search_type === 'single' ? '#007bff' : '#6c757d',
                                color: 'white',
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px'
                              }}>
                                {search.search_type === 'single' ? 'Одиночный' : 'Массовый'}
                              </span>
                              <strong>{search.email}</strong>
                            </div>
                            <div style={{ fontSize: '14px', color: '#666' }}>
                              {search.results_found} результатов • {new Date(search.created_at).toLocaleString('ru-RU')}
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card>
                  )}
                </>
              ) : (
                <Card title="Статистика системы">
                  {isLoadingStats ? (
                    <div style={{ textAlign: 'center', color: '#666' }}>
                      Загрузка статистики...
                    </div>
                  ) : stats?.error ? (
                    <div style={{ color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px' }}>
                      ❌ {stats.error}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#666' }}>
                      Статистика будет доступна после подключения к API
                    </div>
                  )}
                </Card>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <footer style={{ 
          textAlign: 'center', 
          marginTop: '40px', 
          padding: '20px', 
          borderTop: '1px solid #ddd',
          color: '#666'
        }}>
          <p>✅ React приложение работает корректно</p>
          <p>🔗 API соединение: {stats ? 'установлено' : 'проверяется...'}</p>
          <p>🚀 Frontend: http://localhost:5173 | Backend: http://localhost:8000</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
