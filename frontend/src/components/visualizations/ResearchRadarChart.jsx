import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

const ResearchRadarChart = ({ data }) => {
  // Default data structure if no data provided
  const defaultData = [
    { subject: 'Продуктивность', A: 120, fullMark: 150 },
    { subject: 'Влияние', A: 98, fullMark: 150 },
    { subject: 'Сотрудничество', A: 86, fullMark: 150 },
    { subject: 'Инновации', A: 99, fullMark: 150 },
    { subject: 'Качество', A: 85, fullMark: 150 },
    { subject: 'Актуальность', A: 65, fullMark: 150 }
  ];

  const chartData = data && data.length > 0 ? data : defaultData;

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={chartData}>
          <PolarGrid gridType="polygon" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fontSize: 12, fill: '#666' }}
            className="text-sm"
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 150]} 
            tick={{ fontSize: 10, fill: '#999' }}
            tickCount={4}
          />
          <Radar
            name="Исследовательский профиль"
            dataKey="A"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.2}
            strokeWidth={2}
            dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ResearchRadarChart;
