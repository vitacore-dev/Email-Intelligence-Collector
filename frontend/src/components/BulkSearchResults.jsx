import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { CheckCircle, XCircle, AlertCircle, Clock, Users, Database } from 'lucide-react';

const BulkSearchResults = ({ data }) => {
  if (!data) return null;

  const successRate = data.total > 0 ? Math.round((data.processed / data.total) * 100) : 0;
  const newRate = data.total > 0 ? Math.round((data.new / data.total) * 100) : 0;
  const cacheRate = data.total > 0 ? Math.round((data.existing / data.total) * 100) : 0;

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              <div>
                <div className="text-2xl font-bold">{data.total}</div>
                <div className="text-sm text-muted-foreground">Всего</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <div>
                <div className="text-2xl font-bold text-green-600">{data.processed}</div>
                <div className="text-sm text-muted-foreground">Обработано</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-600" />
              <div>
                <div className="text-2xl font-bold text-blue-600">{data.existing}</div>
                <div className="text-sm text-muted-foreground">Из кэша</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-purple-600" />
              <div>
                <div className="text-2xl font-bold text-purple-600">{data.new}</div>
                <div className="text-sm text-muted-foreground">Новых</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <div>
                <div className="text-2xl font-bold text-red-600">{data.invalid}</div>
                <div className="text-sm text-muted-foreground">Невалидных</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Progress Bars */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4" />
            Прогресс обработки
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Общий прогресс</span>
              <span>{successRate}%</span>
            </div>
            <Progress value={successRate} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Новые данные</span>
              <span>{newRate}%</span>
            </div>
            <Progress value={newRate} className="h-2" />
          </div>

          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Из кэша</span>
              <span>{cacheRate}%</span>
            </div>
            <Progress value={cacheRate} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-green-600">Успешно обработано</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Валидных email:</span>
                <Badge variant="outline">{data.processed}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Успешность:</span>
                <Badge variant="default">{successRate}%</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">Проблемные записи</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Невалидных email:</span>
                <Badge variant="destructive">{data.invalid}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Процент ошибок:</span>
                <Badge variant="outline">{Math.round((data.invalid / data.total) * 100)}%</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Processing Details */}
      {data.details && (
        <Card>
          <CardHeader>
            <CardTitle>Детали обработки</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.details.map((detail, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    {detail.status === 'success' ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : detail.status === 'cached' ? (
                      <Database className="h-4 w-4 text-blue-600" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-600" />
                    )}
                    <span className="font-mono text-sm">{detail.email}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={
                        detail.status === 'success' ? 'default' :
                        detail.status === 'cached' ? 'secondary' : 'destructive'
                      }
                    >
                      {detail.status === 'success' ? 'Обработан' :
                       detail.status === 'cached' ? 'Кэш' : 'Ошибка'}
                    </Badge>
                    {detail.sources_found && (
                      <Badge variant="outline">
                        {detail.sources_found} источников
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Сводка производительности</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center">
              <div className="text-lg font-semibold text-green-600">{successRate}%</div>
              <div className="text-muted-foreground">Успешность</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-blue-600">{cacheRate}%</div>
              <div className="text-muted-foreground">Из кэша</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-purple-600">{newRate}%</div>
              <div className="text-muted-foreground">Новых данных</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-red-600">
                {Math.round((data.invalid / data.total) * 100)}%
              </div>
              <div className="text-muted-foreground">Ошибок</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BulkSearchResults;
