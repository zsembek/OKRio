import {
  DndContext,
  DragEndEvent,
  PointerSensor,
  useDroppable,
  useDraggable,
  useSensor,
  useSensors
} from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { useDispatch, useSelector } from 'react-redux';
import { Box, Card, CardBody, Heading, Progress, Stack, Text } from '@chakra-ui/react';
import { moveObjective } from '../model/alignmentSlice';
import type { Objective } from '../model/types';
import type { RootState } from '../../../shared/config/store';

interface ObjectiveCardProps {
  objective: Objective;
}

const ObjectiveCard = ({ objective }: ObjectiveCardProps) => (
  <Card variant="outline" borderColor="gray.200" _dark={{ borderColor: 'gray.700' }} mb={3}>
    <CardBody>
      <Stack spacing={2}>
        <Heading as="h4" size="sm">
          {objective.title}
        </Heading>
        <Text fontSize="sm" color="gray.500">
          {objective.owner}
        </Text>
        <Progress value={objective.progress} colorScheme="teal" rounded="full" />
      </Stack>
    </CardBody>
  </Card>
);

interface ObjectiveTreeProps {
  objectives: Objective[];
}

const ObjectiveTree = ({ objectives }: ObjectiveTreeProps) => (
  <Stack spacing={4} pl={4} borderLeftWidth="1px" borderColor="gray.200" _dark={{ borderColor: 'gray.700' }}>
    {objectives.map((objective) => (
      <ObjectiveBranch key={objective.id} objective={objective} />
    ))}
  </Stack>
);

const ObjectiveBranch = ({ objective }: ObjectiveCardProps) => {
  const { setNodeRef } = useDroppable({ id: objective.id });
  const { attributes, listeners, setNodeRef: setDragRef, transform, isDragging } = useDraggable({ id: objective.id });

  const style = {
    transform: transform ? CSS.Translate.toString(transform) : undefined,
    cursor: 'grab'
  } as const;

  return (
    <Box ref={setNodeRef} p={2} borderRadius="md" bg={isDragging ? 'teal.50' : 'transparent'} _dark={{ bg: isDragging ? 'teal.900' : 'transparent' }}>
      <Box ref={setDragRef} {...listeners} {...attributes} style={style} opacity={isDragging ? 0.6 : 1}>
        <ObjectiveCard objective={objective} />
      </Box>
      {objective.children && objective.children.length > 0 && <ObjectiveTree objectives={objective.children} />}
    </Box>
  );
};

export const AlignmentBoard = () => {
  const dispatch = useDispatch();
  const objectives = useSelector((state: RootState) => state.alignment.objectives);
  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;
    const targetParentId = over.id === 'root-dropzone' ? null : String(over.id);

    dispatch(moveObjective({ objectiveId: String(active.id), targetParentId }));
  };

  const { setNodeRef } = useDroppable({ id: 'root-dropzone' });

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <Box ref={setNodeRef} borderWidth="1px" borderStyle="dashed" borderColor="gray.300" rounded="md" p={4}>
        <ObjectiveTree objectives={objectives} />
      </Box>
    </DndContext>
  );
};
