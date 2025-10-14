import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

export const resources = {
  en: {
    translation: {
      navigation: {
        dashboard: 'Dashboard',
        workspace: 'Workspace',
        analytics: 'Analytics'
      },
      actions: {
        toggleTheme: 'Toggle color mode',
        language: 'Language',
        addObjective: 'Add objective',
        export: 'Export data'
      },
      dashboard: {
        alignmentTitle: 'Alignment board',
        analyticsTitle: 'Key metrics',
        healthTitle: 'Health pulse'
      },
      workspace: {
        heading: 'Workspace alignment',
        dragHint: 'Drag objectives to realign them'
      },
      analytics: {
        velocity: 'Execution velocity',
        completion: 'Objective completion',
        engagement: 'Engagement pulse'
      }
    }
  },
  ru: {
    translation: {
      navigation: {
        dashboard: 'Дашборд',
        workspace: 'Рабочее пространство',
        analytics: 'Аналитика'
      },
      actions: {
        toggleTheme: 'Переключить тему',
        language: 'Язык',
        addObjective: 'Добавить цель',
        export: 'Экспорт данных'
      },
      dashboard: {
        alignmentTitle: 'Доска выравнивания',
        analyticsTitle: 'Ключевые метрики',
        healthTitle: 'Пульс вовлеченности'
      },
      workspace: {
        heading: 'Иерархия OKR',
        dragHint: 'Перетащите цели для изменения выравнивания'
      },
      analytics: {
        velocity: 'Скорость исполнения',
        completion: 'Завершение целей',
        engagement: 'Вовлеченность'
      }
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['querystring', 'localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });

export { i18n };
