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

