import React, { useState, useEffect } from 'react';
import { 
  User, 
  Brain, 
  Network, 
  TrendingUp, 
  Clock, 
  BookOpen, 
  Award,
  Download,
  Refresh,
  Search,
  Users,
  Target,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';
import apiService from '../services/api';

// Sub-components for different visualization types
import ResearchRadarChart from './visualizations/ResearchRadarChart';
import CollaborationNetwork from './visualizations/CollaborationNetwork';
import ResearchTimeline from './visualizations/ResearchTimeline';
import MetricsDisplay from './visualizations/MetricsDisplay';

const DigitalTwin = ({ email }) => {
  const [digitalTwinData, setDigitalTwinData] = useState(null);
  const [visualizationData, setVisualizationData] = useState(null);
  const [academicProfile, setAcademicProfile] = useState(null);
  const [networkAnalysis, setNetworkAnalysis] = useState(null);
  const [researchMetrics, setResearchMetrics] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [creationStage, setCreationStage] = useState('idle'); // idle, academic-search, creating-twin, completed

  // Create digital twin workflow
  const createDigitalTwin = async () => {
    if (!email) return;
    
    setLoading(true);
    setError(null);
    setCreationStage('academic-search');
    
    try {
      // Step 1: Perform academic search
      console.log('Performing academic search for:', email);
      const academicSearchResult = await apiService.performAcademicSearch(email);
      console.log('Academic search completed:', academicSearchResult);
      
      setCreationStage('creating-twin');
      
      // Step 2: Create digital twin
      console.log('Creating digital twin for:', email);
      const digitalTwinResult = await apiService.createDigitalTwin(email);
      console.log('Digital twin created:', digitalTwinResult);
      
      // Set the created data
      if (digitalTwinResult?.data) {
        setDigitalTwinData(digitalTwinResult.data);
        
        // Extract visualization data if available
        if (digitalTwinResult.data.visualization_data) {
          setVisualizationData(digitalTwinResult.data.visualization_data);
        }
        
        // Extract academic profile
        if (digitalTwinResult.data.academic_profile) {
          setAcademicProfile(digitalTwinResult.data.academic_profile);
        }
        
        // Extract network analysis
        if (digitalTwinResult.data.network_analysis) {
          setNetworkAnalysis(digitalTwinResult.data.network_analysis);
        }
        
        // Extract research metrics from impact_metrics
        if (digitalTwinResult.data.impact_metrics) {
          setResearchMetrics({
            total_publications: digitalTwinResult.data.impact_metrics.citation_impact?.publication_count || 0,
            total_citations: digitalTwinResult.data.impact_metrics.citation_impact?.estimated_citations || 0,
            h_index: digitalTwinResult.data.impact_metrics.citation_impact?.h_index_estimate || 0,
            collaboration_score: digitalTwinResult.data.impact_metrics.overall_impact_score || 0
          });
        }
      }
      
      setCreationStage('completed');
      
    } catch (err) {
      console.error('Digital twin creation error:', err);
      setError(`Ошибка при создании цифрового двойника: ${err.message}`);
      setCreationStage('idle');
    } finally {
      setLoading(false);
    }
  };

  // Load existing digital twin data
  const loadDigitalTwinData = async () => {
    if (!email) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Try to load existing digital twin
      const digitalTwin = await apiService.getDigitalTwin(email);
      setDigitalTwinData(digitalTwin.data);
      setCreationStage('completed');
      
      // Load additional data
      const [
        visualization,
        academic,
        network,
        metrics,
        timelineData
      ] = await Promise.allSettled([
        apiService.getVisualization(email),
        apiService.getAcademicProfile(email),
        apiService.getNetworkAnalysis(email),
        apiService.getResearchMetrics(email),
        apiService.getResearchTimeline(email)
      ]);

      // Set data for successful requests
      if (visualization.status === 'fulfilled') {
        setVisualizationData(visualization.value);
      }
      if (academic.status === 'fulfilled') {
        setAcademicProfile(academic.value);
      }
      if (network.status === 'fulfilled') {
        setNetworkAnalysis(network.value);
      }
      if (metrics.status === 'fulfilled') {
        setResearchMetrics(metrics.value);
      }
      if (timelineData.status === 'fulfilled') {
        setTimeline(timelineData.value);
      }

    } catch (err) {
      console.log('No existing digital twin found, will need to create one');
      setCreationStage('idle');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (email) {
      loadDigitalTwinData();
    }
  }, [email]);

  const handleExportProfile = async (format) => {
    try {
      const data = await apiService.exportProfile(email, format);
      
      if (format === 'pdf') {
        // Handle PDF download
        const url = window.URL.createObjectURL(data);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `profile_${email}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        // Handle JSON download
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `profile_${email}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  if (loading) {
    const loadingMessages = {
      'academic-search': 'Выполняется академический поиск...',
      'creating-twin': 'Создается цифровой двойник...',
      'idle': 'Загрузка цифрового двойника...'
    };
    
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span>{loadingMessages[creationStage] || 'Загрузка...'}</span>
          </div>
          {creationStage !== 'idle' && (
            <div className="mt-4">
              <Progress value={creationStage === 'academic-search' ? 30 : creationStage === 'creating-twin' ? 70 : 100} className="h-2" />
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert>
        <AlertDescription>{error}</AlertDescription>
        <div className="mt-4">
          <Button onClick={createDigitalTwin} disabled={loading}>
            Попробовать снова
          </Button>
        </div>
      </Alert>
    );
  }

  // Show creation interface if no digital twin exists
  if (creationStage === 'idle' && !digitalTwinData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Создание цифрового двойника
          </CardTitle>
          <CardDescription>
            Цифровой двойник для {email} еще не создан. Начните процесс создания для комплексного анализа исследовательского профиля.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center space-y-4">
            <p className="text-muted-foreground">
              Процесс создания включает:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Search className="h-4 w-4 text-blue-500" />
                <span>Академический поиск</span>
              </div>
              <div className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-purple-500" />
                <span>Анализ профиля</span>
              </div>
              <div className="flex items-center gap-2">
                <Network className="h-4 w-4 text-green-500" />
                <span>Сетевой анализ</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-orange-500" />
                <span>Метрики воздействия</span>
              </div>
            </div>
            <Button onClick={createDigitalTwin} disabled={loading} className="mt-6">
              <Brain className="h-4 w-4 mr-2" />
              Создать цифрового двойника
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Profile Summary */}
      {digitalTwinData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Профиль исследователя
            </CardTitle>
            <CardDescription>
              Основная информация и ключевые характеристики
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{email}</p>
              </div>
              {digitalTwinData.name && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Имя</p>
                  <p className="font-medium">{digitalTwinData.name}</p>
                </div>
              )}
              {digitalTwinData.affiliation && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Организация</p>
                  <p className="font-medium">{digitalTwinData.affiliation}</p>
                </div>
              )}
              {digitalTwinData.research_interests && (
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Область исследований</p>
                  <div className="flex flex-wrap gap-1">
                    {digitalTwinData.research_interests.slice(0, 3).map((interest, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {interest}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      {researchMetrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Ключевые метрики
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {researchMetrics.total_publications || 0}
                </div>
                <div className="text-sm text-muted-foreground">Публикации</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {researchMetrics.total_citations || 0}
                </div>
                <div className="text-sm text-muted-foreground">Цитирования</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {researchMetrics.h_index || 0}
                </div>
                <div className="text-sm text-muted-foreground">H-индекс</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {researchMetrics.collaboration_score || 0}%
                </div>
                <div className="text-sm text-muted-foreground">Коллаборация</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Research Impact */}
      {visualizationData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Исследовательский профиль
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResearchRadarChart data={visualizationData.radar_data} />
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderNetwork = () => (
    <div className="space-y-6">
      {networkAnalysis && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network className="h-5 w-5" />
                Сеть сотрудничества
              </CardTitle>
              <CardDescription>
                Визуализация исследовательских связей и коллабораций
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CollaborationNetwork data={networkAnalysis} />
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Ключевые соавторы
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {networkAnalysis.top_collaborators?.map((collaborator, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{collaborator.name}</p>
                        <p className="text-sm text-muted-foreground">{collaborator.affiliation}</p>
                      </div>
                      <Badge variant="outline">
                        {collaborator.collaboration_count} публикаций
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Центральность в сети
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Betweenness Centrality</span>
                      <span>{networkAnalysis.centrality_metrics?.betweenness?.toFixed(3) || 'N/A'}</span>
                    </div>
                    <Progress value={(networkAnalysis.centrality_metrics?.betweenness || 0) * 100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Closeness Centrality</span>
                      <span>{networkAnalysis.centrality_metrics?.closeness?.toFixed(3) || 'N/A'}</span>
                    </div>
                    <Progress value={(networkAnalysis.centrality_metrics?.closeness || 0) * 100} className="h-2" />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Degree Centrality</span>
                      <span>{networkAnalysis.centrality_metrics?.degree?.toFixed(3) || 'N/A'}</span>
                    </div>
                    <Progress value={(networkAnalysis.centrality_metrics?.degree || 0) * 100} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );

  const renderTimeline = () => (
    <div className="space-y-6">
      {timeline && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Временная линия исследований
            </CardTitle>
            <CardDescription>
              Хронология публикаций и исследовательской активности
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResearchTimeline data={timeline} />
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderMetrics = () => (
    <div className="space-y-6">
      {researchMetrics && (
        <MetricsDisplay data={researchMetrics} />
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Цифровой двойник</h2>
          <p className="text-muted-foreground">
            Комплексный анализ исследовательского профиля для {email}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={createDigitalTwin}>
            <Refresh className="h-4 w-4 mr-2" />
            Пересоздать
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExportProfile('json')}>
            <Download className="h-4 w-4 mr-2" />
            JSON
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExportProfile('pdf')}>
            <Download className="h-4 w-4 mr-2" />
            PDF
          </Button>
        </div>
      </div>

      {/* Main content tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Обзор
          </TabsTrigger>
          <TabsTrigger value="network" className="flex items-center gap-2">
            <Network className="h-4 w-4" />
            Сеть
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Временная линия
          </TabsTrigger>
          <TabsTrigger value="metrics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Метрики
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">{renderOverview()}</TabsContent>
        <TabsContent value="network">{renderNetwork()}</TabsContent>
        <TabsContent value="timeline">{renderTimeline()}</TabsContent>
        <TabsContent value="metrics">{renderMetrics()}</TabsContent>
      </Tabs>
    </div>
  );
};

export default DigitalTwin;
