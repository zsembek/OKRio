import { Box, Heading, Stack, Text } from '@chakra-ui/react';
import { AlignmentBoard } from '../../features/alignment-board';
import { useTranslation } from 'react-i18next';

const WorkspacePage = () => {
  const { t } = useTranslation();

  return (
    <Stack spacing={6}>
      <Box>
        <Heading size="md">{t('workspace.heading')}</Heading>
        <Text color="gray.500">{t('workspace.dragHint')}</Text>
      </Box>
      <AlignmentBoard />
    </Stack>
  );
};

export default WorkspacePage;
