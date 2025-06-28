import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { TrendingUp, TrendingDown, Award, Users, BookOpen, Quote } from 'lucide-react';

const MetricsDisplay = ({ data }) => {
  // Default metrics if none provided
  const defaultMetrics = {
    total_publications: 45,
    total_citations: 892,
    h_index: 14,
    i10_index: 23,
    collaboration_score: 78,
    impact_factor_avg: 2.45,
    recent_publications: 12,
    citation_growth: 15.4,
    research_areas: [
      { name: 'Machine Learning', publications: 18, percentage: 40 },
      { name: 'Data Science', publications: 12, percentage: 27 },
      { name: 'AI Ethics', publications: 8, percentage: 18 },
      { name: 'Computer Vision', publications: 7, percentage: 15 }
    ],
    yearly_impact: [
      { year: 2019, impact: 45 },
      { year: 2020, impact: 78 },
      { year: 2021, impact: 123 },
      { year: 2022, impact: 156 },
      { year: 2023, impact: 201 }
    ]
  };

  const metrics = data || defaultMetrics;

  // Colors for pie chart
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
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
      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{metrics.total_publications}</div>
                <div className="text-sm text-muted-foreground">Публикации</div>
                {metrics.recent_publications && (
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-xs text-green-600">+{metrics.recent_publications} недавно</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Quote className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{metrics.total_citations}</div>
                <div className="text-sm text-muted-foreground">Цитирования</div>
                {metrics.citation_growth && (
                  <div className="flex items-center gap-1 mt-1">
                    <TrendingUp className="h-3 w-3 text-green-600" />
                    <span className="text-xs text-green-600">+{metrics.citation_growth}%</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Award className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{metrics.h_index}</div>
                <div className="text-sm text-muted-foreground">H-индекс</div>
                {metrics.i10_index && (
                  <div className="text-xs text-muted-foreground mt-1">
                    i10: {metrics.i10_index}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-lg">
                <Users className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{metrics.collaboration_score}%</div>
                <div className="text-sm text-muted-foreground">Коллаборация</div>
                {metrics.impact_factor_avg && (
                  <div className="text-xs text-muted-foreground mt-1">
                    IF: {metrics.impact_factor_avg}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Research Areas Distribution */}
      {metrics.research_areas && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Области исследований</CardTitle>
              <CardDescription>
                Распределение публикаций по тематикам
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={metrics.research_areas}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name} (${percentage}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="publications"
                    >
                      {metrics.research_areas.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Публикации по областям</CardTitle>
              <CardDescription>
                Количество работ в каждой области
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {metrics.research_areas.map((area, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">{area.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {area.publications} ({area.percentage}%)
                      </span>
                    </div>
                    <Progress value={area.percentage} className="h-2" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Impact Timeline */}
      {metrics.yearly_impact && (
        <Card>
          <CardHeader>
            <CardTitle>Динамика научного влияния</CardTitle>
            <CardDescription>
              Изменение импакт-фактора и цитируемости по годам
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metrics.yearly_impact}>
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
                    dataKey="impact" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                    name="Научное влияние"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Advanced Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Индексы цитирования</CardTitle>
            <CardDescription>
              Ключевые показатели научного влияния
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span>H-индекс</span>
              <Badge variant="default">{metrics.h_index}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>i10-индекс</span>
              <Badge variant="secondary">{metrics.i10_index || 'N/A'}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>Средний IF</span>
              <Badge variant="outline">{metrics.impact_factor_avg || 'N/A'}</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span>Индекс коллаборации</span>
              <div className="flex items-center gap-2">
                <Progress value={metrics.collaboration_score} className="w-20 h-2" />
                <span className="text-sm">{metrics.collaboration_score}%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Тренды роста</CardTitle>
            <CardDescription>
              Динамика развития исследовательской деятельности
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Рост цитирований</span>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-green-600 font-medium">+{metrics.citation_growth || 0}%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>Новые публикации</span>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <span className="text-blue-600 font-medium">+{metrics.recent_publications || 0}</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>Активность коллабораций</span>
              <div className="flex items-center gap-1">
                <TrendingUp className="h-4 w-4 text-purple-600" />
                <span className="text-purple-600 font-medium">Высокая</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MetricsDisplay;
