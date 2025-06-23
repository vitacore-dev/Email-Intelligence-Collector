import React, { useState } from 'react';
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

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [searchEmail, setSearchEmail] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkResult, setBulkResult] = useState(null);
  const [forceRefresh, setForceRefresh] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleSingleSearch = async (e) => {
    e.preventDefault();
    if (!searchEmail) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/search', {
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
        body: formData,
      });

      const data = await response.json();
      setBulkResult(data);
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
          <TabsList className="grid w-full grid-cols-3">
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
                    renderProfileData(searchResult)
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
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold">{bulkResult.total}</div>
                          <div className="text-sm text-muted-foreground">Всего</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">{bulkResult.processed}</div>
                          <div className="text-sm text-muted-foreground">Обработано</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-600">{bulkResult.existing}</div>
                          <div className="text-sm text-muted-foreground">Из кэша</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-600">{bulkResult.new}</div>
                          <div className="text-sm text-muted-foreground">Новых</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">{bulkResult.invalid}</div>
                          <div className="text-sm text-muted-foreground">Невалидных</div>
                        </div>
                      </div>
                      
                      <Progress value={(bulkResult.processed / bulkResult.total) * 100} />
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Stats Tab */}
          <TabsContent value="stats" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Статистика системы</CardTitle>
                <CardDescription>
                  Общая информация о работе системы
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center text-muted-foreground">
                  Статистика будет доступна после подключения к API
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;

