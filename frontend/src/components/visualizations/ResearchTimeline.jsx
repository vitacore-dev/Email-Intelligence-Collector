import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { Badge } from '../ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

const ResearchTimeline = ({ data }) => {
  // Default data if none provided
  const defaultData = [
    { year: 2018, publications: 3, citations: 45, collaborations: 2 },
    { year: 2019, publications: 5, citations: 78, collaborations: 4 },
    { year: 2020, publications: 7, citations: 123, collaborations: 6 },
    { year: 2021, publications: 4, citations: 156, collaborations: 5 },
    { year: 2022, publications: 6, citations: 201, collaborations: 8 },
    { year: 2023, publications: 8, citations: 289, collaborations: 7 }
  ];

  const timelineData = data && data.timeline ? data.timeline : defaultData;
  const events = data && data.events ? data.events : [];

  // Custom tooltip for the charts
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{`Год: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      {/* Main timeline chart */}
      <Card>
        <CardHeader>
          <CardTitle>Динамика публикаций и цитирований</CardTitle>
          <CardDescription>
            Изменение исследовательской активности во времени
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="year" 
                  stroke="#64748b"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="publications" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                  name="Публикации"
                />
                <Line 
                  type="monotone" 
                  dataKey="citations" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  dot={{ fill: '#10b981', strokeWidth: 2, r: 6 }}
                  name="Цитирования"
                />
                <Line 
                  type="monotone" 
                  dataKey="collaborations" 
                  stroke="#f59e0b" 
                  strokeWidth={3}
                  dot={{ fill: '#f59e0b', strokeWidth: 2, r: 6 }}
                  name="Коллаборации"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Publications by year as bars */}
      <Card>
        <CardHeader>
          <CardTitle>Публикации по годам</CardTitle>
          <CardDescription>
            Распределение публикационной активности
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="year" 
                  stroke="#64748b"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#64748b"
                  fontSize={12}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="publications" 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                  name="Публикации"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Timeline events */}
      {events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Ключевые события</CardTitle>
            <CardDescription>
              Важные вехи в исследовательской карьере
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {events.map((event, index) => (
                <div key={index} className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className="flex-shrink-0">
                    <Badge variant="outline">{event.year}</Badge>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{event.title}</div>
                    {event.description && (
                      <div className="text-sm text-muted-foreground mt-1">
                        {event.description}
                      </div>
                    )}
                    {event.type && (
                      <Badge variant="secondary" className="mt-2">
                        {event.type}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {timelineData.reduce((sum, year) => sum + year.publications, 0)}
              </div>
              <div className="text-sm text-muted-foreground">Всего публикаций</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {timelineData.reduce((sum, year) => sum + year.citations, 0)}
              </div>
              <div className="text-sm text-muted-foreground">Всего цитирований</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {Math.round(timelineData.reduce((sum, year) => sum + year.publications, 0) / timelineData.length * 10) / 10}
              </div>
              <div className="text-sm text-muted-foreground">Публикаций в год</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ResearchTimeline;
