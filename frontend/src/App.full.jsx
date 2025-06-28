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
import DigitalTwin from './components/DigitalTwin';
import apiService from './services/api';

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
  const [digitalTwinEmail, setDigitalTwinEmail] = useState('');

  // Load statistics on component mount
  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setIsLoadingStats(true);
    try {
      const data = await apiService.getStats();
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
      const data = await apiService.searchSingle(searchEmail, forceRefresh);
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
      const data = await apiService.searchBulk(formData);
      setBulkResult(data);
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
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="single" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Одиночный поиск
            </TabsTrigger>
            <TabsTrigger value="digital-twin" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Цифровой двойник
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

          {/* Digital Twin Tab */}
          <TabsContent value="digital-twin" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Анализ цифрового двойника</CardTitle>
                <CardDescription>
                  Введите email для создания цифрового двойника исследователя
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  if (digitalTwinEmail) {
                    setDigitalTwinEmail(digitalTwinEmail);
                  }
                }} className="space-y-4">
                  <div className="flex gap-4">
                    <Input
                      type="email"
                      placeholder="researcher@university.com"
                      value={digitalTwinEmail}
                      onChange={(e) => setDigitalTwinEmail(e.target.value)}
                      className="flex-1"
                      required
                    />
                    <Button type="submit">
                      Создать цифрового двойника
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* Digital Twin Results */}
            {digitalTwinEmail && (
              <DigitalTwin email={digitalTwinEmail} />
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
