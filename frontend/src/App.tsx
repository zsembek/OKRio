import { ChakraProvider, Container, Flex, Heading, Select, SimpleGrid, Stack, Text } from "@chakra-ui/react";
import { useTranslation } from "react-i18next";
import ObjectiveCard from "./components/ObjectiveCard";
import { selectActivePeriod, selectDashboardObjectives } from "./features/dashboard/selectors";
import { setActivePeriod } from "./features/dashboard/dashboardSlice";
import { useAppDispatch, useAppSelector } from "./app/hooks";

const periodOptions = ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"];

export const App = () => {
  const dispatch = useAppDispatch();
  const { t } = useTranslation();
  const activePeriod = useAppSelector(selectActivePeriod);
  const objectives = useAppSelector(selectDashboardObjectives);

  return (
    <ChakraProvider>
      <Container maxW="6xl" py={10}>
        <Stack spacing={6}>
          <Flex justify="space-between" align={"center"}>
            <Heading size="lg">{t("dashboard.title")}</Heading>
            <Flex align="center" gap={3}>
              <Text fontWeight="medium">{t("dashboard.period")}</Text>
              <Select
                value={activePeriod}
                onChange={(event) => dispatch(setActivePeriod(event.target.value))}
                maxW="40"
              >
                {periodOptions.map((period) => (
                  <option key={period} value={period}>
                    {period}
                  </option>
                ))}
              </Select>
            </Flex>
          </Flex>
          <Text color="gray.500">{t("dashboard.subtitle", { count: objectives.length })}</Text>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {objectives.map((objective) => (
              <ObjectiveCard key={objective.id} objective={objective} />
            ))}
          </SimpleGrid>
        </Stack>
      </Container>
    </ChakraProvider>
  );
};

export default App;
