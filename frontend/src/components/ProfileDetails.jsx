import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { User, Mail, Phone, MapPin, Building, Link, Calendar, TrendingUp } from 'lucide-react';

const ProfileDetails = ({ data }) => {
  if (!data || !data.data) return null;

  const profile = data.data;
  const source = data.source;

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
                    <span className="text-sm">{social.username || 'Профиль найден'}</span>
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
              <Link className="h-4 w-4" />
              Веб-сайты
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {profile.websites.map((website, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm">{website}</span>
                  <a 
                    href={website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline text-sm"
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
              {profile.sources.map((source, index) => (
                <Badge key={index} variant="secondary">{source}</Badge>
              ))}
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
