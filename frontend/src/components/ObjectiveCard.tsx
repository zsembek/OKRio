import { Box, Flex, Progress, Text, useColorModeValue } from "@chakra-ui/react";
import type { ObjectiveSummary } from "../features/dashboard/dashboardSlice";

const statusColor: Record<ObjectiveSummary["status"], string> = {
  on_track: "green",
  at_risk: "orange",
  off_track: "red"
};

const statusCopy: Record<ObjectiveSummary["status"], string> = {
  on_track: "On Track",
  at_risk: "At Risk",
  off_track: "Off Track"
};

export const ObjectiveCard = ({ objective }: { objective: ObjectiveSummary }) => (
  <Box
    borderWidth="1px"
    borderRadius="md"
    p={4}
    bg={useColorModeValue("white", "gray.800")}
    shadow="sm"
  >
    <Flex justify="space-between" align="center" mb={3}>
      <Text fontWeight="semibold">{objective.name}</Text>
      <Text color={`${statusColor[objective.status]}.400`} fontWeight="medium">
        {statusCopy[objective.status]}
      </Text>
    </Flex>
    <Progress value={objective.progress * 100} colorScheme={statusColor[objective.status]} borderRadius="md" mb={2} />
    <Text fontSize="sm" color="gray.500">
      {Math.round(objective.progress * 100)}% complete
    </Text>
  </Box>
);

export default ObjectiveCard;
