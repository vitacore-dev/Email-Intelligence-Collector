import React, { useState, useEffect } from 'react';
import './App.css';
import { Search, Upload, User, BarChart3, Settings, Moon, Sun } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Switch } from './components/ui/switch';
import { Label } from './components/ui/label';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import ProfileDetails from './components/ProfileDetails';
import BulkSearchResults from './components/BulkSearchResults';
import SearchEngineStats from './components/SearchEngineStats';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [searchEmail, setSearchEmail] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkResult, setBulkResult] = useState(null);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [stats, setStats] = useState(null);
  const [isLoadingStats, setIsLoadingStats] = useState(false);

  // Load statistics on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const response = await fetch('http://localhost:8001/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Stats loading error:', error);
      setStats({ error: 'Не удалось загрузить статистику' });
    } finally {
      setIsLoadingStats(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleSingleSearch = async (e) => {
    e.preventDefault();
    if (!searchEmail) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8001/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: searchEmail,
          force_refresh: forceRefresh
        }),
      });

      const data = await response.json();
      setSearchResult(data);
      // Refresh stats after successful search
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
      const response = await fetch('http://localhost:8001/api/bulk_search', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setBulkResult(data);
      // Refresh stats after successful bulk search
      loadStats();
    } catch (error) {
      console.error('Bulk search error:', error);
      setBulkResult({
        status: 'error',
        message: 'Ошибка при массовом поиске. Проверьте подключение к серверу.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderProfileData = (data) => {
    if (!data || !data.data) return null;

    const profile = data.data;
    
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Профиль: {profile.email}</h3>
          <Badge variant={data.source === 'cache' ? 'secondary' : 'default'}>
            {data.source === 'cache' ? 'Из кэша' : 'Новые данные'}
          </Badge>
        </div>
        
        {profile.person_info && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Личная информация
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {profile.person_info.name && (
                <div><strong>Имя:</strong> {profile.person_info.name}</div>
              )}
              {profile.person_info.location && (
                <div><strong>Местоположение:</strong> {profile.person_info.location}</div>
              )}
              {profile.person_info.occupation && (
                <div><strong>Профессия:</strong> {profile.person_info.occupation}</div>
              )}
              {profile.person_info.company && (
                <div><strong>Компания:</strong> {profile.person_info.company}</div>
              )}
            </CardContent>
          </Card>
        )}

        {profile.social_profiles && profile.social_profiles.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Социальные сети</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {profile.social_profiles.map((social, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <Badge variant="outline">{social.platform}</Badge>
                    <a 
                      href={social.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {social.username || social.url}
                    </a>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {profile.sources && profile.sources.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Источники данных</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {profile.sources.map((source, index) => (
                  <Badge key={index} variant="secondary">{source}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className={`min-h-screen bg-background ${darkMode ? 'dark' : ''}`}>
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Email Intelligence Collector</h1>
            <p className="text-muted-foreground">
              Сбор и анализ информации по email-адресам из открытых источников
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center space-x-2">
              <Sun className="h-4 w-4" />
              <Switch checked={darkMode} onCheckedChange={toggleDarkMode} />
              <Moon className="h-4 w-4" />
            </div>
          </div>
        </div>

        <Tabs defaultValue="single" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="single" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Одиночный поиск
            </TabsTrigger>
            <TabsTrigger value="bulk" className="flex items-center gap-2">
              <Upload className="h-4 w-4" />
              Массовый поиск
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Статистика
            </TabsTrigger>
            <TabsTrigger value="search-engines" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Поисковые системы
            </TabsTrigger>
          </TabsList>

          {/* Single Search Tab */}
          <TabsContent value="single" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Поиск по одному email</CardTitle>
                <CardDescription>
                  Введите email-адрес для сбора информации из открытых источников
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSingleSearch} className="space-y-4">
                  <div className="flex gap-4">
                    <Input
                      type="email"
                      placeholder="example@domain.com"
                      value={searchEmail}
                      onChange={(e) => setSearchEmail(e.target.value)}
                      className="flex-1"
                      required
                    />
                    <Button type="submit" disabled={isLoading}>
                      {isLoading ? 'Поиск...' : 'Найти'}
                    </Button>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Switch 
                      id="force-refresh" 
                      checked={forceRefresh}
                      onCheckedChange={setForceRefresh}
                    />
                    <Label htmlFor="force-refresh">
                      Принудительное обновление (игнорировать кэш)
                    </Label>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Search Results */}
            {searchResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Результаты поиска</CardTitle>
                </CardHeader>
                <CardContent>
                  {searchResult.status === 'error' ? (
                    <Alert>
                      <AlertDescription>{searchResult.message}</AlertDescription>
                    </Alert>
                  ) : (
                    <ProfileDetails data={searchResult} />
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Bulk Search Tab */}
          <TabsContent value="bulk" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Массовый поиск</CardTitle>
                <CardDescription>
                  Загрузите файл с email-адресами (CSV или TXT)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleBulkSearch} className="space-y-4">
                  <div className="flex gap-4">
                    <Input
                      type="file"
                      accept=".csv,.txt"
                      onChange={(e) => setBulkFile(e.target.files[0])}
                      className="flex-1"
                      required
                    />
                    <Button type="submit" disabled={isLoading || !bulkFile}>
                      {isLoading ? 'Обработка...' : 'Загрузить'}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Bulk Results */}
            {bulkResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Результаты массового поиска</CardTitle>
                </CardHeader>
                <CardContent>
                  {bulkResult.status === 'error' ? (
                    <Alert>
                      <AlertDescription>{bulkResult.message}</AlertDescription>
                    </Alert>
                  ) : (
                    <BulkSearchResults data={bulkResult} />
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Stats Tab */}
          <TabsContent value="stats" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Статистика системы</h2>
              <Button onClick={loadStats} disabled={isLoadingStats}>
                {isLoadingStats ? 'Обновление...' : 'Обновить'}
              </Button>
            </div>
            
            {stats && !stats.error ? (
              <>
                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Всего профилей</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.total_profiles}</div>
                      <p className="text-xs text-muted-foreground">в базе данных</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Всего поисков</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.total_searches}</div>
                      <p className="text-xs text-muted-foreground">выполнено запросов</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium flex items-center gap-1">
                        <Search className="h-3 w-3" />
                        Поисковые результаты
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.search_engine_results || 0}</div>
                      <p className="text-xs text-muted-foreground">найдено через поисковики</p>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium">Последние поиски</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">{stats.recent_searches?.length || 0}</div>
                      <p className="text-xs text-muted-foreground">недавних запросов</p>
                    </CardContent>
                  </Card>
                </div>
                
                {/* Search Engine Statistics */}
                {stats.search_engine_stats && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Search className="h-4 w-4" />
                        Статистика поисковых систем
                      </CardTitle>
                      <CardDescription>
                        Эффективность различных поисковых систем
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {Object.entries(stats.search_engine_stats).map(([engine, data]) => (
                          <div key={engine} className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Badge variant="outline">{engine}</Badge>
                              <span className="text-sm text-muted-foreground">
                                {data.success_rate ? `${Math.round(data.success_rate * 100)}%` : 'N/A'}
                              </span>
                            </div>
                            <div className="space-y-1">
                              <div className="flex justify-between text-sm">
                                <span>Результатов:</span>
                                <span className="font-medium">{data.total_results || 0}</span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Использований:</span>
                                <span className="font-medium">{data.usage_count || 0}</span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Среднее время:</span>
                                <span className="font-medium">
                                  {data.avg_response_time ? `${data.avg_response_time.toFixed(2)}с` : 'N/A'}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                {/* Recent Searches */}
                {stats.recent_searches && stats.recent_searches.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Последние поиски</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {stats.recent_searches.map((search, index) => (
                          <div key={search.id || index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              <Badge variant={search.search_type === 'single' ? 'default' : 'secondary'}>
                                {search.search_type === 'single' ? 'Одиночный' : 'Массовый'}
                              </Badge>
                              <span className="font-medium">{search.email}</span>
                            </div>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                              <span>{search.results_found} результатов</span>
                              <span>{new Date(search.created_at).toLocaleString('ru-RU')}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Статистика системы</CardTitle>
                  <CardDescription>
                    Общая информация о работе системы
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoadingStats ? (
                    <div className="text-center text-muted-foreground">
                      Загрузка статистики...
                    </div>
                  ) : stats?.error ? (
                    <Alert>
                      <AlertDescription>{stats.error}</AlertDescription>
                    </Alert>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      Статистика будет доступна после подключения к API
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Search Engines Tab */}
          <TabsContent value="search-engines" className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Детальная статистика поисковых систем</h2>
              <Button onClick={loadStats} disabled={isLoadingStats}>
                {isLoadingStats ? 'Обновление...' : 'Обновить'}
              </Button>
            </div>
            
            {stats && !stats.error ? (
              <SearchEngineStats stats={stats} />
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>Статистика поисковых систем</CardTitle>
                  <CardDescription>
                    Детальный анализ работы поисковых систем
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoadingStats ? (
                    <div className="text-center text-muted-foreground">
                      Загрузка статистики...
                    </div>
                  ) : stats?.error ? (
                    <Alert>
                      <AlertDescription>{stats.error}</AlertDescription>
                    </Alert>
                  ) : (
                    <div className="text-center text-muted-foreground">
                      Статистика будет доступна после подключения к API
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;

