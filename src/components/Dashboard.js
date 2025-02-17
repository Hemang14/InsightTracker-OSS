import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Grid, TextField, Paper, Typography, useTheme, CircularProgress } from '@mui/material';
import ProjectCard from './ProjectCard';

const API_URL = "https://api.github.com/orgs/apache/repos?per_page=25";

const Dashboard = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const theme = useTheme();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch(API_URL);
        const data = await response.json();
        // Process API data into the format needed
        const formattedProjects = data.map((repo) => ({
          id: repo.id,
          name: repo.name,
          organization: repo.owner?.login || "Unknown",
          description: repo.description || "No description available",
          status: repo.archived ? "Archived" : "Active",
          last_updated: new Date(repo.updated_at).toLocaleDateString()
        }));
        setProjects(formattedProjects);
      } catch (error) {
        console.error("Error fetching projects:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    project.organization.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Paper style={{
      padding: 16,
      backgroundColor: 'transparent',
      color: theme.palette.text.primary
    }}>
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', fontWeight: 'bold' }}>
        InsightTracker OSS
      </Typography>
      <TextField 
        fullWidth
        label="Search Projects" 
        variant="outlined" 
        value={searchTerm} 
        onChange={(e) => setSearchTerm(e.target.value)} 
        style={{ marginBottom: 16 }}
      />
      
      {loading ? (
        <Typography sx={{ textAlign: 'center' }}>
          <CircularProgress />
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {filteredProjects.length > 0 ? (
            filteredProjects.map(project => (
              <Grid item xs={12} sm={6} md={4} key={project.id}>
                <ProjectCard project={project} onClick={() => navigate(`/project/${project.id}`, { state: { project } })} />
              </Grid>
            ))
          ) : (
            <Typography sx={{ textAlign: 'center', width: '100%' }}>No projects found.</Typography>
          )}
        </Grid>
      )}
    </Paper>
  );
};

export default Dashboard;
