import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { BarChart, Search, Clock, Globe, TrendingUp, Database } from 'lucide-react';

const SearchEngineStats = ({ stats }) => {
  if (!stats || !stats.search_engine_stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Статистика поисковых систем
          </CardTitle>
          <CardDescription>
            Данные о работе поисковых систем недоступны
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground">
            Статистика будет доступна после выполнения поисковых запросов
          </div>
        </CardContent>
      </Card>
    );
  }

  const searchEngineStats = stats.search_engine_stats;
  const totalResults = Object.values(searchEngineStats).reduce((sum, engine) => sum + (engine.total_results || 0), 0);
  const totalUsage = Object.values(searchEngineStats).reduce((sum, engine) => sum + (engine.usage_count || 0), 0);

  // Расчет средних показателей
  const avgSuccessRate = Object.values(searchEngineStats).reduce((sum, engine) => sum + (engine.success_rate || 0), 0) / Object.keys(searchEngineStats).length;
  const avgResponseTime = Object.values(searchEngineStats).reduce((sum, engine) => sum + (engine.avg_response_time || 0), 0) / Object.keys(searchEngineStats).length;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{totalResults}</div>
                <div className="text-xs text-muted-foreground">Всего результатов</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{Object.keys(searchEngineStats).length}</div>
                <div className="text-xs text-muted-foreground">Активных систем</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-orange-500" />
              <div>
                <div className="text-2xl font-bold">{Math.round(avgSuccessRate * 100)}%</div>
                <div className="text-xs text-muted-foreground">Средний успех</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-purple-500" />
              <div>
                <div className="text-2xl font-bold">{avgResponseTime.toFixed(1)}с</div>
                <div className="text-xs text-muted-foreground">Среднее время</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Engine Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart className="h-4 w-4" />
            Детальная статистика по поисковым системам
          </CardTitle>
          <CardDescription>
            Производительность и эффективность каждой поисковой системы
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {Object.entries(searchEngineStats).map(([engine, data]) => {
              const successRate = (data.success_rate || 0) * 100;
              const usagePercentage = totalUsage > 0 ? (data.usage_count || 0) / totalUsage * 100 : 0;

              return (
                <div key={engine} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Badge variant="outline" className="font-medium">
                        {engine}
                      </Badge>
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant={successRate >= 80 ? "default" : successRate >= 60 ? "secondary" : "destructive"}
                          className="text-xs"
                        >
                          {successRate.toFixed(1)}% успех
                        </Badge>
                        {data.is_premium && (
                          <Badge variant="outline" className="text-xs">
                            Premium
                          </Badge>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {data.total_results || 0} результатов
                    </div>
                  </div>

                  {/* Progress Bars */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Успешность запросов</span>
                      <span className="font-medium">{successRate.toFixed(1)}%</span>
                    </div>
                    <Progress value={successRate} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Доля использования</span>
                      <span className="font-medium">{usagePercentage.toFixed(1)}%</span>
                    </div>
                    <Progress value={usagePercentage} className="h-2" />
                  </div>

                  {/* Detailed Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2">
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Запросов</div>
                      <div className="font-medium">{data.usage_count || 0}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Время ответа</div>
                      <div className="font-medium">
                        {data.avg_response_time ? `${data.avg_response_time.toFixed(2)}с` : 'N/A'}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Результатов/запрос</div>
                      <div className="font-medium">
                        {data.usage_count > 0 ? ((data.total_results || 0) / data.usage_count).toFixed(1) : 'N/A'}
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-xs text-muted-foreground">Статус</div>
                      <div className="font-medium">
                        <Badge 
                          variant={data.is_active ? "default" : "secondary"}
                          className="text-xs"
                        >
                          {data.is_active ? 'Активна' : 'Неактивна'}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Rate Limiting Info */}
                  {data.rate_limit && (
                    <div className="text-xs text-muted-foreground border-t pt-2">
                      Лимит: {data.rate_limit} запросов/час
                      {data.last_used && (
                        <span className="ml-2">
                          • Последнее использование: {new Date(data.last_used).toLocaleString('ru-RU')}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Performance Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Сравнение производительности</CardTitle>
          <CardDescription>
            Рейтинг поисковых систем по эффективности
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(searchEngineStats)
              .sort((a, b) => (b[1].success_rate || 0) - (a[1].success_rate || 0))
              .map(([engine, data], index) => (
                <div key={engine} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">#{index + 1}</Badge>
                    <span className="font-medium">{engine}</span>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-medium">{Math.round((data.success_rate || 0) * 100)}%</div>
                      <div className="text-xs text-muted-foreground">Успех</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">{data.total_results || 0}</div>
                      <div className="text-xs text-muted-foreground">Результатов</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">
                        {data.avg_response_time ? `${data.avg_response_time.toFixed(1)}с` : 'N/A'}
                      </div>
                      <div className="text-xs text-muted-foreground">Время</div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SearchEngineStats;
