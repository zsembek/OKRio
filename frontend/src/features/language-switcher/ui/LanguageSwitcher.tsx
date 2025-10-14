import { Menu, MenuButton, MenuItem, MenuList, Button } from '@chakra-ui/react';
import { useTranslation } from 'react-i18next';

const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'ru', label: 'Русский' }
];

export const LanguageSwitcher = () => {
  const { i18n, t } = useTranslation();

  const handleChange = (code: string) => {
    i18n.changeLanguage(code);
  };

  return (
    <Menu>
      <MenuButton as={Button} variant="ghost" size="sm">
        {t('actions.language')}
      </MenuButton>
      <MenuList>
        {SUPPORTED_LANGUAGES.map((lang) => (
          <MenuItem key={lang.code} onClick={() => handleChange(lang.code)}>
            {lang.label}
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  );
};
