import React, { useState, useEffect, useRef } from 'react';
import { Search, Clock } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import apiService from '../services/api';

const SearchWithSuggestions = ({ onSearch, placeholder = "example@domain.com" }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const inputRef = useRef();
  const suggestionsRef = useRef();

  // Load recent searches from localStorage
  useEffect(() => {
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    setRecentSearches(recent.slice(0, 5)); // Keep only last 5
  }, []);

  // Fetch suggestions when query changes
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length < 2) {
        setSuggestions([]);
        return;
      }

      setIsLoading(true);
      try {
        const response = await apiService.getSearchSuggestions(query);
        setSuggestions(response.suggestions || []);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    const timeoutId = setTimeout(fetchSuggestions, 300); // Debounce
    return () => clearTimeout(timeoutId);
  }, [query]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e, email = query) => {
    e.preventDefault();
    if (!email) return;

    // Save to recent searches
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    const updated = [email, ...recent.filter(item => item !== email)].slice(0, 5);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
    setRecentSearches(updated);

    // Close suggestions and call onSearch
    setShowSuggestions(false);
    onSearch(email);
  };

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    const fakeEvent = { preventDefault: () => {} };
    handleSubmit(fakeEvent, suggestion);
  };

  return (
    <div className="relative w-full">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="relative flex-1">
          <Input
            ref={inputRef}
            type="email"
            placeholder={placeholder}
            value={query}
            onChange={handleInputChange}
            onFocus={() => setShowSuggestions(true)}
            className="pr-10"
            autoComplete="off"
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        </div>
        <Button type="submit" disabled={!query}>
          Поиск
        </Button>
      </form>

      {/* Suggestions dropdown */}
      {showSuggestions && (query.length >= 2 || recentSearches.length > 0) && (
        <Card ref={suggestionsRef} className="absolute top-full left-0 right-0 z-50 mt-1">
          <CardContent className="p-2 max-h-60 overflow-y-auto">
            {/* Loading state */}
            {isLoading && (
              <div className="p-2 text-sm text-muted-foreground text-center">
                Поиск предложений...
              </div>
            )}

            {/* Suggestions from API */}
            {!isLoading && suggestions.length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground px-2 py-1 border-b">
                  Предложения
                </div>
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="px-2 py-2 rounded hover:bg-accent cursor-pointer flex items-center gap-2"
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    <Search className="h-3 w-3 text-muted-foreground" />
                    <span className="text-sm">{suggestion}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Recent searches */}
            {recentSearches.length > 0 && (query.length < 2 || suggestions.length === 0) && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground px-2 py-1 border-b flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  Недавние поиски
                </div>
                {recentSearches.map((recent, index) => (
                  <div
                    key={index}
                    className="px-2 py-2 rounded hover:bg-accent cursor-pointer flex items-center gap-2"
                    onClick={() => handleSuggestionClick(recent)}
                  >
                    <Clock className="h-3 w-3 text-muted-foreground" />
                    <span className="text-sm">{recent}</span>
                    <Badge variant="secondary" className="ml-auto text-xs">
                      Недавно
                    </Badge>
                  </div>
                ))}
              </div>
            )}

            {/* No suggestions */}
            {!isLoading && query.length >= 2 && suggestions.length === 0 && recentSearches.length === 0 && (
              <div className="p-2 text-sm text-muted-foreground text-center">
                Нет предложений
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SearchWithSuggestions;
