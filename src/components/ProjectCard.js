import React from 'react';
import { Card, CardActionArea, CardContent, Typography, Box, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const getStatusColor = (status) => {
  switch (status) {
    case 'Active': return '#4CAF50';
    case 'Archived': return '#F44336';
    default: return '#9E9E9E';
  }
};

const ProjectCard = ({ project }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/project/${project.id}`, { state: { project } });
  };

  return (
    <Card 
      onClick={handleClick} 
      raised 
      sx={{ 
        backgroundColor: '#37474F', 
        borderRadius: '16px', 
        '&:hover': { transform: "scale(1.05)", transition: "transform 0.3s" },
        color: '#fff',
        textAlign: 'center',
        padding: 2
      }}
    >
      <CardActionArea>
        <CardContent>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            {project.name}
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'center', marginTop: 1 }}>
            <Chip 
              label={project.status} 
              sx={{
                backgroundColor: getStatusColor(project.status),
                color: '#fff',
                fontWeight: 'bold',
                fontSize: '0.8rem'
              }}
            />
          </Box>

          <Typography variant="body2" sx={{ marginTop: 1, fontSize: '1rem', color: '#E0E0E0' }}>
            {project.organization}
          </Typography>

          <Typography variant="body2" sx={{ marginTop: 1, fontSize: '0.9rem', color: '#B0BEC5' }}>
            {project.description.length > 80 ? `${project.description.substring(0, 80)}...` : project.description}
          </Typography>

          <Typography variant="caption" sx={{ display: 'block', marginTop: 1, color: '#B0BEC5' }}>
            Last Updated: {project.last_updated}
          </Typography>

        </CardContent>
      </CardActionArea>
    </Card>
  );
};

export default ProjectCard;
