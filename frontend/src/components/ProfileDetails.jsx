import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { User, Mail, Phone, MapPin, Building, Link, Calendar, TrendingUp, Search, Globe, BarChart } from 'lucide-react';

const ProfileDetails = ({ data }) => {
  if (!data || !data.data) return null;

  const profile = data.data;
  const source = data.source;

  // Компонент для отображения результатов поисковых систем
  const SearchResultsSection = ({ searchResults, searchStats }) => {
    if (!searchResults || searchResults.length === 0) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Результаты поисковых систем
          </CardTitle>
          <CardDescription>
            Найдено {searchResults.length} релевантных результатов из поисковых систем
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="results" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="results">Результаты поиска</TabsTrigger>
              <TabsTrigger value="stats">Статистика</TabsTrigger>
            </TabsList>
            
            <TabsContent value="results" className="space-y-3 mt-4">
              {searchResults.map((result, index) => (
                <div key={index} className="p-4 border rounded-lg space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline">{result.source}</Badge>
                        <Badge variant="secondary">Ранг: {result.rank}</Badge>
                        {result.relevance_score && (
                          <Badge variant="outline">
                            Релевантность: {Math.round(result.relevance_score * 100)}%
                          </Badge>
                        )}
                      </div>
                      <h4 className="font-medium text-sm leading-tight mb-1">
                        {result.title}
                      </h4>
                      {result.snippet && (
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {result.snippet}
                        </p>
                      )}
                      <a 
                        href={result.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-xs truncate block"
                      >
                        {result.url}
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </TabsContent>
            
            <TabsContent value="stats" className="mt-4">
              {searchStats && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {searchStats.search_engines_used && (
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">Использованные поисковые системы</div>
                      <div className="flex flex-wrap gap-2">
                        {searchStats.search_engines_used.map((engine, index) => (
                          <Badge key={index} variant="secondary">{engine}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {searchStats.total_results && (
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">Всего результатов найдено</div>
                      <div className="text-lg font-semibold">{searchStats.total_results}</div>
                    </div>
                  )}
                  
                  {searchStats.processing_time && (
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">Время обработки</div>
                      <div className="text-lg font-semibold">{searchStats.processing_time.toFixed(2)}с</div>
                    </div>
                  )}
                  
                  {searchStats.unique_domains && (
                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">Уникальных доменов</div>
                      <div className="text-lg font-semibold">{searchStats.unique_domains}</div>
                    </div>
                  )}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold flex items-center gap-2">
          <Mail className="h-5 w-5" />
          Профиль: {profile.email}
        </h3>
        <div className="flex items-center gap-2">
          <Badge variant={source === 'cache' ? 'secondary' : 'default'}>
            {source === 'cache' ? 'Из кэша' : 'Новые данные'}
          </Badge>
          {profile.confidence_score && (
            <Badge variant="outline">
              Достоверность: {Math.round(profile.confidence_score * 100)}%
            </Badge>
          )}
        </div>
      </div>

      <Separator />

      {/* Search Results from Search Engines */}
      <SearchResultsSection 
        searchResults={profile.search_results} 
        searchStats={profile.search_statistics} 
      />

      {/* Personal Information */}
      {profile.person_info && Object.keys(profile.person_info).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Личная информация
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profile.person_info.name && (
              <div className="flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">Имя</div>
                  <div className="font-medium">{profile.person_info.name}</div>
                </div>
              </div>
            )}
            {profile.person_info.location && (
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">Местоположение</div>
                  <div className="font-medium">{profile.person_info.location}</div>
                </div>
              </div>
            )}
            {profile.person_info.occupation && (
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">Профессия</div>
                  <div className="font-medium">{profile.person_info.occupation}</div>
                </div>
              </div>
            )}
            {profile.person_info.company && (
              <div className="flex items-center gap-2">
                <Building className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="text-sm text-muted-foreground">Компания</div>
                  <div className="font-medium">{profile.person_info.company}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Contact Information */}
      {(profile.phone_numbers?.length > 0 || profile.addresses?.length > 0) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Phone className="h-4 w-4" />
              Контактная информация
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {profile.phone_numbers && profile.phone_numbers.length > 0 && (
              <div>
                <div className="text-sm text-muted-foreground mb-2">Телефоны</div>
                <div className="flex flex-wrap gap-2">
                  {profile.phone_numbers.map((phone, index) => (
                    <Badge key={index} variant="outline">
                      {phone}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {profile.addresses && profile.addresses.length > 0 && (
              <div>
                <div className="text-sm text-muted-foreground mb-2">Адреса</div>
                <div className="space-y-1">
                  {profile.addresses.map((address, index) => (
                    <div key={index} className="text-sm">{address}</div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Social Profiles */}
      {profile.social_profiles && profile.social_profiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Link className="h-4 w-4" />
              Социальные сети
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {profile.social_profiles.map((social, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{social.platform}</Badge>
                    <div className="flex flex-col">
                      <span className="text-sm font-medium">
                        {social.username || 'Профиль найден'}
                      </span>
                      {social.source && (
                        <span className="text-xs text-muted-foreground">
                          Источник: {social.source}
                        </span>
                      )}
                    </div>
                  </div>
                  <a 
                    href={social.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Открыть
                  </a>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Websites */}
      {profile.websites && profile.websites.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Веб-сайты
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.websites.map((website, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <span className="text-sm truncate">{website}</span>
                  <a 
                    href={website.startsWith('http') ? website : `https://${website}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm flex-shrink-0 ml-2"
                  >
                    Посетить
                  </a>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Sources */}
      {profile.sources && profile.sources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Источники данных
            </CardTitle>
            <CardDescription>
              Платформы, из которых была собрана информация
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {profile.sources.map((source, index) => {
                const isSearchEngine = source.toLowerCase().includes('search');
                return (
                  <Badge 
                    key={index} 
                    variant={isSearchEngine ? "default" : "secondary"}
                    className={isSearchEngine ? "bg-blue-100 text-blue-800" : ""}
                  >
                    {source}
                  </Badge>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Метаданные
          </CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {profile.last_updated && (
            <div>
              <div className="text-muted-foreground">Последнее обновление</div>
              <div>{new Date(profile.last_updated).toLocaleString('ru-RU')}</div>
            </div>
          )}
          {profile.confidence_score && (
            <div>
              <div className="text-muted-foreground">Уровень достоверности</div>
              <div>{Math.round(profile.confidence_score * 100)}%</div>
            </div>
          )}
          {profile.sources && (
            <div>
              <div className="text-muted-foreground">Количество источников</div>
              <div>{profile.sources.length}</div>
            </div>
          )}
          {profile.search_results && (
            <div>
              <div className="text-muted-foreground">Результаты поиска</div>
              <div>{profile.search_results.length} найдено</div>
            </div>
          )}
          <div>
            <div className="text-muted-foreground">Источник данных</div>
            <div>{source === 'cache' ? 'Кэш системы' : 'Новый сбор'}</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfileDetails;
